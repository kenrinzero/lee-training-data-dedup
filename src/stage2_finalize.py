#!/usr/bin/env python3
import argparse
import csv
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from stage1_audit import run_name, sha256, write_json
from stage2_acquire import validate_receipt_set
from stage2_compare import companion_verdicts

COPY_OUTPUTS = (
    "input-manifest.json",
    "release-identity.json",
    "cluster-histogram.csv",
    "figure-counts.csv",
    "figure-verdicts.csv",
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
    "table2-verdicts.csv",
    "table13-verdicts.csv",
    "section5-verdicts.csv",
    "table11-verdicts.csv",
    "random-split-verdict.json",
    "convention-application.json",
    "comparison-summary.json",
)


def finalize(root, out_dir):
    root = Path(root)
    out_dir = Path(out_dir)
    run = run_name(out_dir)
    source = out_dir.parent.parent / "run-002"
    source_audit = source / "audit"
    out_dir.mkdir(parents=True, exist_ok=False)
    metadata_path = source / "train-source-metadata.json"
    acquisition_path = source / "split-acquisition-manifest.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    acquisition = json.loads(acquisition_path.read_text(encoding="utf-8"))
    receipt_stats = validate_receipt_set(metadata["files"], acquisition["train_inputs"])
    assert receipt_stats == {"shards": 1024, "bytes": 326778635540, "rows": 364868892}
    for name in COPY_OUTPUTS:
        shutil.copyfile(source_audit / name, out_dir / name)
    companion = companion_verdicts([
        {"rule": row["rule"], "derived_removals": row["derived_removals"]}
        for row in csv.DictReader((out_dir / "table13-verdicts.csv").open("r", encoding="utf-8", newline=""))
    ])
    arithmetic = json.loads((root / "planning/step0/arithmetic.json").read_text(encoding="utf-8"))
    derivations = {row["id"]: row for row in arithmetic["derivations"]}
    companion["step0_companions"] = {
        "c4_removal_ceiling": {
            "source": "planning/step0/arithmetic.json derivations.c4_removal_ceiling",
            "verdict": "CONTRADICTION",
            "robust_minimum_shortfall": derivations["c4_removal_ceiling"]["outputs"]["robust_minimum_shortfall"],
        },
        "fig1_bounds": {
            "source": "planning/step0/arithmetic.json derivations.fig1_bounds",
            "verdict": "CONSISTENT_INTERVAL",
            "train_removal_lower": derivations["fig1_bounds"]["outputs"]["train_removal_lower"],
            "train_removal_upper": derivations["fig1_bounds"]["outputs"]["train_removal_upper"],
        },
    }
    write_json(out_dir / "companion-verdicts.json", companion)
    custody = {
        "status": "PASS",
        "train_receipts": receipt_stats,
        "train_source_metadata": str(metadata_path),
        "train_source_metadata_sha256": sha256(metadata_path),
        "acquisition_manifest": str(acquisition_path),
        "acquisition_manifest_sha256": sha256(acquisition_path),
        "derived_public_db": acquisition["derived_public_db"],
        "validation_inputs": acquisition["validation_inputs"],
    }
    write_json(out_dir / "custody-verification.json", custody)
    full_manifest = json.loads((source_audit / "full-input-manifest.json").read_text(encoding="utf-8"))
    full_manifest.update({
        "stage": f"Stage 2 finalization / {run}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "acquisition_manifest": str(acquisition_path.resolve()),
        "acquisition_manifest_sha256": custody["acquisition_manifest_sha256"],
        "train_source_metadata": str(metadata_path.resolve()),
        "train_source_metadata_sha256": custody["train_source_metadata_sha256"],
        "work_db": str((source_audit / "work/c4.duckdb").resolve()),
        "code_sha256": {
            "src/stage2_acquire.py": sha256(root / "src/stage2_acquire.py"),
            "src/stage2_audit.py": sha256(root / "src/stage2_audit.py"),
            "src/stage2_compare.py": sha256(root / "src/stage2_compare.py"),
            "src/stage2_finalize.py": sha256(root / "src/stage2_finalize.py"),
            "src/verify_stage2.py": sha256(root / "src/verify_stage2.py"),
        },
    })
    write_json(out_dir / "full-input-manifest.json", full_manifest)
    print(json.dumps({"status": "FINALIZED", "custody": receipt_stats, "output": str(out_dir)}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    finalize(args.root, args.out_dir)


if __name__ == "__main__":
    main()
