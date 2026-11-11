#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
from pathlib import Path

try:
    from stage2_report import render_report
except ImportError as exc:
    raise SystemExit(f"FAIL: Stage 2 report generator is missing: {exc}")


def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
    identity = json.loads((args.run_dir / "release-identity.json").read_text(encoding="utf-8"))
    assert identity["status"] in report
    for row in read_csv(args.run_dir / "figure-verdicts.csv"):
        assert row["derived_count"] in report
    if identity["status"] == "IDENTITY_HOLD":
        for name, fields in {
            "table2-verdicts.csv": ("derived_numerator", "rounded_percent", "verdict"),
            "table13-verdicts.csv": ("derived_removals", "derived_retained_rounded", "neardup_verdict"),
            "section5-verdicts.csv": ("derived_value", "verdict"),
            "table11-verdicts.csv": ("derived_total", "total_verdict", "frac_verdict"),
        }.items():
            for row in read_csv(args.run_dir / name):
                for field in fields:
                    assert str(row[field]) in report, f"missing {name} {field}={row[field]}"
        random_verdict = json.loads((args.run_dir / "random-split-verdict.json").read_text(encoding="utf-8"))
        assert random_verdict["rounded_percent"] in report
        assert "SOURCE_MISSING" in report
        assert "not observed author deletions" in report
        companion = json.loads((args.run_dir / "companion-verdicts.json").read_text(encoding="utf-8"))
        assert companion["section5_rounding"]["printed_table2"] in report
        assert companion["section5_rounding"]["printed_section5_3"] in report
        for rule in ("A", "B", "S"):
            assert companion["printed_difference_interval"][rule] in report
        assert companion["tokens"]["original"] in report
        assert companion["tokens"]["neardup"] in report
        assert "source-native host-level estimand" in report
        assert "not** a reconstruction of the printed host-like frequency ranking" in report
        custody = json.loads((args.run_dir / "custody-verification.json").read_text(encoding="utf-8"))
        assert custody["status"] == "PASS"
    manifest = json.loads((args.run_dir / "run-manifest.json").read_text(encoding="utf-8"))
    for name, receipt in manifest["outputs"].items():
        path = args.run_dir / name
        assert path.stat().st_size == receipt["bytes"]
        assert sha256(path) == receipt["sha256"]
    for name, expected_hash in manifest["code_sha256"].items():
        if name == "verify_stage2_report.py":
            continue
        assert sha256(args.root / "src" / name) == expected_hash, f"code hash changed: {name}"
    assert b"\r" not in before
    assert report_path.read_bytes() == before
    print(f"PASS: Stage 2 report, all reader claims, outputs and code receipts verified without modification: {report_path}")


if __name__ == "__main__":
    main()
