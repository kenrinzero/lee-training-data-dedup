#!/usr/bin/env python3
import argparse
import csv
import io
import json
import platform
import sys
import tarfile
from datetime import datetime, timezone
from decimal import Decimal, getcontext
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.csv as pa_csv

from stage1_audit import receipt, run_name, sha256, write_csv, write_json

getcontext().prec = 60

SPLIT_SIZES = {"train": 364868892, "validation": 364608}
SPLIT_ROOT_SHA = "1588ec454efa1a09f29cd18ddd04fe05fc8653a2"
EXPECTED_SPLIT_BYTES = {
    "train-00000.parquet": 312302655,
    "train-00001.parquet": 314250060,
    "train-00002.parquet": 312268050,
    "train-00003.parquet": 312065965,
    "train-00004.parquet": 308599130,
    "train-00005.parquet": 312308752,
    "train-00006.parquet": 313118966,
    "train-00007.parquet": 313275039,
    "train-00008.parquet": 312402829,
    "train-00009.parquet": 273854946,
    "validation-00000.parquet": 311994499,
    "validation-00001.parquet": 197281279,
}
EXPECTED_SPLIT_SHA256 = {
    "train-00000.parquet": "f037570cc07478d7d66acd7e90e26730977af798321f29f030b24acb02767d36",
    "train-00001.parquet": "dc4254969e16c58b80ac3bed3dfd2c1c614c8be23d0a58c321eeb53574b7846a",
    "train-00002.parquet": "b88d598fe84f9573a76672cd5cf07eddc68c1330de85d65685020ee0dc2927da",
    "train-00003.parquet": "e0433e40ec1d50e00f3d98555509dea6895796927c096ff38a8660417a0cb757",
    "train-00004.parquet": "a63f29a3ecb6172cd7ca8bfb7550744c14842284c9202519ca1f8232bf959ade",
    "train-00005.parquet": "e2b4340fe887f2f618786015e3a78664f26af4222aa7815c8b6500405dc3a347",
    "train-00006.parquet": "a272945443ccdb16e8643d2fec708896b2d75e24a8d95acc74e9eaf1c11b9e4c",
    "train-00007.parquet": "0177f692e952258332d6641df494f79eca312d063a210b5834fdfd92e43dfe5b",
    "train-00008.parquet": "bd6418278b33b64334c14f4da4e5f7c8daccbf6e4294c9021130e76098477a4f",
    "train-00009.parquet": "2f3fe85eb34855670902e16aca30a08b36e29bf94cfbefaef7102364f9680552",
    "validation-00000.parquet": "709bd820dacbaeb50025a0ebf5bfd311745b5a90cd6941887a01b1faf00ff285",
    "validation-00001.parquet": "6f276e569450e157cad26d67d7623f82f512b2a67d317188b7717b29c6da565f",
}
FULL_OUTPUTS = (
    "full-input-manifest.json",
    "derived-summary.json",
    "derived-duplication.csv",
    "derived-removals.csv",
    "cluster-facts.json",
    "random-split-ee.json",
    "random-split-ratios.csv",
    "table11-top20.csv",
    "duplicate-public-keys.csv",
    "cross-split-public-keys.csv",
    "duplicate-released-urls.csv",
    "unmatched-released-keys.csv",
    "missing-public-keys.csv",
    "keep-discrepancies.csv",
    "url-divergences.csv",
    "work/c4.duckdb",
)


def random_split_ee(histogram, population, evaluation_size):
    train_size = population - evaluation_size
    expected_numerator = Decimal(0)
    ratios = {}
    no_train_partner = Decimal(1)
    maximum_size = max(histogram, default=0)
    for size in range(1, maximum_size + 1):
        if size == 1:
            ratios[size] = no_train_partner
            continue
        index = size - 2
        no_train_partner *= Decimal(train_size - index) / Decimal(population - 1 - index)
        ratios[size] = no_train_partner
        if size in histogram:
            expected_numerator += Decimal(size * histogram[size]) * (Decimal(1) - no_train_partner)
    return {
        "population": population,
        "evaluation_size": evaluation_size,
        "train_size": train_size,
        "expected_numerator": expected_numerator,
        "probability": expected_numerator / Decimal(population),
        "no_train_partner_ratios": ratios,
    }


def rank_all_duplicate_urls(rows):
    eligible = [row for row in rows if row["total"] > 0 and row["keep0"] == row["total"]]
    eligible.sort(key=lambda row: (-row["total"], row["url"].encode("utf-8")))
    return [row["url"] for row in eligible]


def resume_ingest_ready(table_names):
    return {"released", "clusters", "public_masks"}.issubset(table_names)


def ensure_fresh_full(out_dir, resume=False):
    out_dir = Path(out_dir)
    existing = [name for name in FULL_OUTPUTS if (out_dir / name).exists()]
    if resume:
        existing = [name for name in existing if name != "work/c4.duckdb"]
    if existing:
        raise FileExistsError(f"refusing to overwrite Stage 2 full-audit outputs in {out_dir}: {existing}")


def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def rows_for_csv(rows, fields):
    return [dict(zip(fields, row)) for row in rows]


def accumulate_splits(cluster_ids, train_counts, validation_counts, n_train, n_validation):
    train_mask = (train_counts > 0) & (validation_counts == 0)
    validation_mask = (validation_counts > 0) & (train_counts == 0)
    np.add.at(n_train, cluster_ids[train_mask], 1)
    np.add.at(n_validation, cluster_ids[validation_mask], 1)


def create_composition(con, work):
    writer = con.cursor()
    con.execute("CREATE TABLE IF NOT EXISTS composition (cluster BIGINT, n_all BIGINT, keep0 BIGINT, keep1 BIGINT, n_train BIGINT, n_validation BIGINT)")
    con.execute("CREATE TABLE IF NOT EXISTS released_public (released_rowid BIGINT, public_rowid BIGINT)")
    assert con.execute("SELECT COUNT(*) FROM composition").fetchone()[0] == 0
    assert con.execute("SELECT COUNT(*) FROM released_public").fetchone()[0] == 0
    maximum_cluster = con.execute("SELECT MAX(cluster) FROM clusters").fetchone()[0]
    public_count = con.execute("SELECT COUNT(*) FROM public_masks").fetchone()[0]
    n_train = np.zeros(maximum_cluster + 1, dtype=np.uint32)
    n_validation = np.zeros(maximum_cluster + 1, dtype=np.uint32)
    released_url_counts = np.zeros(public_count + 1, dtype=np.uint32)
    unmatched = cross_split = processed = 0
    con.complete()
    reader = con.sql("""
        SELECT r.row_id, r.cluster, m.rowid, m.train_count, m.validation_count
        FROM released r LEFT JOIN public_masks m ON r.id = m.url
    """).to_arrow_reader(1000000)
    for batch in reader:
        released_ids = batch.column(0).to_numpy(zero_copy_only=False)
        cluster_ids = batch.column(1).to_numpy(zero_copy_only=False)
        public_ids = batch.column(2).fill_null(-1).to_numpy(zero_copy_only=False)
        train_counts = batch.column(3).fill_null(0).to_numpy(zero_copy_only=False)
        validation_counts = batch.column(4).fill_null(0).to_numpy(zero_copy_only=False)
        accumulate_splits(cluster_ids, train_counts, validation_counts, n_train, n_validation)
        matched = public_ids >= 0
        np.add.at(released_url_counts, public_ids[matched], 1)
        unmatched += int(np.count_nonzero(~matched))
        cross_split += int(np.count_nonzero((train_counts > 0) & (validation_counts > 0)))
        output = pa.table({"released_rowid": pa.array(released_ids, type=pa.int64()), "public_rowid": pa.array(public_ids, type=pa.int64())})
        writer.register("released_public_batch", output)
        writer.execute("INSERT INTO released_public SELECT * FROM released_public_batch")
        writer.unregister("released_public_batch")
        processed += batch.num_rows
        if processed % 50000000 < batch.num_rows:
            print(f"joined {processed} released rows", flush=True)
    np.save(work / "n_train.npy", n_train)
    np.save(work / "n_validation.npy", n_validation)
    np.save(work / "released_url_counts.npy", released_url_counts)
    missing_keys = missing_rows = 0
    con.complete()
    public_reader = con.sql("SELECT rowid, total FROM public_masks").to_arrow_reader(1000000)
    for batch in public_reader:
        public_ids = batch.column(0).to_numpy(zero_copy_only=False)
        totals = batch.column(1).to_numpy(zero_copy_only=False)
        missing = released_url_counts[public_ids] == 0
        missing_keys += int(np.count_nonzero(missing))
        missing_rows += int(totals[missing].sum())
    duplicate_mask = released_url_counts > 1
    duplicate_urls = int(np.count_nonzero(duplicate_mask))
    duplicate_rows = int((released_url_counts[duplicate_mask] - 1).sum())
    con.complete()
    cluster_reader = con.sql("SELECT cluster, n_all, keep0, keep1 FROM clusters").to_arrow_reader(1000000)
    for batch in cluster_reader:
        cluster_ids = batch.column(0).to_numpy(zero_copy_only=False)
        output = pa.table({
            "cluster": pa.array(cluster_ids, type=pa.int64()),
            "n_all": batch.column(1),
            "keep0": batch.column(2),
            "keep1": batch.column(3),
            "n_train": pa.array(n_train[cluster_ids], type=pa.int64()),
            "n_validation": pa.array(n_validation[cluster_ids], type=pa.int64()),
        })
        writer.register("composition_batch", output)
        writer.execute("INSERT INTO composition SELECT * FROM composition_batch")
        writer.unregister("composition_batch")
    return {
        "unmatched_released_rows": unmatched,
        "cross_split_released_rows": cross_split,
        "missing_public_keys": missing_keys,
        "missing_public_rows": missing_rows,
        "duplicate_released_urls": duplicate_urls,
        "duplicate_released_rows": duplicate_rows,
        "population_balance": {"train": int(n_train.sum()), "validation": int(n_validation.sum())},
    }


def run_full_audit(root, out_dir, resume=False):
    import duckdb

    root = Path(root).resolve()
    out_dir = Path(out_dir)
    ensure_fresh_full(out_dir, resume=resume)
    identity = json.loads((out_dir / "release-identity.json").read_text(encoding="utf-8"))
    assert identity["status"] == "IDENTITY_HOLD"
    acquisition_manifest_path = out_dir.parent / "split-acquisition-manifest.json"
    acquisition = json.loads(acquisition_manifest_path.read_text(encoding="utf-8"))
    public_db = Path(acquisition["derived_public_db"]["path"])
    assert public_db.stat().st_size == acquisition["derived_public_db"]["bytes"]
    assert sha256(public_db) == acquisition["derived_public_db"]["sha256"]
    split_receipts = []
    for name in ("validation-00000.parquet", "validation-00001.parquet"):
        index = int(name.split("-")[1].split(".")[0])
        path = root / "data/raw/c4/en" / name
        url = f"https://huggingface.co/api/datasets/allenai/c4/parquet/en/validation/{index}.parquet"
        split_receipts.append(receipt(
            path,
            url,
            EXPECTED_SPLIT_BYTES[name],
            "C4 is ODC-BY; keep acquired source files local and publish aggregates only.",
            EXPECTED_SPLIT_SHA256[name],
        ))

    work = out_dir / "work"
    work.mkdir(exist_ok=True)
    database_path = work / "c4.duckdb"
    con = duckdb.connect(str(database_path))
    con.execute("SET threads TO 1")
    con.execute("SET memory_limit = '20GB'")
    con.execute("SET preserve_insertion_order = false")
    con.execute(f"SET temp_directory = '{(work / 'tmp').as_posix()}'")
    if resume:
        table_names = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
        assert resume_ingest_ready(table_names), f"cannot resume incomplete tables: {table_names}"
    else:
        con.execute("CREATE TABLE released (row_id BIGINT, id VARCHAR, keep INTEGER, cluster BIGINT)")
    archive = root / "data/raw/clusters/c4.tar.gz"
    if resume:
        row_offset = con.execute("SELECT COUNT(*) FROM released").fetchone()[0]
    else:
        row_offset = 0
        with tarfile.open(archive, "r:gz") as tar:
            members = [member for member in tar.getmembers() if member.isfile()]
            assert len(members) == 1 and members[0].name == "c4.csv"
            member = members[0]
            raw = tar.extractfile(member)
            assert raw is not None
            reader = pa_csv.open_csv(
                raw,
                read_options=pa_csv.ReadOptions(column_names=["id", "keep", "cluster"], block_size=16 * 1024 * 1024, skip_rows=1),
                convert_options=pa_csv.ConvertOptions(
                    column_types=pa.schema([("id", pa.string()), ("keep", pa.int32()), ("cluster", pa.int64())]),
                    include_columns=["id", "keep", "cluster"],
                    strings_can_be_null=False,
                ),
            )
            for batch in reader:
                row_ids = pa.array(range(row_offset + 1, row_offset + batch.num_rows + 1), type=pa.int64())
                table = pa.Table.from_batches([batch])
                table = table.add_column(0, "row_id", row_ids)
                con.register("batch_arrow", table)
                con.execute("INSERT INTO released SELECT row_id, id, keep, cluster FROM batch_arrow")
                con.unregister("batch_arrow")
                row_offset += batch.num_rows
                if row_offset % 25000000 < batch.num_rows:
                    print(f"streamed {row_offset} released rows", flush=True)
    assert row_offset == identity["physical_rows"]

    con.execute("ATTACH ? AS public_source (READ_ONLY)", [str(public_db)])
    public_counts = dict(con.execute("SELECT split, COUNT(*) FROM public_source.public GROUP BY split").fetchall())
    assert public_counts == SPLIT_SIZES, f"public split counts differ: {public_counts}"
    if not resume:
        con.execute("""
            CREATE TABLE public_masks AS
            SELECT url, COUNT(*) AS total,
                   SUM(split = 'train') AS train_count,
                   SUM(split = 'validation') AS validation_count
            FROM public_source.public GROUP BY url
        """)
    con.execute("DETACH public_source")
    if not resume:
        con.execute("""
            CREATE TABLE clusters AS
            SELECT cluster, COUNT(*) AS n_all,
                   SUM(keep = 0) AS keep0, SUM(keep = 1) AS keep1
            FROM released GROUP BY cluster
        """)
    join_stream = create_composition(con, work)
    con.execute("CREATE TABLE keep0_urls AS SELECT DISTINCT id FROM released WHERE keep = 0")
    con.execute("""
        CREATE TABLE url_stats AS
        SELECT r.id AS url, COUNT(*) AS total,
               SUM(r.keep = 0) AS keep0,
               SUM(c.n_all >= 2) AS multi_membership
        FROM released r
        JOIN keep0_urls k ON r.id = k.id
        JOIN clusters c ON r.cluster = c.cluster
        GROUP BY r.id
    """)

    join_summary = {
        "public_physical_counts": public_counts,
        "public_unique_keys": con.execute("SELECT COUNT(*) FROM public_masks").fetchone()[0],
        "duplicate_public_keys": con.execute("SELECT COUNT(*) FROM public_masks WHERE train_count > 1 OR validation_count > 1").fetchone()[0],
        "duplicate_public_rows": con.execute("SELECT COALESCE(SUM(GREATEST(train_count - 1, 0) + GREATEST(validation_count - 1, 0)), 0) FROM public_masks").fetchone()[0],
        "cross_split_public_keys": con.execute("SELECT COUNT(*) FROM public_masks WHERE train_count > 0 AND validation_count > 0").fetchone()[0],
        **join_stream,
    }
    balance = join_summary["population_balance"]
    join_summary["expected_population_balance"] = SPLIT_SIZES
    join_complete = not any((join_summary["unmatched_released_rows"], join_summary["cross_split_released_rows"], join_summary["missing_public_rows"])) and balance == SPLIT_SIZES
    join_summary["status"] = "COMPLETE" if join_complete else "INDETERMINATE_JOIN"
    join_summary["estimand"] = "released-physical-row weighted"

    write_csv(out_dir / "duplicate-public-keys.csv", ("url", "train_count", "validation_count"), rows_for_csv(con.execute("SELECT url, train_count, validation_count FROM public_masks WHERE train_count > 1 OR validation_count > 1 ORDER BY url").fetchall(), ("url", "train_count", "validation_count")))
    write_csv(out_dir / "cross-split-public-keys.csv", ("url", "train_count", "validation_count"), rows_for_csv(con.execute("SELECT url, train_count, validation_count FROM public_masks WHERE train_count > 0 AND validation_count > 0 ORDER BY url").fetchall(), ("url", "train_count", "validation_count")))
    write_csv(out_dir / "duplicate-released-urls.csv", ("url", "count"), rows_for_csv(con.execute("SELECT m.url, d.n FROM (SELECT public_rowid, COUNT(*) AS n FROM released_public WHERE public_rowid >= 0 GROUP BY public_rowid HAVING COUNT(*) > 1) d JOIN public_masks m ON d.public_rowid = m.rowid ORDER BY m.url").fetchall(), ("url", "count")))
    write_csv(out_dir / "unmatched-released-keys.csv", ("row_id", "url", "cluster"), rows_for_csv(con.execute("SELECT r.row_id, r.id, r.cluster FROM released_public rp JOIN released r ON rp.released_rowid = r.row_id WHERE rp.public_rowid = -1 ORDER BY r.row_id").fetchall(), ("row_id", "url", "cluster")))
    released_url_counts = np.load(work / "released_url_counts.npy", mmap_mode="r")
    missing_output = []
    public_reader = con.sql("SELECT rowid, url, train_count, validation_count FROM public_masks").to_arrow_reader(1000000)
    for batch in public_reader:
        public_ids = batch.column(0).to_numpy(zero_copy_only=False)
        missing = released_url_counts[public_ids] == 0
        for index in np.flatnonzero(missing):
            missing_output.append({"url": batch.column(1)[int(index)].as_py(), "train_count": int(batch.column(2)[int(index)].as_py()), "validation_count": int(batch.column(3)[int(index)].as_py())})
    write_csv(out_dir / "missing-public-keys.csv", ("url", "train_count", "validation_count"), missing_output)
    write_csv(out_dir / "keep-discrepancies.csv", ("row_id", "url", "cluster", "keep", "cluster_size", "expected_keep"), rows_for_csv(con.execute("SELECT r.row_id, r.id, r.cluster, r.keep, c.n_all, CASE WHEN c.n_all = 1 THEN 1 ELSE 0 END FROM released r JOIN clusters c ON r.cluster = c.cluster WHERE r.keep <> CASE WHEN c.n_all = 1 THEN 1 ELSE 0 END ORDER BY r.row_id").fetchall(), ("row_id", "url", "cluster", "keep", "cluster_size", "expected_keep")))
    write_csv(out_dir / "url-divergences.csv", ("url", "total", "keep0", "multi_membership"), rows_for_csv(con.execute("SELECT url, total, keep0, multi_membership FROM url_stats WHERE keep0 <> multi_membership ORDER BY url").fetchall(), ("url", "total", "keep0", "multi_membership")))

    metrics = {
        "TT": con.execute("SELECT SUM(n_train) FROM composition WHERE n_train >= 2").fetchone()[0] or 0,
        "EE": con.execute("SELECT SUM(n_validation) FROM composition WHERE n_validation >= 2").fetchone()[0] or 0,
        "ET": con.execute("SELECT SUM(n_validation) FROM composition WHERE n_validation >= 1 AND n_train >= 1").fetchone()[0] or 0,
    }
    denominators = {"TT": SPLIT_SIZES["train"], "EE": SPLIT_SIZES["validation"], "ET": SPLIT_SIZES["validation"]}
    duplication_rows = [
        {"arm": "validation", "metric": metric, "numerator": numerator, "denominator": denominators[metric], "unrounded_ratio": str(Decimal(numerator) / Decimal(denominators[metric]))}
        for metric, numerator in metrics.items()
    ]
    write_csv(out_dir / "derived-duplication.csv", ("arm", "metric", "numerator", "denominator", "unrounded_ratio"), duplication_rows)
    removals = {
        "A": con.execute("SELECT SUM(CASE WHEN n_validation > 0 THEN n_train ELSE GREATEST(n_train - 1, 0) END) FROM composition").fetchone()[0] or 0,
        "B": con.execute("SELECT SUM(GREATEST(n_train - 1, 0)) FROM composition").fetchone()[0] or 0,
        "S": con.execute("SELECT SUM(n_train) FROM composition WHERE n_all >= 2").fetchone()[0] or 0,
    }
    removal_rows = [
        {"arm": "validation", "rule": rule, "removals": count, "retained": SPLIT_SIZES["train"] - count}
        for rule, count in removals.items()
    ]
    write_csv(out_dir / "derived-removals.csv", ("arm", "rule", "removals", "retained"), removal_rows)

    pair_clusters = con.execute("SELECT COUNT(*) FROM clusters WHERE n_all = 2").fetchone()[0]
    multi_clusters = con.execute("SELECT COUNT(*) FROM clusters WHERE n_all >= 2").fetchone()[0]
    facts = {
        "pair_clusters": pair_clusters,
        "multi_clusters": multi_clusters,
        "pair_majority": pair_clusters > multi_clusters / 2,
        "clusters_over_5000": con.execute("SELECT COUNT(*) FROM clusters WHERE n_all > 5000").fetchone()[0],
        "clusters_size_5000": con.execute("SELECT COUNT(*) FROM clusters WHERE n_all = 5000").fetchone()[0],
        "largest_cluster_size": con.execute("SELECT MAX(n_all) FROM clusters").fetchone()[0],
        "singleton_documents": con.execute("SELECT SUM(n_all) FROM clusters WHERE n_all = 1").fetchone()[0],
        "multi_cluster_documents": con.execute("SELECT SUM(n_all) FROM clusters WHERE n_all >= 2").fetchone()[0],
    }
    write_json(out_dir / "cluster-facts.json", facts)

    histogram = {int(row["cluster_size"]): int(row["cluster_count"]) for row in read_csv(out_dir / "cluster-histogram.csv")}
    expectation = random_split_ee(histogram, identity["physical_rows"], SPLIT_SIZES["validation"])
    ratios = expectation.pop("no_train_partner_ratios")
    expectation["expected_numerator"] = str(expectation["expected_numerator"])
    expectation["probability"] = str(expectation["probability"])
    expectation["formula"] = "E[P_EE]=(1/N)*sum_s s*n_s*(1-C(T,s-1)/C(N-1,s-1))"
    expectation["evaluation"] = "uniform fixed-size validation split; secondary random-split check, distinct from observed EE"
    write_json(out_dir / "random-split-ee.json", expectation)
    write_csv(out_dir / "random-split-ratios.csv", ("cluster_size", "no_train_partner_ratio"), ({"cluster_size": size, "no_train_partner_ratio": str(ratio)} for size, ratio in sorted(ratios.items())))

    eligible = [dict(zip(("url", "total", "keep0", "multi_membership"), row)) for row in con.execute("SELECT url, total, keep0, multi_membership FROM url_stats WHERE keep0 = total").fetchall()]
    ranked_urls = rank_all_duplicate_urls(eligible)[:20]
    stats_by_url = {row["url"]: row for row in eligible}
    top_rows = []
    for rank, url in enumerate(ranked_urls, start=1):
        row = stats_by_url[url]
        top_rows.append({
            "rank": rank,
            "url": url,
            "total": row["total"],
            "keep0": row["keep0"],
            "frac_dups": str(Decimal(row["keep0"]) / Decimal(row["total"])),
            "multi_membership": row["multi_membership"],
            "membership_fraction": str(Decimal(row["multi_membership"]) / Decimal(row["total"])),
        })
    write_csv(out_dir / "table11-top20.csv", ("rank", "url", "total", "keep0", "frac_dups", "multi_membership", "membership_fraction"), top_rows)
    keep = dict(con.execute("SELECT 'keep0_multi', SUM(keep = 0) FROM released r JOIN clusters c ON r.cluster = c.cluster WHERE c.n_all >= 2 UNION ALL SELECT 'keep0_singleton', SUM(keep = 0) FROM released r JOIN clusters c ON r.cluster = c.cluster WHERE c.n_all = 1 UNION ALL SELECT 'keep1_multi', SUM(keep = 1) FROM released r JOIN clusters c ON r.cluster = c.cluster WHERE c.n_all >= 2 UNION ALL SELECT 'keep1_singleton', SUM(keep = 1) FROM released r JOIN clusters c ON r.cluster = c.cluster WHERE c.n_all = 1").fetchall())
    divergence_count = con.execute("SELECT COUNT(*) FROM url_stats WHERE keep0 <> multi_membership").fetchone()[0]
    write_json(out_dir / "derived-summary.json", {
        "physical_rows": row_offset,
        "unique_clusters": con.execute("SELECT COUNT(*) FROM clusters").fetchone()[0],
        "split_join": join_summary,
        "keep_agreement": keep,
        "keep_discrepancy_rows": con.execute("SELECT COUNT(*) FROM released r JOIN clusters c ON r.cluster = c.cluster WHERE r.keep <> CASE WHEN c.n_all = 1 THEN 1 ELSE 0 END").fetchone()[0],
        "url_divergence_count": divergence_count,
        "divergence_status": "KEEP_MEMBERSHIP_DIVERGENCE" if divergence_count else "KEEP_MEMBERSHIP_AGREE",
        "duplication": metrics,
        "removals": removals,
        "population": "released archive, all splits",
    })
    con.execute("CHECKPOINT")
    con.close()
    write_json(out_dir / "full-input-manifest.json", {
        "stage": f"Stage 2 full audit / {run_name(out_dir)}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "command": [sys.executable, *sys.argv],
        "python": sys.version,
        "platform": platform.platform(),
        "duckdb": duckdb.__version__,
        "pyarrow": pa.__version__,
        "split_source": "1,024 original allenai/c4 train JSON shards streamed under Amendment A1 plus full validation Parquet",
        "split_root_sha": SPLIT_ROOT_SHA,
        "split_sizes": SPLIT_SIZES,
        "inputs": split_receipts,
        "acquisition_manifest": "../split-acquisition-manifest.json",
        "derived_public_db": acquisition["derived_public_db"],
        "streamed_train_shards": len(acquisition["train_inputs"]),
        "streamed_train_bytes": sum(row["bytes"] for row in acquisition["train_inputs"]),
        "code_sha256": {
            "src/stage2_acquire.py": sha256(root / "src/stage2_acquire.py"),
            "src/stage2_audit.py": sha256(root / "src/stage2_audit.py"),
            "src/stage2_compare.py": sha256(root / "src/stage2_compare.py") if (root / "src/stage2_compare.py").exists() else "PENDING",
            "src/verify_stage2.py": sha256(root / "src/verify_stage2.py"),
        },
    })
    print(json.dumps({"rows": row_offset, "join": join_summary["status"], "duplication": metrics, "removals": removals, "table11_eligible": len(eligible)}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    run_full_audit(args.root, args.out_dir, resume=args.resume)


if __name__ == "__main__":
    main()
