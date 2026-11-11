#!/usr/bin/env python3
import argparse
import csv
import hashlib
import io
import json
import platform
import sys
import tarfile
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, getcontext
from pathlib import Path

import pyarrow
import pyarrow.parquet as pq

getcontext().prec = 50

SPLIT_SIZES = {"train": 2926536, "validation": 163597, "test": 162274}
SPLITS = ("train", "validation", "test")
REVISION = "06bfe584d8193cf58f79c6354ecc2a2b94a7deea"
BIN_LABELS = ("1", "2", "3", "4", "5", "[6, 10)", "[11, 20)", "[21, 50)", "[51, 500)", "[501, 5000)", "[5001, ∞)")
EDGE_SIZES = (10, 20, 50, 500, 5000)
SHARD_SIZES = {
    "train-00000-of-00019.parquet": 292662109,
    "train-00001-of-00019.parquet": 293008855,
    "train-00002-of-00019.parquet": 292921438,
    "train-00003-of-00019.parquet": 293164247,
    "train-00004-of-00019.parquet": 291157463,
    "train-00005-of-00019.parquet": 293404780,
    "train-00006-of-00019.parquet": 290770171,
    "train-00007-of-00019.parquet": 294187640,
    "train-00008-of-00019.parquet": 293810591,
    "train-00009-of-00019.parquet": 292945249,
    "train-00010-of-00019.parquet": 293482891,
    "train-00011-of-00019.parquet": 292662959,
    "train-00012-of-00019.parquet": 292706728,
    "train-00013-of-00019.parquet": 291886673,
    "train-00014-of-00019.parquet": 293363797,
    "train-00015-of-00019.parquet": 292255533,
    "train-00016-of-00019.parquet": 292266499,
    "train-00017-of-00019.parquet": 292483305,
    "train-00018-of-00019.parquet": 293064118,
    "validation-00000-of-00002.parquet": 155816478,
    "validation-00001-of-00002.parquet": 156517783,
    "test-00000-of-00002.parquet": 154017168,
    "test-00001-of-00002.parquet": 155275430,
}
EXPECTED_SHA256 = {
    "wiki40b.tar.gz": "db1df97ef3268e0bdf36c15b66c4f71e4b465c42864f7c009104bb96bf8f8a32",
    "train-00000-of-00019.parquet": "c78d07958f4c7a463cc69f849df3fa023ee4a8584581458fdf207cd245499a62",
    "train-00001-of-00019.parquet": "aeee305a291d62347342f0f9b550989d1e7b967f3cf5e1a01115ea8031f05288",
    "train-00002-of-00019.parquet": "ef47da9985e8a929e27dfc94d15529d84dfb56e822fa6e146e92cae29e71ed4c",
    "train-00003-of-00019.parquet": "30f3486d4f006c5e4ce50a92f1873b6125434f2883dca25bbabfa16073210115",
    "train-00004-of-00019.parquet": "8594a95184849ab5b7dd75e494060e1b0d5e67e1e3f8bf486c410cf7a2910a9f",
    "train-00005-of-00019.parquet": "5a177308bc924a1a9f69d7721a3f1c937b5ffe03307edc1cd436ba6691a01ea6",
    "train-00006-of-00019.parquet": "7cee50578a518e5652a578598bda09cb4c06c940a9c72494b97e5cd212585659",
    "train-00007-of-00019.parquet": "f32be8857f82d8d499139b885a8cf7be52dfe48194650ec66cee2b340abeb348",
    "train-00008-of-00019.parquet": "400378065d969322745173e1deca6a1aae6853fd8411ff73e11ba22e83717296",
    "train-00009-of-00019.parquet": "2dc4bf7fd00ef1a9d8fb36a232190c155e4da9d9815e4e27619bd6c5c1093342",
    "train-00010-of-00019.parquet": "03fb7f5745d7a73bb5c0cafa4d7e69f9b5372a0e39ff70d16f2ec69dd85139ee",
    "train-00011-of-00019.parquet": "d15359299627a545d6f16a1d72fa3f5cd7211e55cc8d16d440f9d1bef68e6559",
    "train-00012-of-00019.parquet": "e39b4b0216e3809cf8b4fb4e0ffa57e44eba8b1f004e617a824a3220f7dc13eb",
    "train-00013-of-00019.parquet": "011253f235a2edc50ad6d4a2e1927e0659a56a80ec2248cb9401efcdf5da5819",
    "train-00014-of-00019.parquet": "4b3938989329b8b36f0ffc3bebbb9651cb016393273399a035cd79d300821c10",
    "train-00015-of-00019.parquet": "d520a0d971da45ee1bd848186323418f6e04d84d22a0ae7110bb7ae8d05cbae1",
    "train-00016-of-00019.parquet": "e590518067af825b4c178876c7f3fae55f51b913c9f86a78759e6d843e9e2a9d",
    "train-00017-of-00019.parquet": "a2ad8596b02585d336a4ecab77d894616f3151715d19fdba6972c101633fb60b",
    "train-00018-of-00019.parquet": "b67c2e9a970a4fc0053224af5a08e586ba09e769ef1ea7c411e2f3dcba64b06a",
    "validation-00000-of-00002.parquet": "9021e6e064e10fbfb972ab6e2a3bb07a7074b94448b5782da40d44a1c5ee7130",
    "validation-00001-of-00002.parquet": "fccd1ba95bbac574fe4d4f931783a96e2cd80e94b1f2a2e6ffde3bc46c2418a0",
    "test-00000-of-00002.parquet": "402aff678586bc2c9b8a0678d10557dddeb77d4c73fae774a6196ed39acdbd23",
    "test-00001-of-00002.parquet": "500c603bf6b1f73b88946947bb24a8b1413586d9090275d80d4fa8b14d0c92b4",
}


def round_half_up(value, digits):
    return value.quantize(Decimal(1).scaleb(-digits), rounding="ROUND_HALF_UP")


def run_name(out_dir):
    return Path(out_dir).parent.name


def evaluation_count(row, arm):
    if arm == "validation+test":
        return row["n_validation"] + row["n_test"]
    return row[f"n_{arm}"]


def compute_duplication(rows, arm, split_sizes):
    tt = ee = et = 0
    for row in rows:
        n_train = row["n_train"]
        n_eval = evaluation_count(row, arm)
        if n_train >= 2:
            tt += n_train
        if n_eval >= 2:
            ee += n_eval
        if n_eval >= 1 and n_train >= 1:
            et += n_eval
    return {
        "TT": {"numerator": tt, "denominator": split_sizes["train"]},
        "EE": {"numerator": ee, "denominator": split_sizes[arm] if arm != "validation+test" else split_sizes["validation"] + split_sizes["test"]},
        "ET": {"numerator": et, "denominator": split_sizes[arm] if arm != "validation+test" else split_sizes["validation"] + split_sizes["test"]},
    }


def compute_removals(rows, arm, train_size):
    removals = {"A": 0, "B": 0, "S": 0}
    for row in rows:
        n_train = row["n_train"]
        n_eval = evaluation_count(row, arm)
        removals["A"] += n_train if n_eval > 0 else max(0, n_train - 1)
        removals["B"] += max(0, n_train - 1)
        if row["n_all"] >= 2:
            removals["S"] += n_train
    return {
        rule: {"removals": count, "retained": train_size - count}
        for rule, count in removals.items()
    }


def figure_counts(histogram, convention):
    counts = [histogram.get(size, 0) for size in range(1, 6)]
    ranges = ((6, 10), (11, 20), (21, 50), (51, 500), (501, 5000))
    for low, high in ranges:
        count = sum(histogram.get(size, 0) for size in range(low, high))
        if convention == "low":
            count += histogram.get(high, 0)
        elif convention == "high" and low > 6:
            count += histogram.get(low - 1, 0)
        counts.append(count)
    final = sum(count for size, count in histogram.items() if size >= 5001)
    if convention == "high":
        final += histogram.get(5000, 0)
    counts.append(final)
    if convention not in {"dropped", "low", "high"}:
        raise ValueError(f"unknown convention: {convention}")
    return counts


def keep_agreement(rows):
    result = {"keep0_multi": 0, "keep0_singleton": 0, "keep1_multi": 0, "keep1_singleton": 0}
    for row in rows:
        membership = "singleton" if row["n_all"] == 1 else "multi"
        result[f"keep0_{membership}"] += row["keep0"]
        result[f"keep1_{membership}"] += row["keep1"]
    return result


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_text(path, text):
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def write_json(path, value):
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def write_csv(path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def receipt(path, url, expected_bytes, rights, expected_sha256):
    stat = path.stat()
    assert stat.st_size == expected_bytes, f"unexpected byte count for {path}: {stat.st_size} != {expected_bytes}"
    actual_sha256 = sha256(path)
    assert actual_sha256 == expected_sha256, f"unexpected SHA-256 for {path}: {actual_sha256} != {expected_sha256}"
    return {
        "local_path": str(path.resolve()),
        "url": url,
        "bytes": stat.st_size,
        "expected_bytes": expected_bytes,
        "sha256": actual_sha256,
        "expected_sha256": expected_sha256,
        "acquired_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        "rights": rights,
    }


def load_public_keys(files):
    public = {}
    physical_counts = {split: 0 for split in SPLITS}
    parquet_receipts = []
    for split, path in files:
        split_index = SPLITS.index(split)
        parquet_file = pq.ParquetFile(path)
        file_count = 0
        for batch in parquet_file.iter_batches(columns=["wikidata_id"], batch_size=100000):
            for key in batch.column(0).to_pylist():
                if not isinstance(key, str) or not key:
                    raise ValueError(f"invalid wikidata_id in {path}")
                physical_counts[split] += 1
                file_count += 1
                public.setdefault(key, [0, 0, 0])[split_index] += 1
        parquet_receipts.append({
            "path": str(path),
            "rows": file_count,
            "metadata_rows": parquet_file.metadata.num_rows,
            "columns": parquet_file.schema_arrow.names,
        })
        assert file_count == parquet_file.metadata.num_rows
    assert physical_counts == SPLIT_SIZES, f"public split counts differ: {physical_counts}"
    return public, physical_counts, parquet_receipts


def run_audit(root, out_dir):
    root = Path(root).resolve()
    out_dir = Path(out_dir)
    archive = root / "data/raw/clusters/wiki40b.tar.gz"
    split_files = [
        (split, root / "data/raw/wiki40b/en" / name)
        for split, name in (
            (name.split("-", 1)[0], name)
            for name in sorted(SHARD_SIZES)
        )
    ]
    rights = "Source terms are not established as unrestricted redistribution rights; keep raw inputs local."
    inputs = [receipt(
        archive,
        "https://storage.googleapis.com/gresearch/data_deduplication/wiki40b.tar.gz",
        26773963,
        rights,
        EXPECTED_SHA256[archive.name],
    )]
    for _, path in split_files:
        inputs.append(receipt(
            path,
            f"https://huggingface.co/datasets/google/wiki40b/resolve/{REVISION}/en/{path.name}?download=true",
            SHARD_SIZES[path.name],
            rights,
            EXPECTED_SHA256[path.name],
        ))
    out_dir.mkdir(parents=True, exist_ok=False)

    rows = []
    cluster_sizes = Counter()
    cluster_keep = {}
    document_counts = Counter()
    with tarfile.open(archive, "r:gz") as tar:
        members = [member for member in tar.getmembers() if member.isfile()]
        assert len(members) == 1, f"unexpected archive members: {members}"
        member = members[0]
        assert member.name == "wiki40b.csv", f"unexpected member: {member.name}"
        raw = tar.extractfile(member)
        assert raw is not None
        with io.TextIOWrapper(raw, encoding="utf-8", newline="") as text:
            reader = csv.reader(text, strict=True)
            header = next(reader)
            assert header == ["id", "keep", "cluster"], f"unexpected header: {header}"
            for row_number, values in enumerate(reader, start=1):
                if len(values) != 3 or any(value == "" for value in values):
                    raise ValueError(f"malformed row {row_number}: {values}")
                document_id, keep_text, cluster_id = values
                if keep_text not in {"0", "1"}:
                    raise ValueError(f"invalid keep at row {row_number}: {keep_text}")
                keep = int(keep_text)
                rows.append((document_id, keep, cluster_id))
                document_counts[document_id] += 1
                cluster_sizes[cluster_id] += 1
                cluster_keep.setdefault(cluster_id, [0, 0])[keep] += 1
            decompressed_bytes = raw.tell()
    assert decompressed_bytes == member.size

    public, physical_counts, parquet_receipts = load_public_keys(split_files)
    cluster_splits = {cluster_id: [0, 0, 0] for cluster_id in cluster_sizes}
    join_discrepancies = []
    unmatched_released_rows = 0
    cross_split_released_rows = 0
    for row_number, (document_id, _, cluster_id) in enumerate(rows, start=1):
        counts = public.get(document_id)
        if counts is None:
            unmatched_released_rows += 1
            join_discrepancies.append({"type": "UNMATCHED_RELEASED_KEY", "row_number": row_number, "document_id": document_id, "cluster_id": cluster_id, "detail": ""})
            continue
        present = [index for index, count in enumerate(counts) if count > 0]
        if len(present) != 1:
            cross_split_released_rows += 1
            join_discrepancies.append({"type": "CROSS_SPLIT_KEY", "row_number": row_number, "document_id": document_id, "cluster_id": cluster_id, "detail": str(counts)})
            continue
        cluster_splits[cluster_id][present[0]] += 1

    duplicate_public = []
    cross_split_public = []
    duplicate_public_rows = 0
    for key, counts in public.items():
        for split, count in zip(SPLITS, counts):
            if count > 1:
                duplicate_public.append({"split": split, "document_id": key, "count": count})
                duplicate_public_rows += count - 1
        if sum(count > 0 for count in counts) > 1:
            cross_split_public.append({"document_id": key, "train": counts[0], "validation": counts[1], "test": counts[2]})
    duplicate_released = [
        {"document_id": key, "count": count}
        for key, count in document_counts.items() if count > 1
    ]
    missing_public = []
    missing_public_rows = 0
    for key, counts in public.items():
        if key not in document_counts:
            missing_public.append({"document_id": key, "train": counts[0], "validation": counts[1], "test": counts[2]})
            missing_public_rows += sum(counts)

    population_balance = {
        split: sum(counts[index] for counts in cluster_splits.values())
        for index, split in enumerate(SPLITS)
    }
    join_complete = not any((unmatched_released_rows, cross_split_released_rows, missing_public_rows)) and population_balance == SPLIT_SIZES

    def compositions():
        for cluster_id, n_all in cluster_sizes.items():
            keep0, keep1 = cluster_keep[cluster_id]
            n_train, n_validation, n_test = cluster_splits[cluster_id]
            yield {
                "cluster_id": cluster_id,
                "n_all": n_all,
                "keep0": keep0,
                "keep1": keep1,
                "n_train": n_train,
                "n_validation": n_validation,
                "n_test": n_test,
            }

    composition_fields = ("cluster_id", "n_all", "keep0", "keep1", "n_train", "n_validation", "n_test")
    write_csv(out_dir / "cluster-composition.csv", composition_fields, compositions())
    keep_discrepancies = []
    for row_number, (document_id, keep, cluster_id) in enumerate(rows, start=1):
        expected_keep = 1 if cluster_sizes[cluster_id] == 1 else 0
        if keep != expected_keep:
            keep_discrepancies.append({"row_number": row_number, "document_id": document_id, "cluster_id": cluster_id, "keep": keep, "cluster_size": cluster_sizes[cluster_id], "expected_keep": expected_keep})
    write_csv(out_dir / "keep-discrepancies.csv", ("row_number", "document_id", "cluster_id", "keep", "cluster_size", "expected_keep"), keep_discrepancies)
    write_csv(out_dir / "join-discrepancies.csv", ("type", "row_number", "document_id", "cluster_id", "detail"), join_discrepancies)
    write_csv(out_dir / "duplicate-public-keys.csv", ("split", "document_id", "count"), duplicate_public)
    write_csv(out_dir / "cross-split-public-keys.csv", ("document_id", "train", "validation", "test"), cross_split_public)
    write_csv(out_dir / "duplicate-released-ids.csv", ("document_id", "count"), duplicate_released)
    write_csv(out_dir / "missing-public-keys.csv", ("document_id", "train", "validation", "test"), missing_public)

    histogram = dict(sorted(cluster_sizes.items(), key=lambda item: int(item[0])))
    size_histogram = Counter(cluster_sizes.values())
    write_csv(
        out_dir / "cluster-histogram.csv",
        ("cluster_size", "cluster_count", "document_count"),
        ({"cluster_size": size, "cluster_count": count, "document_count": size * count} for size, count in sorted(size_histogram.items())),
    )
    write_csv(
        out_dir / "edge-sizes.csv",
        ("cluster_size", "cluster_count", "document_count"),
        ({"cluster_size": size, "cluster_count": size_histogram.get(size, 0), "document_count": size * size_histogram.get(size, 0)} for size in EDGE_SIZES),
    )
    figure_rows = []
    for convention in ("dropped", "low", "high"):
        counts = figure_counts(size_histogram, convention)
        for bin_index, (label, count) in enumerate(zip(BIN_LABELS, counts), start=1):
            figure_rows.append({"convention": convention, "bin_index": bin_index, "bin_label": label, "cluster_count": count})
    write_csv(out_dir / "figure-counts.csv", ("convention", "bin_index", "bin_label", "cluster_count"), figure_rows)

    duplication_rows = []
    for arm in ("validation", "test"):
        metrics = compute_duplication(compositions(), arm, SPLIT_SIZES)
        for metric in ("TT", "EE", "ET"):
            numerator = metrics[metric]["numerator"]
            denominator = metrics[metric]["denominator"]
            duplication_rows.append({"arm": arm, "metric": metric, "numerator": numerator, "denominator": denominator, "unrounded_ratio": str(Decimal(numerator) / Decimal(denominator))})
    write_csv(out_dir / "derived-duplication.csv", ("arm", "metric", "numerator", "denominator", "unrounded_ratio"), duplication_rows)
    removal_rows = []
    for arm in ("validation", "test", "validation+test"):
        metrics = compute_removals(compositions(), arm, SPLIT_SIZES["train"])
        for rule in ("A", "B", "S"):
            removal_rows.append({"arm": arm, "rule": rule, "removals": metrics[rule]["removals"], "retained": metrics[rule]["retained"]})
    write_csv(out_dir / "derived-removals.csv", ("arm", "rule", "removals", "retained"), removal_rows)

    summary = {
        "physical_rows": len(rows),
        "unique_ids": len(document_counts),
        "unique_clusters": len(cluster_sizes),
        "duplicate_released_ids": len(duplicate_released),
        "duplicate_released_rows": sum(item["count"] - 1 for item in duplicate_released),
        "malformed_rows": 0,
        "empty_field_rows": 0,
        "row_order": "physical released CSV order; one-based data row numbers in diagnostics",
        "population": "released archive, all splits",
        "keep_agreement": keep_agreement(compositions()),
        "keep_discrepancy_rows": len(keep_discrepancies),
        "split_join": {
            "status": "COMPLETE" if join_complete else "INDETERMINATE_JOIN",
            "public_physical_counts": physical_counts,
            "public_unique_keys": len(public),
            "duplicate_public_keys": len(duplicate_public),
            "duplicate_public_rows": duplicate_public_rows,
            "cross_split_public_keys": len(cross_split_public),
            "unmatched_released_rows": unmatched_released_rows,
            "cross_split_released_rows": cross_split_released_rows,
            "missing_public_keys": len(missing_public),
            "missing_public_rows": missing_public_rows,
            "population_balance": population_balance,
            "expected_population_balance": SPLIT_SIZES,
            "estimand": "released-physical-row weighted",
        },
    }
    write_json(out_dir / "derived-summary.json", summary)
    manifest = {
        "stage": f"Stage 1 / {run_name(out_dir)}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "command": [sys.executable, *sys.argv],
        "python": sys.version,
        "platform": platform.platform(),
        "pyarrow": pyarrow.__version__,
        "csv_parser": "Python csv.reader(strict=True), UTF-8, exact physical rows",
        "archive": {"member": member.name, "decompressed_bytes": decompressed_bytes, "header": header},
        "split_revision": REVISION,
        "split_sizes": SPLIT_SIZES,
        "inputs": inputs,
        "parquet": parquet_receipts,
        "code_sha256": {
            "src/stage1_audit.py": sha256(root / "src/stage1_audit.py"),
            "src/stage1_compare.py": sha256(root / "src/stage1_compare.py"),
        },
    }
    write_json(out_dir / "input-manifest.json", manifest)
    print(json.dumps({"rows": len(rows), "clusters": len(cluster_sizes), "join": summary["split_join"]["status"], "output": str(out_dir)}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    run_audit(args.root, args.out_dir)


if __name__ == "__main__":
    main()
