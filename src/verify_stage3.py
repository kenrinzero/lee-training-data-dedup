#!/usr/bin/env python3
import argparse
import csv
import hashlib
import io
import json
import tarfile
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

import duckdb

from stage3_audit import (
    ceiling_from_histogram,
    create_url_stats,
    ensure_fresh_audit,
    figure_counts,
    ingest_archive,
)
from stage3_compare import (
    ceiling_verdict,
    conditional_table13,
    ensure_fresh_comparison,
    grade_figures,
    grade_url_value,
    nonexecutable_table2,
    printed_rounding_companion,
)
from stage3_report import ensure_fresh_report, render_report
from verify_stage3_report import check_output_hashes


def make_archive(directory, csv_bytes, extra_member=False, member_name="realnews.csv"):
    path = Path(directory) / "realnews.tar.gz"
    with tarfile.open(path, "w:gz") as tar:
        member = tarfile.TarInfo(member_name)
        member.size = len(csv_bytes)
        tar.addfile(member, io.BytesIO(csv_bytes))
        if extra_member:
            extra = tarfile.TarInfo("extra.txt")
            extra.size = 1
            tar.addfile(extra, io.BytesIO(b"x"))
    return path


class AuditContractTests(unittest.TestCase):
    def test_ceiling_from_histogram(self):
        self.assertEqual(
            ceiling_from_histogram({1: 3, 2: 4, 5: 2}),
            {"multi_documents": 18, "multi_clusters": 6, "removals": 12},
        )
        self.assertEqual(
            ceiling_from_histogram({1: 5}),
            {"multi_documents": 0, "multi_clusters": 0, "removals": 0},
        )

    def test_realnews_ranking_includes_mixed_and_keep1_only_urls(self):
        rows = [
            {"url": "z", "total": 12, "keep0": 6, "multi_membership": 6},
            {"url": "b", "total": 10, "keep0": 10, "multi_membership": 10},
            {"url": "a", "total": 10, "keep0": 10, "multi_membership": 10},
            {"url": "below", "total": 9, "keep0": 9, "multi_membership": 9},
            {"url": "mixed", "total": 20, "keep0": 10, "multi_membership": 10},
            {"url": "keep1", "total": 15, "keep0": 0, "multi_membership": 0},
        ]
        from stage3_audit import rank_urls

        ranked = rank_urls(rows)
        self.assertEqual([row["url"] for row in ranked], ["a", "b", "mixed", "z", "keep1"])
        self.assertEqual(len(rank_urls(rows, limit=4)), 4)

    def test_url_stats_preserves_keep1_only_and_duplicate_ids(self):
        con = duckdb.connect(":memory:")
        con.execute("CREATE TABLE released (row_id BIGINT, id VARCHAR, keep INTEGER, cluster BIGINT)")
        con.execute("CREATE TABLE clusters (cluster BIGINT, n_all BIGINT, keep0 BIGINT, keep1 BIGINT)")
        con.executemany(
            "INSERT INTO released VALUES (?, ?, ?, ?)",
            [(1, "keep1-only", 1, 1), (2, "keep1-only", 1, 2), (3, "mixed", 0, 3), (4, "mixed", 1, 3)],
        )
        con.executemany(
            "INSERT INTO clusters VALUES (?, ?, ?, ?)",
            [(1, 1, 0, 1), (2, 1, 0, 1), (3, 2, 1, 1)],
        )
        create_url_stats(con)
        rows = {row[0]: row[1:] for row in con.execute("SELECT url, total, keep0, multi_membership FROM url_stats").fetchall()}
        self.assertEqual(rows["keep1-only"], (2, 0, 0))
        self.assertEqual(rows["mixed"], (2, 1, 2))
        self.assertEqual(con.execute("SELECT COUNT(*) FROM url_stats WHERE total > 1").fetchone()[0], 2)
        con.close()

    def test_all_edge_conventions(self):
        histogram = {1: 100, 2: 10, 6: 1, 10: 2, 11: 4, 20: 3, 5000: 5, 5001: 7}
        self.assertEqual(figure_counts(histogram, "dropped"), [100, 10, 0, 0, 0, 1, 4, 0, 0, 0, 7])
        self.assertEqual(figure_counts(histogram, "low"), [100, 10, 0, 0, 0, 3, 7, 0, 0, 5, 7])
        self.assertEqual(figure_counts(histogram, "high"), [100, 10, 0, 0, 0, 1, 6, 3, 0, 0, 12])

    def test_ingest_archive_streams_exact_rows(self):
        payload = b"id,keep,cluster\na,1,0\nb,0,1\nc,0,1\n"
        with tempfile.TemporaryDirectory() as directory:
            archive = make_archive(directory, payload)
            con = duckdb.connect(":memory:")
            con.execute("CREATE TABLE released (row_id BIGINT, id VARCHAR, keep INTEGER, cluster BIGINT)")
            info = ingest_archive(archive, con, expected_member_size=len(payload))
            self.assertEqual(info["physical_rows"], 3)
            self.assertEqual(info["decompressed_bytes"], len(payload))
            self.assertEqual(con.execute("SELECT COUNT(*), SUM(keep = 0) FROM released").fetchone(), (3, 2))
            con.close()

    def test_ingest_archive_rejects_extra_member_and_bad_schema(self):
        payload = b"id,keep,cluster\na,1,0\n"
        with tempfile.TemporaryDirectory() as directory:
            archive = make_archive(directory, payload, extra_member=True)
            con = duckdb.connect(":memory:")
            con.execute("CREATE TABLE released (row_id BIGINT, id VARCHAR, keep INTEGER, cluster BIGINT)")
            with self.assertRaises(ValueError):
                ingest_archive(archive, con, expected_member_size=len(payload))
            con.close()
        with tempfile.TemporaryDirectory() as directory:
            archive = make_archive(directory, b"id,deleted,cluster\na,1,0\n")
            con = duckdb.connect(":memory:")
            con.execute("CREATE TABLE released (row_id BIGINT, id VARCHAR, keep INTEGER, cluster BIGINT)")
            with self.assertRaises(ValueError):
                ingest_archive(archive, con, expected_member_size=len(b"id,deleted,cluster\na,1,0\n"))
            con.close()

    def test_audit_outputs_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory)
            ensure_fresh_audit(out_dir)
            (out_dir / "derived-summary.json").write_text("existing", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                ensure_fresh_audit(out_dir)


class ComparisonContractTests(unittest.TestCase):
    def test_ceiling_threshold_is_exact(self):
        self.assertEqual(ceiling_verdict(2760000), "CONTRADICTION")
        self.assertEqual(ceiling_verdict(2760001), "CEILING_COMPATIBLE")

    def test_split_cells_and_tokens_remain_nonexecutable(self):
        targets = {
            "table2-realnews-train-train": "13.63",
            "table2-realnews-valid-valid": "1.25",
            "table2-realnews-valid-train": "14.35",
        }
        rows = nonexecutable_table2(targets)
        self.assertEqual([row["metric"] for row in rows], ["TT", "EE", "ET"])
        self.assertTrue(all(row["verdict"] == "NOT_EXECUTABLE_INPUT" for row in rows))
        self.assertTrue(all(row["derived_numerator"] == "" for row in rows))
        companion = printed_rounding_companion()
        self.assertEqual(companion["section5_rounding"]["verdict"], "MATCH")
        self.assertEqual(companion["section5_rounding"]["printed_table2"], "14.35%")
        self.assertEqual(companion["section5_rounding"]["printed_section5_3"], "14.4%")
        self.assertEqual(companion["tokens"]["original"], "NOT_EXECUTABLE_INPUT")
        self.assertEqual(companion["tokens"]["neardup"], "NOT_EXECUTABLE_INPUT")

    def test_conditional_table13_labels_release_population(self):
        row = conditional_table13(31160000, 2770000, "31.16", "28.39")
        self.assertEqual(row["basis"], "CONDITIONAL_RELEASE_POPULATION")
        self.assertEqual(row["derived_original_rounded"], "31.16")
        self.assertEqual(row["derived_retained_rounded"], "28.39")
        self.assertEqual(row["original_verdict"], "MATCH")
        self.assertEqual(row["neardup_verdict"], "MATCH")
        self.assertEqual(row["direct_train_removal_verdict"], "NOT_EXECUTABLE_INPUT")

    def test_url_zero_lookup_differs_from_zero_numerator(self):
        missing = grade_url_value("example.com", "12", "0.94", None)
        self.assertEqual(missing["derived_total"], 0)
        self.assertEqual(missing["total_verdict"], "MISMATCH")
        self.assertEqual(missing["frac_verdict"], "NOT_EXECUTABLE_INPUT")
        present = grade_url_value("example.com", "12", "0.00", (12, 0, 0))
        self.assertEqual(present["derived_total"], 12)
        self.assertEqual(present["derived_frac_keep0"], "0")
        self.assertEqual(present["frac_verdict"], "MATCH")

    def test_url_ratio_uses_displayed_precision(self):
        row = grade_url_value("q.usatoday.com", "33", "0.94", (33, 31, 33))
        self.assertEqual(row["total_verdict"], "MATCH")
        self.assertEqual(row["frac_verdict"], "MATCH")
        self.assertEqual(row["derived_membership_frac"], "1")

    def test_figure_verdicts_cover_all_conventions(self):
        histogram = {1: 100, 2: 10, 6: 1, 10: 2, 11: 4, 20: 3, 5000: 5, 5001: 7}
        printed = [100, 10, 0, 0, 0, 1, 4, 0, 0, 0, 7]
        targets = {f"fig8-realnews-bin-{index:02d}": str(value) for index, value in enumerate(printed, start=1)}
        figure_rows = []
        for convention in ("dropped", "low", "high"):
            for bin_index, count in enumerate(figure_counts(histogram, convention), start=1):
                figure_rows.append({"convention": convention, "bin_index": bin_index, "cluster_count": count})
        verdicts = grade_figures(figure_rows, targets)
        matches = {
            convention: sum(row["verdict"] == "MATCH" for row in verdicts if row["convention"] == convention)
            for convention in ("dropped", "low", "high")
        }
        self.assertEqual(len(verdicts), 33)
        self.assertEqual(matches, {"dropped": 11, "low": 8, "high": 8})

    def test_comparison_outputs_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory)
            ensure_fresh_comparison(out_dir)
            (out_dir / "table2-verdicts.csv").write_text("existing", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                ensure_fresh_comparison(out_dir)


class IndependentVerificationTests(unittest.TestCase):
    def test_cluster_size_mutation_is_rejected(self):
        con = duckdb.connect(":memory:")
        con.execute("CREATE TABLE released (row_id BIGINT, id VARCHAR, keep INTEGER, cluster BIGINT)")
        con.execute("CREATE TABLE clusters (cluster BIGINT, n_all BIGINT, keep0 BIGINT, keep1 BIGINT)")
        con.executemany("INSERT INTO released VALUES (?, ?, ?, ?)", [(1, "a", 0, 1), (2, "b", 0, 1), (3, "c", 1, 2)])
        con.executemany("INSERT INTO clusters VALUES (?, ?, ?, ?)", [(1, 2, 2, 0), (2, 1, 0, 1)])
        self.assertEqual(assert_cluster_aggregates(con), {1: 1, 2: 1})
        con.execute("UPDATE clusters SET n_all = 1 WHERE cluster = 1")
        with self.assertRaises(AssertionError):
            assert_cluster_aggregates(con)
        con.close()

    def test_keep1_only_url_omission_is_rejected(self):
        con = duckdb.connect(":memory:")
        con.execute("CREATE TABLE released (row_id BIGINT, id VARCHAR, keep INTEGER, cluster BIGINT)")
        con.execute("CREATE TABLE clusters (cluster BIGINT, n_all BIGINT, keep0 BIGINT, keep1 BIGINT)")
        con.execute("CREATE TABLE url_stats (url VARCHAR, total BIGINT, keep0 BIGINT, multi_membership BIGINT)")
        con.executemany("INSERT INTO released VALUES (?, ?, ?, ?)", [(1, "keep1-only", 1, 1), (2, "keep1-only", 1, 2)])
        con.executemany("INSERT INTO clusters VALUES (?, ?, ?, ?)", [(1, 1, 0, 1), (2, 1, 0, 1)])
        con.execute("INSERT INTO url_stats VALUES ('keep1-only', 2, 0, 0)")
        self.assertEqual(assert_url_coverage(con), 1)
        con.execute("DELETE FROM url_stats")
        with self.assertRaises(AssertionError):
            assert_url_coverage(con)
        con.close()


class ReportContractTests(unittest.TestCase):
    def test_report_outputs_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory)
            ensure_fresh_report(out_dir)
            (out_dir / "report.md").write_text("existing", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                ensure_fresh_report(out_dir)

    def test_output_hash_mutation_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            output = run_dir / "report.md"
            output.write_text("original\n", encoding="utf-8")
            manifest = {
                "outputs": {
                    "report.md": {
                        "bytes": output.stat().st_size,
                        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                    }
                }
            }
            check_output_hashes(run_dir, manifest)
            output.write_text("changed\n", encoding="utf-8")
            with self.assertRaises(AssertionError):
                check_output_hashes(run_dir, manifest)

    def test_rendered_report_preserves_scientific_limits(self):
        from stage1_audit import write_csv, write_json

        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory) / "run-001" / "audit"
            out_dir.mkdir(parents=True)
            write_json(out_dir / "input-manifest.json", {
                "inputs": [{"bytes": 1428191066, "sha256": "abc123"}],
                "archive": {"member": "realnews.csv", "decompressed_bytes": 3432651696, "header": ["id", "keep", "cluster"]},
                "scratch_bytes": 123456,
                "elapsed_seconds": 12.5,
            })
            write_json(out_dir / "derived-summary.json", {
                "physical_rows": 31160000,
                "unique_ids": 31000000,
                "unique_clusters": 28390000,
                "duplicate_released_ids": 2,
                "duplicate_released_rows": 3,
                "singleton_documents": 25390000,
                "multi_documents": 5770000,
                "multi_clusters": 3000000,
                "removals": 2770000,
                "malformed_rows": 0,
                "empty_field_rows": 0,
                "keep_agreement": {"keep0_multi": 5000000, "keep0_singleton": 0, "keep1_multi": 770000, "keep1_singleton": 25390000},
                "keep_discrepancy_rows": 0,
                "url_divergence_count": 1,
                "divergence_status": "KEEP_MEMBERSHIP_DIVERGENCE",
                "table11_eligible_ids": 5,
            })
            write_json(out_dir / "removal-ceiling.json", {
                "physical_rows": 31160000,
                "multi_documents": 5770000,
                "multi_clusters": 3000000,
                "removals": 2770000,
                "retained_release_population": 28390000,
                "formula": "U=D_multi-C_multi",
            })
            targets = {
                "table2-realnews-train-train": "13.63",
                "table2-realnews-valid-valid": "1.25",
                "table2-realnews-valid-train": "14.35",
            }
            table2 = nonexecutable_table2(targets)
            write_csv(out_dir / "table2-verdicts.csv", tuple(table2[0]), table2)
            table13 = conditional_table13(31160000, 2770000, "31.16", "28.39")
            write_csv(out_dir / "table13-verdicts.csv", tuple(table13), [table13])
            companion = printed_rounding_companion()
            companion["split_free_ceiling"] = {
                "derived_removals": 2770000,
                "verdict": "CEILING_COMPATIBLE",
                "basis": "split-free keep-one ceiling; not a train-size match",
            }
            companion["table13_conditional_basis"] = "measured release rows, not a verified public train size"
            write_json(out_dir / "companion-verdicts.json", companion)
            figure = [{
                "convention": "dropped", "bin_index": 1, "bin_label": "1",
                "target_id": "fig8-realnews-bin-01", "printed_count": 27917044,
                "derived_count": 27917044, "verdict": "MATCH",
            }]
            write_csv(out_dir / "figure-verdicts.csv", tuple(figure[0]), figure)
            write_csv(out_dir / "edge-sizes.csv", ("cluster_size", "cluster_count", "document_count"), [{"cluster_size": 10, "cluster_count": 0, "document_count": 0}])
            url = grade_url_value("example.com", "12", "0.50", (12, 6, 6))
            write_csv(out_dir / "table11-verdicts.csv", ("row", *url.keys()), [{"row": 1, **url}])
            write_csv(out_dir / "table11-top20.csv", ("rank", "url", "total", "keep0", "frac_dups", "multi_membership", "membership_fraction"), [{"rank": 1, "url": "example.com", "total": 12, "keep0": 6, "frac_dups": "0.5", "multi_membership": 6, "membership_fraction": "0.5"}])
            write_json(out_dir / "convention-application.json", {"primary": "dropped", "realnews_figure_match_counts": {"dropped": 1, "low": 0, "high": 0}})
            write_json(out_dir / "comparison-summary.json", {"ceiling_verdict": "CEILING_COMPATIBLE"})
            root = Path(__file__).resolve().parents[1]
            report_path = render_report(root, out_dir)
            report = report_path.read_text(encoding="utf-8")
            for expected in (
                "NOT_EXECUTABLE_INPUT",
                "CONDITIONAL_RELEASE_POPULATION",
                "CEILING_COMPATIBLE",
                "keep=0 / # Total",
                "total >= 10",
                "not a verified public train",
                "KEEP_MEMBERSHIP_DIVERGENCE",
            ):
                self.assertIn(expected, report)
            self.assertNotIn(str(root.resolve()), report)
            self.assertTrue((out_dir / "run-manifest.json").is_file())


def read_csv(path):
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def assert_cluster_aggregates(con):
    direct_sql = "SELECT cluster, COUNT(*) AS n_all FROM released GROUP BY cluster"
    mismatches = con.execute(f"""
        WITH direct AS ({direct_sql})
        SELECT
            (SELECT COUNT(*) FROM direct d LEFT JOIN clusters c ON d.cluster = c.cluster
             WHERE c.cluster IS NULL OR c.n_all <> d.n_all),
            (SELECT COUNT(*) FROM clusters c LEFT JOIN direct d ON c.cluster = d.cluster
             WHERE d.cluster IS NULL)
    """).fetchone()
    assert mismatches == (0, 0), f"cluster aggregate mismatch: {mismatches}"
    rows = con.execute(f"WITH direct AS ({direct_sql}) SELECT n_all, COUNT(*) FROM direct GROUP BY n_all").fetchall()
    return {int(size): int(count) for size, count in rows}


def assert_url_coverage(con):
    distinct_ids = con.execute("SELECT COUNT(DISTINCT id) FROM released").fetchone()[0]
    assert con.execute("SELECT COUNT(*) FROM url_stats").fetchone()[0] == distinct_ids
    mismatches = con.execute("""
        WITH direct_clusters AS (
            SELECT cluster, COUNT(*) AS n_all FROM released GROUP BY cluster
        ), expected AS (
            SELECT r.id AS url, COUNT(*) AS total,
                   SUM(r.keep = 0) AS keep0,
                   SUM(dc.n_all >= 2) AS multi_membership
            FROM released r JOIN direct_clusters dc ON r.cluster = dc.cluster
            GROUP BY r.id
        )
        SELECT
            (SELECT COUNT(*) FROM expected e LEFT JOIN url_stats u ON e.url = u.url
             WHERE u.url IS NULL OR u.total <> e.total OR u.keep0 <> e.keep0
                OR u.multi_membership <> e.multi_membership),
            (SELECT COUNT(*) FROM url_stats u LEFT JOIN expected e ON u.url = e.url
             WHERE e.url IS NULL)
    """).fetchone()
    assert mismatches == (0, 0), f"URL aggregate coverage mismatch: {mismatches}"
    return distinct_ids


def independent_figure_counts(histogram, convention):
    if convention not in {"dropped", "low", "high"}:
        raise ValueError(convention)
    ranges = (
        (6, 9, 10, 6, 9),
        (11, 19, 20, 10, 19),
        (21, 49, 50, 20, 49),
        (51, 499, 500, 50, 499),
        (501, 4999, 5000, 500, 4999),
    )
    counts = [histogram.get(size, 0) for size in range(1, 6)]
    for dropped_low, dropped_high, low_high, high_low, high_high in ranges:
        low, high = {
            "dropped": (dropped_low, dropped_high),
            "low": (dropped_low, low_high),
            "high": (high_low, high_high),
        }[convention]
        counts.append(sum(count for size, count in histogram.items() if low <= size <= high))
    minimum = 5000 if convention == "high" else 5001
    counts.append(sum(count for size, count in histogram.items() if size >= minimum))
    return counts


def independent_rank_urls(rows, limit=20):
    from fractions import Fraction

    eligible = [dict(row) for row in rows if int(row["total"]) >= 10]
    eligible.sort(key=lambda row: row["url"].encode("utf-8"))
    eligible.sort(key=lambda row: int(row["total"]), reverse=True)
    eligible.sort(key=lambda row: Fraction(int(row["keep0"]), int(row["total"])), reverse=True)
    ranked = []
    for rank, row in enumerate(eligible[:limit], start=1):
        total = int(row["total"])
        row["rank"] = rank
        row["frac_dups"] = str(Decimal(int(row["keep0"])) / Decimal(total))
        row["membership_fraction"] = str(Decimal(int(row["multi_membership"])) / Decimal(total))
        ranked.append(row)
    return ranked


def verify_run(run_dir, full=False):
    run_dir = Path(run_dir).resolve()
    root = run_dir.parents[3]
    manifest = json.loads((run_dir / "input-manifest.json").read_text(encoding="utf-8"))
    source = Path(manifest["inputs"][0]["local_path"])
    assert source.stat().st_size == manifest["inputs"][0]["bytes"]
    if full:
        assert file_sha256(source) == manifest["inputs"][0]["expected_sha256"], "raw archive hash changed"
    acquisition_path = Path(manifest["acquisition_manifest"])
    assert file_sha256(acquisition_path) == manifest["acquisition_manifest_sha256"]
    summary = json.loads((run_dir / "derived-summary.json").read_text(encoding="utf-8"))
    ceiling = json.loads((run_dir / "removal-ceiling.json").read_text(encoding="utf-8"))
    emitted_histogram = {int(row["cluster_size"]): int(row["cluster_count"]) for row in read_csv(run_dir / "cluster-histogram.csv")}
    con = duckdb.connect(str(run_dir / "work/realnews.duckdb"), read_only=True)
    histogram = assert_cluster_aggregates(con)
    assert histogram == emitted_histogram, "emitted histogram differs from direct released-table aggregation"
    physical_rows = sum(size * count for size, count in histogram.items())
    assert physical_rows == summary["physical_rows"] == ceiling["physical_rows"] == manifest["archive"]["physical_rows"]
    assert con.execute("SELECT COUNT(*) FROM released").fetchone()[0] == physical_rows
    assert sum(histogram.values()) == summary["unique_clusters"]
    assert con.execute("SELECT COUNT(*) FROM clusters").fetchone()[0] == summary["unique_clusters"]
    assert assert_url_coverage(con) == summary["unique_ids"]
    multi_documents = sum(size * count for size, count in histogram.items() if size >= 2)
    multi_clusters = sum(count for size, count in histogram.items() if size >= 2)
    independent_ceiling = {
        "multi_documents": multi_documents,
        "multi_clusters": multi_clusters,
        "removals": multi_documents - multi_clusters,
    }
    for key, value in independent_ceiling.items():
        assert summary[key] == value
        assert ceiling[key] == value
    assert ceiling["retained_release_population"] == physical_rows - independent_ceiling["removals"]
    figure_rows = read_csv(run_dir / "figure-counts.csv")
    for convention in ("dropped", "low", "high"):
        expected = independent_figure_counts(histogram, convention)
        actual = [int(row["cluster_count"]) for row in figure_rows if row["convention"] == convention]
        assert actual == expected, f"figure mismatch: {convention}"
    for row in read_csv(run_dir / "edge-sizes.csv"):
        size = int(row["cluster_size"])
        assert int(row["cluster_count"]) == histogram.get(size, 0)
        assert int(row["document_count"]) == size * histogram.get(size, 0)

    duplicate_ids = con.execute("SELECT COUNT(*) FROM url_stats WHERE total > 1").fetchone()[0]
    duplicate_rows = con.execute("SELECT COALESCE(SUM(total - 1), 0) FROM url_stats WHERE total > 1").fetchone()[0]
    assert duplicate_ids == summary["duplicate_released_ids"]
    assert duplicate_rows == summary["duplicate_released_rows"]
    duplicate_output = read_csv(run_dir / "duplicate-released-urls.csv")
    assert len(duplicate_output) == duplicate_ids
    assert sum(int(row["total"]) - 1 for row in duplicate_output) == duplicate_rows
    keep = dict(con.execute("""
        SELECT 'keep0_multi', SUM(r.keep = 0) FROM released r JOIN clusters c ON r.cluster = c.cluster WHERE c.n_all >= 2
        UNION ALL SELECT 'keep0_singleton', SUM(r.keep = 0) FROM released r JOIN clusters c ON r.cluster = c.cluster WHERE c.n_all = 1
        UNION ALL SELECT 'keep1_multi', SUM(r.keep = 1) FROM released r JOIN clusters c ON r.cluster = c.cluster WHERE c.n_all >= 2
        UNION ALL SELECT 'keep1_singleton', SUM(r.keep = 1) FROM released r JOIN clusters c ON r.cluster = c.cluster WHERE c.n_all = 1
    """).fetchall())
    assert keep == summary["keep_agreement"]
    discrepancy_count = con.execute("SELECT COUNT(*) FROM released r JOIN clusters c ON r.cluster = c.cluster WHERE r.keep <> CASE WHEN c.n_all = 1 THEN 1 ELSE 0 END").fetchone()[0]
    assert discrepancy_count == summary["keep_discrepancy_rows"]
    assert len(read_csv(run_dir / "keep-discrepancies.csv")) == discrepancy_count
    divergence_count = con.execute("SELECT COUNT(*) FROM url_stats WHERE keep0 <> multi_membership").fetchone()[0]
    assert divergence_count == summary["url_divergence_count"]
    assert len(read_csv(run_dir / "url-divergences.csv")) == divergence_count
    assert summary["divergence_status"] == ("KEEP_MEMBERSHIP_DIVERGENCE" if divergence_count else "KEEP_MEMBERSHIP_AGREE")
    eligible = [dict(zip(("url", "total", "keep0", "multi_membership"), row)) for row in con.execute("SELECT url, total, keep0, multi_membership FROM url_stats WHERE total >= 10").fetchall()]
    assert len(eligible) == summary["table11_eligible_ids"]
    expected_top = independent_rank_urls(eligible)
    actual_top = read_csv(run_dir / "table11-top20.csv")
    assert len(actual_top) == len(expected_top)
    for actual, expected in zip(actual_top, expected_top):
        for field in ("rank", "url", "total", "keep0", "frac_dups", "multi_membership", "membership_fraction"):
            assert actual[field] == str(expected[field]), f"ranking mismatch: {field}"

    if (run_dir / "table2-verdicts.csv").exists():
        targets = {row["target_id"]: row for row in read_csv(root / "paper/targets/printed-targets.csv")}
        printed_values = {target_id: row["printed_value"] for target_id, row in targets.items()}
        expected_table2 = nonexecutable_table2(printed_values)
        actual_table2 = read_csv(run_dir / "table2-verdicts.csv")
        assert len(actual_table2) == 3
        for actual, expected in zip(actual_table2, expected_table2):
            for field in expected:
                assert actual[field] == str(expected[field]), f"Table 2 mismatch: {field}"
        expected_figures = grade_figures(figure_rows, printed_values)
        actual_figures = read_csv(run_dir / "figure-verdicts.csv")
        assert len(actual_figures) == len(expected_figures) == 33
        for actual, expected in zip(actual_figures, expected_figures):
            for field in expected:
                assert actual[field] == str(expected[field]), f"figure verdict mismatch: {field}"
        expected_table13 = conditional_table13(
            physical_rows,
            independent_ceiling["removals"],
            targets["table13-realnews-examples-original"]["printed_value"],
            targets["table13-realnews-examples-neardup"]["printed_value"],
        )
        actual_table13 = read_csv(run_dir / "table13-verdicts.csv")[0]
        for field, value in expected_table13.items():
            assert actual_table13[field] == str(value), f"Table 13 mismatch: {field}"
        companion = json.loads((run_dir / "companion-verdicts.json").read_text(encoding="utf-8"))
        assert companion["split_free_ceiling"]["verdict"] == ceiling_verdict(independent_ceiling["removals"])
        assert companion["section5_rounding"]["verdict"] == "MATCH"
        assert companion["tokens"] == {"original": "NOT_EXECUTABLE_INPUT", "neardup": "NOT_EXECUTABLE_INPUT"}
        actual_urls = read_csv(run_dir / "table11-verdicts.csv")
        assert len(actual_urls) == 19
        for index, actual in enumerate(actual_urls, start=1):
            total_target = targets[f"table11-realnews-r{index:02d}-total"]
            frac_target = targets[f"table11-realnews-r{index:02d}-frac"]
            url = total_target["split_or_arm"]
            stats = con.execute("SELECT total, keep0, multi_membership FROM url_stats WHERE url = ?", [url]).fetchone()
            expected = grade_url_value(url, total_target["printed_value"], frac_target["printed_value"], stats)
            for field, value in expected.items():
                assert actual[field] == str(value), f"Table 11 row {index} mismatch: {field}"
    con.close()
    for path in run_dir.iterdir():
        if path.suffix in {".json", ".csv", ".md"}:
            data = path.read_bytes()
            data.decode("utf-8")
            assert b"\r" not in data, f"CR drift: {path}"
    print(f"PASS: Stage 3 direct released-table histogram and URL coverage, independent figures/ranking, source and verdict checks ({physical_rows} rows; full_hash={full})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir")
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    if args.run_dir:
        verify_run(args.run_dir, full=args.full)
    else:
        unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
