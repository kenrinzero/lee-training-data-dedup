#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

try:
    from stage2_identity import ensure_cluster_capacity, ensure_fresh_identity, evaluate_release_identity
    from stage2_audit import accumulate_splits, ensure_fresh_full, random_split_ee, rank_all_duplicate_urls, resume_ingest_ready
    from stage2_compare import companion_verdicts, ensure_fresh_comparison
    from stage2_acquire import HashingReader, validate_receipt_set
except ImportError as exc:
    raise SystemExit(f"FAIL: Stage 2 implementation is missing: {exc}")


class IdentityContractTests(unittest.TestCase):
    def test_identity_requires_exact_rows_and_a_complete_figure_match(self):
        self.assertEqual(
            evaluate_release_identity(365233500, {"dropped": 11, "low": 9, "high": 9})["status"],
            "IDENTITY_HOLD",
        )
        self.assertEqual(
            evaluate_release_identity(365233499, {"dropped": 11, "low": 11, "high": 11})["status"],
            "KILL_RELEASE_IDENTITY",
        )
        self.assertEqual(
            evaluate_release_identity(365233500, {"dropped": 10, "low": 9, "high": 9})["status"],
            "KILL_RELEASE_IDENTITY",
        )

    def test_cluster_capacity_growth_zero_fills(self):
        import numpy as np
        counts = np.array([1, 2], dtype=np.uint32)
        grown = ensure_cluster_capacity(counts, 4)
        self.assertEqual(grown.tolist(), [1, 2, 0, 0, 0])

    def test_identity_outputs_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory)
            ensure_fresh_identity(out_dir)
            (out_dir / "release-identity.json").write_text("existing", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                ensure_fresh_identity(out_dir)


class FullAuditContractTests(unittest.TestCase):
    def test_split_accumulation_hand_fixture(self):
        import numpy as np
        cluster_ids = np.array([0, 1, 1, 2, 2, 3, 3, 3], dtype=np.int64)
        train_counts = np.array([1, 1, 1, 1, 0, 1, 0, 0], dtype=np.uint8)
        validation_counts = np.array([0, 0, 0, 0, 1, 0, 1, 1], dtype=np.uint8)
        n_train = np.zeros(4, dtype=np.uint32)
        n_validation = np.zeros(4, dtype=np.uint32)
        accumulate_splits(cluster_ids, train_counts, validation_counts, n_train, n_validation)
        self.assertEqual(n_train.tolist(), [1, 2, 1, 1])
        self.assertEqual(n_validation.tolist(), [0, 0, 1, 2])

    def test_random_split_expectation_hand_examples(self):
        small = random_split_ee({1: 1, 2: 2}, 5, 2)
        self.assertEqual(small["probability"], Decimal("0.2"))
        pairs_only = random_split_ee({3: 2}, 6, 2)
        self.assertEqual(pairs_only["probability"], Decimal("0.4"))

    def test_companion_dispositions(self):
        verdicts = companion_verdicts([
            {"rule": "A", "derived_removals": "14393547"},
            {"rule": "B", "derived_removals": "14381052"},
            {"rule": "S", "derived_removals": "16896263"},
        ])
        self.assertEqual(verdicts["section5_rounding"]["verdict"], "MATCH")
        self.assertEqual(verdicts["printed_difference_interval"]["A"], "CONSISTENT_INTERVAL")
        self.assertEqual(verdicts["printed_difference_interval"]["B"], "CONSISTENT_INTERVAL")
        self.assertEqual(verdicts["printed_difference_interval"]["S"], "CONTRADICTION")
        self.assertEqual(verdicts["tokens"]["original"], "NOT_EXECUTABLE_INPUT")
        self.assertEqual(verdicts["tokens"]["neardup"], "NOT_EXECUTABLE_INPUT")

    def test_receipt_set_matches_metadata_lfs(self):
        metadata = [{"path": "en/a.json.gz", "size": 3, "lfs": {"oid": hashlib.sha256(b"abc").hexdigest()}}]
        receipts = [{"path": "en/a.json.gz", "bytes": 3, "rows": 2, "sha256": hashlib.sha256(b"abc").hexdigest()}]
        self.assertEqual(validate_receipt_set(metadata, receipts), {"shards": 1, "bytes": 3, "rows": 2})
        receipts[0]["sha256"] = "0" * 64
        with self.assertRaises(AssertionError):
            validate_receipt_set(metadata, receipts)

    def test_all_duplicate_ranking_filters_then_sorts(self):
        rows = [
            {"url": "b.example", "total": 10, "keep0": 10},
            {"url": "a.example", "total": 10, "keep0": 10},
            {"url": "mixed.example", "total": 20, "keep0": 19},
            {"url": "d.example", "total": 5, "keep0": 5},
        ]
        self.assertEqual(rank_all_duplicate_urls(rows), ["a.example", "b.example", "d.example"])

    def test_hashing_reader_covers_partial_reads(self):
        import io
        reader = HashingReader(io.BytesIO(b"abc"))
        self.assertEqual(reader.read(2), b"ab")
        self.assertEqual(reader.read(), b"c")
        self.assertEqual(reader.bytes_read, 3)
        self.assertEqual(reader.hexdigest(), hashlib.sha256(b"abc").hexdigest())

    def test_full_outputs_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory)
            ensure_fresh_full(out_dir)
            (out_dir / "derived-summary.json").write_text("existing", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                ensure_fresh_full(out_dir)

    def test_resume_requires_complete_ingest_tables(self):
        self.assertTrue(resume_ingest_ready({"released", "clusters", "public_masks"}))
        self.assertFalse(resume_ingest_ready({"released", "clusters"}))

    def test_resume_allows_only_incomplete_work_store(self):
        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory)
            (out_dir / "work").mkdir()
            (out_dir / "work/c4.duckdb").write_bytes(b"incomplete")
            ensure_fresh_full(out_dir, resume=True)
            (out_dir / "derived-summary.json").write_text("existing", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                ensure_fresh_full(out_dir, resume=True)

    def test_comparison_outputs_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory)
            ensure_fresh_comparison(out_dir)
            (out_dir / "table2-verdicts.csv").write_text("existing", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                ensure_fresh_comparison(out_dir)


def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_identity(run_dir):
    run_dir = Path(run_dir)
    identity = json.loads((run_dir / "release-identity.json").read_text(encoding="utf-8"))
    manifest = json.loads((run_dir / "input-manifest.json").read_text(encoding="utf-8"))
    source = Path(manifest["inputs"][0]["local_path"])
    assert source.stat().st_size == manifest["inputs"][0]["bytes"]
    assert sha256(source) == manifest["inputs"][0]["expected_sha256"]
    histogram = {int(row["cluster_size"]): int(row["cluster_count"]) for row in read_csv(run_dir / "cluster-histogram.csv")}
    physical_rows = sum(size * count for size, count in histogram.items())
    assert physical_rows == identity["physical_rows"]
    assert sum(histogram.values()) == identity["unique_clusters"]
    from stage1_audit import figure_counts
    figure_rows = read_csv(run_dir / "figure-counts.csv")
    recomputed_matches = {}
    for convention in ("dropped", "low", "high"):
        expected = figure_counts(histogram, convention)
        actual = [int(row["cluster_count"]) for row in figure_rows if row["convention"] == convention]
        assert actual == expected, f"figure mismatch: {convention}"
        recomputed_matches[convention] = sum(int(row["derived_count"]) == int(row["printed_count"]) for row in read_csv(run_dir / "figure-verdicts.csv") if row["convention"] == convention)
    assert recomputed_matches == identity["figure_match_counts"]
    assert identity["status"] == evaluate_release_identity(physical_rows, recomputed_matches)["status"]
    for path in run_dir.iterdir():
        if path.suffix in {".json", ".csv", ".md"}:
            data = path.read_bytes()
            data.decode("utf-8")
            assert b"\r" not in data, f"CR drift: {path}"
    print(f"PASS: Stage 2 identity receipt, histogram, {physical_rows} rows, figure gate, and UTF-8/LF outputs")


def verify_full(run_dir):
    import duckdb
    import numpy as np

    run_dir = Path(run_dir)
    verify_identity(run_dir)
    manifest = json.loads((run_dir / "full-input-manifest.json").read_text(encoding="utf-8"))
    for receipt in manifest["inputs"]:
        source = Path(receipt["local_path"])
        assert source.stat().st_size == receipt["bytes"]
        assert sha256(source) == receipt["expected_sha256"]
    acquisition_path = (run_dir / manifest["acquisition_manifest"]).resolve()
    acquisition = json.loads(acquisition_path.read_text(encoding="utf-8"))
    metadata_path = (run_dir / manifest.get("train_source_metadata", "../train-source-metadata.json")).resolve()
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert sha256(acquisition_path) == manifest["acquisition_manifest_sha256"]
    assert sha256(metadata_path) == manifest["train_source_metadata_sha256"]
    receipt_stats = validate_receipt_set(metadata["files"], acquisition["train_inputs"])
    assert receipt_stats == {"shards": 1024, "bytes": 326778635540, "rows": 364868892}
    assert acquisition["counts"] == manifest["split_sizes"]
    public_db = Path(acquisition["derived_public_db"]["path"])
    assert public_db.stat().st_size == acquisition["derived_public_db"]["bytes"]
    assert sha256(public_db) == acquisition["derived_public_db"]["sha256"]
    assert manifest["derived_public_db"]["sha256"] == acquisition["derived_public_db"]["sha256"]
    work_db = (run_dir / manifest.get("work_db", "work/c4.duckdb")).resolve()
    con = duckdb.connect(str(work_db), read_only=True)
    expected_metrics = {
        "TT": con.execute("SELECT SUM(n_train) FROM composition WHERE n_train >= 2").fetchone()[0] or 0,
        "EE": con.execute("SELECT SUM(n_validation) FROM composition WHERE n_validation >= 2").fetchone()[0] or 0,
        "ET": con.execute("SELECT SUM(n_validation) FROM composition WHERE n_validation >= 1 AND n_train >= 1").fetchone()[0] or 0,
    }
    for row in read_csv(run_dir / "derived-duplication.csv"):
        assert int(row["numerator"]) == expected_metrics[row["metric"]]
    expected_removals = {
        "A": con.execute("SELECT SUM(CASE WHEN n_validation > 0 THEN n_train ELSE GREATEST(n_train - 1, 0) END) FROM composition").fetchone()[0] or 0,
        "B": con.execute("SELECT SUM(GREATEST(n_train - 1, 0)) FROM composition").fetchone()[0] or 0,
        "S": con.execute("SELECT SUM(n_train) FROM composition WHERE n_all >= 2").fetchone()[0] or 0,
    }
    for row in read_csv(run_dir / "derived-removals.csv"):
        assert int(row["removals"]) == expected_removals[row["rule"]]
        assert int(row["retained"]) == manifest["split_sizes"]["train"] - expected_removals[row["rule"]]
    facts = json.loads((run_dir / "cluster-facts.json").read_text(encoding="utf-8"))
    independent_facts = {
        "pair_clusters": con.execute("SELECT COUNT(*) FROM clusters WHERE n_all = 2").fetchone()[0],
        "multi_clusters": con.execute("SELECT COUNT(*) FROM clusters WHERE n_all >= 2").fetchone()[0],
        "clusters_over_5000": con.execute("SELECT COUNT(*) FROM clusters WHERE n_all > 5000").fetchone()[0],
        "clusters_size_5000": con.execute("SELECT COUNT(*) FROM clusters WHERE n_all = 5000").fetchone()[0],
        "largest_cluster_size": con.execute("SELECT MAX(n_all) FROM clusters").fetchone()[0],
        "singleton_documents": con.execute("SELECT SUM(n_all) FROM clusters WHERE n_all = 1").fetchone()[0],
        "multi_cluster_documents": con.execute("SELECT SUM(n_all) FROM clusters WHERE n_all >= 2").fetchone()[0],
    }
    for name, value in independent_facts.items():
        assert facts[name] == value, f"cluster fact mismatch: {name}"
    assert facts["pair_majority"] == (facts["pair_clusters"] > facts["multi_clusters"] / 2)
    summary = json.loads((run_dir / "derived-summary.json").read_text(encoding="utf-8"))
    join = summary["split_join"]
    balance = dict(con.execute("SELECT 'train', SUM(n_train) FROM composition UNION ALL SELECT 'validation', SUM(n_validation) FROM composition").fetchall())
    assert join["population_balance"] == balance == manifest["split_sizes"]
    released_url_counts = np.load(work_db.parent / "released_url_counts.npy", mmap_mode="r")
    duplicate_mask = released_url_counts > 1
    cross_public = con.execute("SELECT COUNT(*) FROM public_masks WHERE train_count > 0 AND validation_count > 0").fetchone()[0]
    cross_released = 0 if cross_public == 0 else con.execute("SELECT COUNT(*) FROM released r JOIN public_masks m ON r.id = m.url WHERE m.train_count > 0 AND m.validation_count > 0").fetchone()[0]
    expected_join = {
        "public_unique_keys": con.execute("SELECT COUNT(*) FROM public_masks").fetchone()[0],
        "duplicate_public_keys": con.execute("SELECT COUNT(*) FROM public_masks WHERE train_count > 1 OR validation_count > 1").fetchone()[0],
        "cross_split_public_keys": cross_public,
        "unmatched_released_rows": con.execute("SELECT COUNT(*) FROM released_public WHERE public_rowid = -1").fetchone()[0],
        "cross_split_released_rows": cross_released,
        "duplicate_released_urls": int(np.count_nonzero(duplicate_mask)),
        "duplicate_released_rows": int((released_url_counts[duplicate_mask] - 1).sum()),
    }
    for name, value in expected_join.items():
        assert join[name] == value, f"join diagnostic mismatch: {name}"
    missing_keys = missing_rows = 0
    con.complete()
    public_reader = con.sql("SELECT rowid, total FROM public_masks").to_arrow_reader(1000000)
    for batch in public_reader:
        public_ids = batch.column(0).to_numpy(zero_copy_only=False)
        totals = batch.column(1).to_numpy(zero_copy_only=False)
        missing = released_url_counts[public_ids] == 0
        missing_keys += int(np.count_nonzero(missing))
        missing_rows += int(totals[missing].sum())
    assert (join["missing_public_keys"], join["missing_public_rows"]) == (missing_keys, missing_rows)
    complete = not any((join["unmatched_released_rows"], join["cross_split_released_rows"], join["missing_public_rows"])) and balance == manifest["split_sizes"]
    assert join["status"] == ("COMPLETE" if complete else "INDETERMINATE_JOIN")
    assert summary["url_divergence_count"] == con.execute("SELECT COUNT(*) FROM url_stats WHERE keep0 <> multi_membership").fetchone()[0]
    histogram = {int(row["cluster_size"]): int(row["cluster_count"]) for row in read_csv(run_dir / "cluster-histogram.csv")}
    identity = json.loads((run_dir / "release-identity.json").read_text(encoding="utf-8"))
    expected = random_split_ee(histogram, identity["physical_rows"], manifest["split_sizes"]["validation"])
    actual = json.loads((run_dir / "random-split-ee.json").read_text(encoding="utf-8"))
    assert actual["expected_numerator"] == str(expected["expected_numerator"])
    assert actual["probability"] == str(expected["probability"])
    eligible = [dict(zip(("url", "total", "keep0", "multi_membership"), row)) for row in con.execute("SELECT url, total, keep0, multi_membership FROM url_stats WHERE keep0 = total").fetchall()]
    expected_urls = rank_all_duplicate_urls(eligible)[:20]
    actual_urls = [row["url"] for row in read_csv(run_dir / "table11-top20.csv")]
    assert actual_urls == expected_urls
    con.close()
    for path in run_dir.iterdir():
        if path.suffix in {".json", ".csv", ".md"}:
            data = path.read_bytes()
            data.decode("utf-8")
            assert b"\r" not in data, f"CR drift: {path}"
    print(f"PASS: full Stage 2 split receipts, metrics, removals, cluster facts, random split, Table 11 ranking, and UTF-8/LF outputs")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir")
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    if args.run_dir:
        verify_full(args.run_dir) if args.full else verify_identity(args.run_dir)
    else:
        suite = unittest.TestSuite((
            unittest.defaultTestLoader.loadTestsFromTestCase(IdentityContractTests),
            unittest.defaultTestLoader.loadTestsFromTestCase(FullAuditContractTests),
        ))
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            raise SystemExit(1)


if __name__ == "__main__":
    main()
