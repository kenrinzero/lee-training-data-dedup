#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import tempfile
from pathlib import Path

try:
    from stage1_report import ensure_fresh_report, superseded_run
except ImportError as exc:
    raise SystemExit(f"FAIL: Stage 1 report generator or immutability guard is missing: {exc}")


def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def check_fresh_guard():
    assert superseded_run("run-001") is None
    assert superseded_run("run-003") == "run-002"
    with tempfile.TemporaryDirectory() as directory:
        out_dir = Path(directory)
        ensure_fresh_report(out_dir)
        (out_dir / "report.md").write_text("existing", encoding="utf-8")
        try:
            ensure_fresh_report(out_dir)
        except FileExistsError:
            pass
        else:
            raise AssertionError("report guard allowed an existing report to be overwritten")
    print("PASS: report guard accepts a fresh directory and refuses an existing report")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--check-fresh", action="store_true")
    args = parser.parse_args()
    if args.check_fresh:
        check_fresh_guard()
        return
    report_path = args.run_dir / "report.md"
    assert report_path.is_file(), f"missing report: {report_path}"
    before = report_path.read_bytes()
    report = before.decode("utf-8")
    lock = json.loads((args.run_dir / "convention-lock.json").read_text(encoding="utf-8"))
    assert f"**{lock['status']}**" in report
    assert "C4 content was not opened" in report
    assert "does not rename or relabel" in report
    assert "unused run name" in report
    for row in read_csv(args.run_dir / "table2-verdicts.csv"):
        assert row["derived_numerator"] in report
        assert row["rounded_percent"] in report
        assert row["verdict"] in report
    for row in read_csv(args.run_dir / "table13-verdicts.csv"):
        assert str(row["derived_removals"]) in report
        assert row["derived_retained_rounded"] in report
        assert row["interval_verdict"] in report
    for row in read_csv(args.run_dir / "figure-verdicts.csv"):
        assert row["derived_count"] in report
    assert b"\r" not in before
    assert report_path.read_bytes() == before, "report verification modified the report"
    run_manifest = json.loads((args.run_dir / "run-manifest.json").read_text(encoding="utf-8"))
    assert run_manifest["stage"] == f"Stage 1 / {args.run_dir.parent.name}"
    assert run_manifest["supersedes"] == superseded_run(args.run_dir.parent.name)
    assert run_manifest["c4_content_opened"] is False
    for name, receipt in run_manifest["outputs"].items():
        path = args.run_dir / name
        assert path.stat().st_size == receipt["bytes"], f"output byte count changed: {name}"
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        assert digest.hexdigest() == receipt["sha256"], f"output hash changed: {name}"
    src_dir = args.run_dir.resolve().parents[3] / "src"
    for name, expected_hash in run_manifest["code_sha256"].items():
        if name == "verify_stage1_report.py":
            continue
        assert hashlib.sha256((src_dir / name).read_bytes()).hexdigest() == expected_hash, f"code hash changed: {name}"
    print(f"PASS: report, all output/code hashes, verdicts, and frozen convention lock verified without modification: {report_path}")


if __name__ == "__main__":
    main()
