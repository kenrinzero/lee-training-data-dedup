#!/usr/bin/env python3
import argparse
import csv
import io
import json
import platform
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pyarrow

from stage1_audit import BIN_LABELS, figure_counts, receipt, run_name, sha256, write_csv, write_json

EXPECTED_ROWS = 365233500
EXPECTED_BYTES = 13872073006
EXPECTED_SHA256 = "5b73b507b3aa08c7dca5d5da55afe27babe6a4ddde40f4107ad1e88e82986723"
CLUSTER_URL = "https://storage.googleapis.com/gresearch/data_deduplication/c4.tar.gz"
IDENTITY_OUTPUTS = (
    "input-manifest.json",
    "release-identity.json",
    "cluster-histogram.csv",
    "figure-counts.csv",
    "figure-verdicts.csv",
)


def ensure_fresh_identity(out_dir):
    out_dir = Path(out_dir)
    existing = [name for name in IDENTITY_OUTPUTS if (out_dir / name).exists()]
    if existing:
        raise FileExistsError(f"refusing to overwrite Stage 2 identity outputs in {out_dir}: {existing}")


def ensure_cluster_capacity(counts, cluster_id):
    if cluster_id < len(counts):
        return counts
    expanded = np.zeros(max(cluster_id + 1, len(counts) * 2), dtype=counts.dtype)
    expanded[:len(counts)] = counts
    return expanded


def evaluate_release_identity(row_count, match_counts):
    matching = sorted(name for name, count in match_counts.items() if count == 11)
    rows_match = row_count == EXPECTED_ROWS
    return {
        "status": "IDENTITY_HOLD" if rows_match and matching else "KILL_RELEASE_IDENTITY",
        "physical_rows": row_count,
        "expected_rows": EXPECTED_ROWS,
        "row_count_matches": rows_match,
        "figure_match_counts": dict(match_counts),
        "matching_conventions": matching,
    }


def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def run_identity(root, out_dir):
    root = Path(root).resolve()
    out_dir = Path(out_dir)
    ensure_fresh_identity(out_dir)
    archive = root / "data/raw/clusters/c4.tar.gz"
    source_receipt = receipt(
        archive,
        CLUSTER_URL,
        EXPECTED_BYTES,
        "Cluster redistribution rights are unresolved; keep raw inputs local.",
        EXPECTED_SHA256,
    )
    out_dir.mkdir(parents=True, exist_ok=False)
    stage1_lock = json.loads((root / "results/stage1/run-004/audit/convention-lock.json").read_text(encoding="utf-8"))
    assert stage1_lock["primary"] == "dropped" and stage1_lock["locked_candidate_set"] == ["dropped"]

    physical_rows = 0
    maximum_cluster = -1
    counts = np.zeros(1 << 20, dtype=np.uint32)
    with tarfile.open(archive, "r:gz") as tar:
        members = [member for member in tar.getmembers() if member.isfile()]
        assert len(members) == 1 and members[0].name == "c4.csv", f"unexpected archive members: {members}"
        member = members[0]
        raw = tar.extractfile(member)
        assert raw is not None
        with io.TextIOWrapper(raw, encoding="utf-8", newline="") as text:
            reader = csv.reader(text, strict=True)
            header = next(reader)
            assert header == ["id", "keep", "cluster"], f"unexpected header: {header}"
            for row_number, values in enumerate(reader, start=1):
                if len(values) != 3 or any(value == "" for value in values):
                    raise ValueError(f"malformed row {row_number}: {values}")
                _, keep, cluster_text = values
                if keep not in {"0", "1"}:
                    raise ValueError(f"invalid keep at row {row_number}: {keep}")
                cluster_id = int(cluster_text)
                if cluster_id < 0:
                    raise ValueError(f"negative cluster at row {row_number}: {cluster_id}")
                counts = ensure_cluster_capacity(counts, cluster_id)
                counts[cluster_id] += 1
                physical_rows += 1
                if cluster_id > maximum_cluster:
                    maximum_cluster = cluster_id
            decompressed_bytes = raw.tell()
    assert decompressed_bytes == member.size
    counts = counts[:maximum_cluster + 1]
    histogram_array = np.bincount(counts)
    histogram = {int(size): int(count) for size, count in enumerate(histogram_array) if count}
    unique_clusters = int(np.count_nonzero(counts))

    write_csv(
        out_dir / "cluster-histogram.csv",
        ("cluster_size", "cluster_count", "document_count"),
        ({"cluster_size": size, "cluster_count": count, "document_count": size * count} for size, count in sorted(histogram.items())),
    )
    printed_bars = [row for row in read_csv(root / "paper/targets/figure-bars.csv") if row["figure"] == "Figure 1"]
    figure_rows = []
    verdict_rows = []
    match_counts = {}
    for convention in ("dropped", "low", "high"):
        derived = figure_counts(histogram, convention)
        match_counts[convention] = 0
        for bin_index, (label, count, printed) in enumerate(zip(BIN_LABELS, derived, printed_bars), start=1):
            assert label == printed["bin_label"]
            verdict = "MATCH" if count == int(printed["printed_count"]) else "MISMATCH"
            match_counts[convention] += verdict == "MATCH"
            figure_rows.append({"convention": convention, "bin_index": bin_index, "bin_label": label, "cluster_count": count})
            verdict_rows.append({"convention": convention, "bin_index": bin_index, "bin_label": label, "printed_count": printed["printed_count"], "derived_count": count, "verdict": verdict})
    write_csv(out_dir / "figure-counts.csv", ("convention", "bin_index", "bin_label", "cluster_count"), figure_rows)
    write_csv(out_dir / "figure-verdicts.csv", ("convention", "bin_index", "bin_label", "printed_count", "derived_count", "verdict"), verdict_rows)
    identity = evaluate_release_identity(physical_rows, match_counts)
    identity.update({
        "unique_clusters": unique_clusters,
        "largest_cluster_size": maximum_cluster and int(counts.max()),
        "stage1_primary": stage1_lock["primary"],
        "population": "released archive, all splits",
        "decompressed_bytes": decompressed_bytes,
        "header": header,
        "row_order": "physical released CSV order; one-based data row numbers",
        "malformed_rows": 0,
        "empty_field_rows": 0,
    })
    write_json(out_dir / "release-identity.json", identity)
    write_json(out_dir / "input-manifest.json", {
        "stage": f"Stage 2 identity / {run_name(out_dir)}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "command": [sys.executable, *sys.argv],
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "pyarrow": pyarrow.__version__,
        "csv_parser": "Python csv.reader(strict=True), UTF-8, streamed tar member without full extraction",
        "archive": {"member": member.name, "decompressed_bytes": decompressed_bytes, "header": header},
        "inputs": [source_receipt],
        "stage1_lock": stage1_lock,
        "code_sha256": {
            "src/stage1_audit.py": sha256(root / "src/stage1_audit.py"),
            "src/stage2_identity.py": sha256(root / "src/stage2_identity.py"),
            "src/verify_stage2.py": sha256(root / "src/verify_stage2.py"),
        },
    })
    print(json.dumps(identity, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    run_identity(args.root, args.out_dir)


if __name__ == "__main__":
    main()
