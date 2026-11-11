#!/usr/bin/env python3
import argparse
import csv
import io
import json
import platform
import sys
import tarfile
import time
from datetime import datetime, timezone
from decimal import Decimal, getcontext
from pathlib import Path

import duckdb
import pyarrow as pa

from stage1_audit import (
    BIN_LABELS,
    EDGE_SIZES,
    figure_counts,
    receipt,
    run_name,
    sha256,
    write_csv,
    write_json,
)

getcontext().prec = 60

REALNEWS_URL = "https://storage.googleapis.com/gresearch/data_deduplication/realnews.tar.gz"
EXPECTED_ARCHIVE_BYTES = 1428191066
EXPECTED_ARCHIVE_SHA256 = "27b14ae911e3bb2632f2a087e84f24c0f5163786d77ff92e1bbfa9d47473046c"
EXPECTED_DECOMPRESSED_BYTES = 3432651696
RIGHTS = "Cluster redistribution rights are unresolved; keep raw inputs local and publish aggregates only."
AUDIT_OUTPUTS = (
    "input-manifest.json",
    "derived-summary.json",
    "cluster-histogram.csv",
    "figure-counts.csv",
    "edge-sizes.csv",
    "removal-ceiling.json",
    "table11-top20.csv",
    "duplicate-released-urls.csv",
    "keep-discrepancies.csv",
    "url-divergences.csv",
    "work/realnews.duckdb",
)


def ceiling_from_histogram(histogram):
    multi_documents = sum(size * count for size, count in histogram.items() if size >= 2)
    multi_clusters = sum(count for size, count in histogram.items() if size >= 2)
    return {
        "multi_documents": multi_documents,
        "multi_clusters": multi_clusters,
        "removals": multi_documents - multi_clusters,
    }


def rank_urls(rows, limit=20):
    eligible = [dict(row) for row in rows if int(row["total"]) >= 10]
    eligible.sort(key=lambda row: row["url"].encode("utf-8"))
    eligible.sort(key=lambda row: int(row["total"]), reverse=True)
    eligible.sort(key=lambda row: Decimal(int(row["keep0"])) / Decimal(int(row["total"])), reverse=True)
    ranked = []
    for rank, row in enumerate(eligible[:limit], start=1):
        total = int(row["total"])
        row["rank"] = rank
        row["frac_dups"] = str(Decimal(int(row["keep0"])) / Decimal(total))
        row["membership_fraction"] = str(Decimal(int(row["multi_membership"])) / Decimal(total))
        ranked.append(row)
    return ranked


def ensure_fresh_audit(out_dir):
    out_dir = Path(out_dir)
    existing = [name for name in AUDIT_OUTPUTS if (out_dir / name).exists()]
    if existing:
        raise FileExistsError(f"refusing to overwrite Stage 3 audit outputs in {out_dir}: {existing}")


def create_url_stats(con):
    con.execute("""
        CREATE TABLE url_stats AS
        SELECT r.id AS url, COUNT(*) AS total,
               SUM(r.keep = 0) AS keep0,
               SUM(c.n_all >= 2) AS multi_membership
        FROM released r
        JOIN clusters c ON r.cluster = c.cluster
        GROUP BY r.id
    """)


def ingest_archive(archive, con, expected_member_size=EXPECTED_DECOMPRESSED_BYTES, batch_size=250000):
    archive = Path(archive)
    row_offset = 0
    with tarfile.open(archive, "r:gz") as tar:
        member = tar.next()
        if member is None or not member.isfile() or member.name != "realnews.csv":
            raise ValueError(f"unexpected first archive member: {member}")
        if member.size != expected_member_size:
            raise ValueError(f"unexpected decompressed size: {member.size} != {expected_member_size}")
        raw = tar.extractfile(member)
        if raw is None:
            raise ValueError("archive member cannot be read")
        with io.TextIOWrapper(raw, encoding="utf-8", newline="") as text:
            reader = csv.reader(text, strict=True)
            header = next(reader)
            if header != ["id", "keep", "cluster"]:
                raise ValueError(f"unexpected CSV header: {header}")
            ids, keeps, clusters = [], [], []

            def flush():
                nonlocal row_offset
                if not ids:
                    return
                row_ids = pa.array(range(row_offset + 1, row_offset + len(ids) + 1), type=pa.int64())
                table = pa.Table.from_pydict(
                    {"id": ids, "keep": keeps, "cluster": clusters},
                    schema=pa.schema([("id", pa.string()), ("keep", pa.int32()), ("cluster", pa.int64())]),
                )
                table = table.add_column(0, "row_id", row_ids)
                con.register("stage3_batch", table)
                con.execute("INSERT INTO released SELECT row_id, id, keep, cluster FROM stage3_batch")
                con.unregister("stage3_batch")
                row_offset += len(ids)
                if row_offset % 5000000 < len(ids):
                    print(f"streamed {row_offset} released rows", flush=True)
                ids.clear()
                keeps.clear()
                clusters.clear()

            for row_number, values in enumerate(reader, start=1):
                if len(values) != 3 or any(value == "" for value in values):
                    raise ValueError(f"malformed row {row_number}: {values}")
                document_id, keep_text, cluster_text = values
                if keep_text not in {"0", "1"}:
                    raise ValueError(f"invalid keep at row {row_number}: {keep_text}")
                cluster = int(cluster_text)
                if cluster < 0 or cluster >= 2**63:
                    raise ValueError(f"invalid cluster at row {row_number}: {cluster_text}")
                ids.append(document_id)
                keeps.append(int(keep_text))
                clusters.append(cluster)
                if len(ids) >= batch_size:
                    flush()
            flush()
            decompressed_bytes = raw.tell()
        if decompressed_bytes != member.size:
            raise ValueError(f"consumed bytes differ: {decompressed_bytes} != {member.size}")
        if tar.next() is not None:
            raise ValueError("unexpected extra archive member")
    return {
        "member": member.name,
        "decompressed_bytes": decompressed_bytes,
        "header": header,
        "physical_rows": row_offset,
    }


def rows_for_csv(rows, fields):
    return [dict(zip(fields, row)) for row in rows]


def run_audit(root, out_dir):
    started = time.perf_counter()
    root = Path(root).resolve()
    out_dir = Path(out_dir)
    ensure_fresh_audit(out_dir)
    archive = root / "data/raw/clusters/realnews.tar.gz"
    inputs = [receipt(archive, REALNEWS_URL, EXPECTED_ARCHIVE_BYTES, RIGHTS, EXPECTED_ARCHIVE_SHA256)]
    acquisition_path = out_dir.parent / "acquisition-manifest.json"
    acquisition = json.loads(acquisition_path.read_text(encoding="utf-8"))
    acquired = acquisition["inputs"][0]
    assert acquired["bytes"] == inputs[0]["bytes"]
    assert acquired["sha256"] == inputs[0]["sha256"]
    assert Path(acquired["local_path"]) == archive
    out_dir.mkdir(parents=True, exist_ok=False)
    work = out_dir / "work"
    work.mkdir()
    database_path = work / "realnews.duckdb"
    con = duckdb.connect(str(database_path))
    con.execute("SET threads TO 1")
    con.execute("SET memory_limit = '4GB'")
    con.execute("SET preserve_insertion_order = false")
    con.execute(f"SET temp_directory = '{(work / 'tmp').as_posix()}'")
    con.execute("CREATE TABLE released (row_id BIGINT, id VARCHAR, keep INTEGER, cluster BIGINT)")
    archive_info = ingest_archive(archive, con)
    con.execute("""
        CREATE TABLE clusters AS
        SELECT cluster, COUNT(*) AS n_all,
               SUM(keep = 0) AS keep0, SUM(keep = 1) AS keep1
        FROM released GROUP BY cluster
    """)
    create_url_stats(con)

    fields = ("url", "total")
    write_csv(
        out_dir / "duplicate-released-urls.csv",
        fields,
        rows_for_csv(con.execute("SELECT url, total FROM url_stats WHERE total > 1 ORDER BY url").fetchall(), fields),
    )
    fields = ("row_id", "url", "cluster", "keep", "cluster_size", "expected_keep")
    write_csv(
        out_dir / "keep-discrepancies.csv",
        fields,
        rows_for_csv(con.execute("""
            SELECT r.row_id, r.id, r.cluster, r.keep, c.n_all,
                   CASE WHEN c.n_all = 1 THEN 1 ELSE 0 END
            FROM released r JOIN clusters c ON r.cluster = c.cluster
            WHERE r.keep <> CASE WHEN c.n_all = 1 THEN 1 ELSE 0 END
            ORDER BY r.row_id
        """).fetchall(), fields),
    )
    fields = ("url", "total", "keep0", "multi_membership")
    write_csv(
        out_dir / "url-divergences.csv",
        fields,
        rows_for_csv(con.execute("SELECT url, total, keep0, multi_membership FROM url_stats WHERE keep0 <> multi_membership ORDER BY url").fetchall(), fields),
    )

    fields = ("cluster_size", "cluster_count", "document_count")
    histogram_rows = rows_for_csv(con.execute("""
        SELECT n_all, COUNT(*), SUM(n_all) FROM clusters GROUP BY n_all ORDER BY n_all
    """).fetchall(), fields)
    write_csv(out_dir / "cluster-histogram.csv", fields, histogram_rows)
    histogram = {int(row["cluster_size"]): int(row["cluster_count"]) for row in histogram_rows}
    write_csv(
        out_dir / "edge-sizes.csv",
        fields,
        ({"cluster_size": size, "cluster_count": histogram.get(size, 0), "document_count": size * histogram.get(size, 0)} for size in EDGE_SIZES),
    )
    figure_rows = []
    for convention in ("dropped", "low", "high"):
        counts = figure_counts(histogram, convention)
        for bin_index, (label, count) in enumerate(zip(BIN_LABELS, counts), start=1):
            figure_rows.append({"convention": convention, "bin_index": bin_index, "bin_label": label, "cluster_count": count})
    write_csv(out_dir / "figure-counts.csv", ("convention", "bin_index", "bin_label", "cluster_count"), figure_rows)

    ceiling = ceiling_from_histogram(histogram)
    physical_rows = archive_info["physical_rows"]
    write_json(out_dir / "removal-ceiling.json", {
        **ceiling,
        "physical_rows": physical_rows,
        "retained_release_population": physical_rows - ceiling["removals"],
        "population": "released archive, all splits; not a verified public train population",
        "formula": "U=D_multi-C_multi=sum_{c:n_all(c)>=2}(n_all(c)-1)",
    })
    eligible_rows = rows_for_csv(con.execute("SELECT url, total, keep0, multi_membership FROM url_stats WHERE total >= 10").fetchall(), ("url", "total", "keep0", "multi_membership"))
    top_rows = rank_urls(eligible_rows)
    write_csv(
        out_dir / "table11-top20.csv",
        ("rank", "url", "total", "keep0", "frac_dups", "multi_membership", "membership_fraction"),
        top_rows,
    )

    keep = dict(con.execute("""
        SELECT 'keep0_multi', SUM(r.keep = 0) FROM released r JOIN clusters c ON r.cluster = c.cluster WHERE c.n_all >= 2
        UNION ALL SELECT 'keep0_singleton', SUM(r.keep = 0) FROM released r JOIN clusters c ON r.cluster = c.cluster WHERE c.n_all = 1
        UNION ALL SELECT 'keep1_multi', SUM(r.keep = 1) FROM released r JOIN clusters c ON r.cluster = c.cluster WHERE c.n_all >= 2
        UNION ALL SELECT 'keep1_singleton', SUM(r.keep = 1) FROM released r JOIN clusters c ON r.cluster = c.cluster WHERE c.n_all = 1
    """).fetchall())
    divergence_count = con.execute("SELECT COUNT(*) FROM url_stats WHERE keep0 <> multi_membership").fetchone()[0]
    duplicate_ids = con.execute("SELECT COUNT(*) FROM url_stats WHERE total > 1").fetchone()[0]
    duplicate_rows = con.execute("SELECT COALESCE(SUM(total - 1), 0) FROM url_stats WHERE total > 1").fetchone()[0]
    summary = {
        "physical_rows": physical_rows,
        "unique_ids": con.execute("SELECT COUNT(*) FROM url_stats").fetchone()[0],
        "unique_clusters": con.execute("SELECT COUNT(*) FROM clusters").fetchone()[0],
        "duplicate_released_ids": duplicate_ids,
        "duplicate_released_rows": duplicate_rows,
        "singleton_documents": histogram.get(1, 0),
        **ceiling,
        "malformed_rows": 0,
        "empty_field_rows": 0,
        "row_order": "physical released CSV order; one-based data row numbers in diagnostics",
        "population": "released archive, all splits",
        "keep_agreement": keep,
        "keep_discrepancy_rows": con.execute("SELECT COUNT(*) FROM released r JOIN clusters c ON r.cluster = c.cluster WHERE r.keep <> CASE WHEN c.n_all = 1 THEN 1 ELSE 0 END").fetchone()[0],
        "url_divergence_count": divergence_count,
        "divergence_status": "KEEP_MEMBERSHIP_DIVERGENCE" if divergence_count else "KEEP_MEMBERSHIP_AGREE",
        "table11_eligible_ids": len(eligible_rows),
    }
    write_json(out_dir / "derived-summary.json", summary)
    con.execute("CHECKPOINT")
    con.close()
    scratch_bytes = sum(path.stat().st_size for path in work.rglob("*") if path.is_file())
    write_json(out_dir / "input-manifest.json", {
        "stage": f"Stage 3 / {run_name(out_dir)}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "command": [sys.executable, *sys.argv],
        "python": sys.version,
        "platform": platform.platform(),
        "duckdb": duckdb.__version__,
        "pyarrow": pa.__version__,
        "csv_parser": "Python csv.reader(strict=True), UTF-8, typed batches into DuckDB",
        "archive": archive_info,
        "inputs": inputs,
        "acquisition_manifest": str(acquisition_path.resolve()),
        "acquisition_manifest_sha256": sha256(acquisition_path),
        "work_db": "work/realnews.duckdb",
        "scratch_bytes": scratch_bytes,
        "elapsed_seconds": time.perf_counter() - started,
        "code_sha256": {
            "src/stage1_audit.py": sha256(root / "src/stage1_audit.py"),
            "src/stage3_audit.py": sha256(root / "src/stage3_audit.py"),
            "src/stage3_compare.py": sha256(root / "src/stage3_compare.py"),
            "src/stage3_report.py": sha256(root / "src/stage3_report.py"),
            "src/verify_stage3.py": sha256(root / "src/verify_stage3.py"),
            "src/verify_stage3_report.py": sha256(root / "src/verify_stage3_report.py"),
        },
    })
    print(json.dumps({
        "rows": physical_rows,
        "clusters": summary["unique_clusters"],
        "removals": ceiling["removals"],
        "table11_eligible": len(eligible_rows),
        "scratch_bytes": scratch_bytes,
        "elapsed_seconds": time.perf_counter() - started,
    }, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    run_audit(args.root, args.out_dir)


if __name__ == "__main__":
    main()
