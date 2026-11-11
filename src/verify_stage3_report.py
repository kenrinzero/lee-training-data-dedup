#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path

from stage1_audit import sha256
from stage1_report import superseded_run


def check_output_hashes(run_dir, manifest):
    run_dir = Path(run_dir)
    for name, receipt in manifest["outputs"].items():
        path = run_dir / name
        assert path.is_file(), f"missing output: {name}"
        assert path.stat().st_size == receipt["bytes"], f"output byte count changed: {name}"
        assert sha256(path) == receipt["sha256"], f"output hash changed: {name}"


def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    report_path = args.run_dir / "report.md"
    assert report_path.is_file(), f"missing report: {report_path}"
    before = report_path.read_bytes()
    report = before.decode("utf-8")
    assert str(args.root.resolve()) not in report
    for required in (
        "NOT_EXECUTABLE_INPUT",
        "CONDITIONAL_RELEASE_POPULATION",
        "not a verified public train",
        "keep=0 / # Total",
        "total >= 10",
        "CEILING_COMPATIBLE` is only a ceiling result, not a train-size match",
    ):
        assert required in report, f"missing reader qualification: {required}"
    for row in read_csv(args.run_dir / "table2-verdicts.csv"):
        assert row["verdict"] in report
        assert row["printed_value"] in report
    for row in read_csv(args.run_dir / "table13-verdicts.csv"):
        for field in ("basis", "derived_removals", "derived_retained", "derived_original_rounded", "derived_retained_rounded", "original_verdict", "neardup_verdict", "direct_train_removal_verdict"):
            assert str(row[field]) in report, f"missing Table 13 {field}={row[field]}"
    for row in read_csv(args.run_dir / "table11-verdicts.csv"):
        for field in ("derived_total", "total_verdict", "frac_verdict"):
            assert str(row[field]) in report, f"missing Table 11 {field}={row[field]}"
    for row in read_csv(args.run_dir / "figure-verdicts.csv"):
        assert row["derived_count"] in report
        assert row["verdict"] in report
    companion = json.loads((args.run_dir / "companion-verdicts.json").read_text(encoding="utf-8"))
    assert companion["split_free_ceiling"]["verdict"] in report
    assert companion["section5_rounding"]["printed_table2"] in report
    assert companion["section5_rounding"]["printed_section5_3"] in report
    assert companion["tokens"]["original"] in report
    manifest = json.loads((args.run_dir / "run-manifest.json").read_text(encoding="utf-8"))
    assert manifest["stage"] == f"Stage 3 / {args.run_dir.parent.name}"
    assert manifest["supersedes"] == superseded_run(args.run_dir.parent.name)
    check_output_hashes(args.run_dir, manifest)
    for name, expected_hash in manifest["code_sha256"].items():
        if name == "verify_stage3_report.py":
            continue
        assert sha256(args.root / "src" / name) == expected_hash, f"code hash changed: {name}"
    assert b"\r" not in before
    assert report_path.read_bytes() == before
    print(f"PASS: Stage 3 report, reader qualifications, outputs and code receipts verified without modification: {report_path}")


if __name__ == "__main__":
    main()
