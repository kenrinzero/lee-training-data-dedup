#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

try:
    from stage1_audit import (
        compute_duplication,
        compute_removals,
        figure_counts,
        keep_agreement,
        receipt,
        round_half_up,
        run_name,
    )
    from stage1_compare import ensure_fresh_comparison, lock_conventions
except ImportError as exc:
    raise SystemExit(f"FAIL: Stage 1 implementation is missing: {exc}")


FIXTURE = [
    {"cluster_id": "0", "n_all": 1, "keep0": 0, "keep1": 1, "n_train": 1, "n_validation": 0, "n_test": 0},
    {"cluster_id": "1", "n_all": 2, "keep0": 2, "keep1": 0, "n_train": 2, "n_validation": 0, "n_test": 0},
    {"cluster_id": "2", "n_all": 2, "keep0": 2, "keep1": 0, "n_train": 1, "n_validation": 1, "n_test": 0},
    {"cluster_id": "3", "n_all": 3, "keep0": 3, "keep1": 0, "n_train": 1, "n_validation": 2, "n_test": 0},
    {"cluster_id": "4", "n_all": 2, "keep0": 2, "keep1": 0, "n_train": 0, "n_validation": 0, "n_test": 2},
    {"cluster_id": "5", "n_all": 2, "keep0": 2, "keep1": 0, "n_train": 0, "n_validation": 1, "n_test": 1},
]
SPLIT_SIZES = {"train": 5, "validation": 4, "test": 3}


class ContractTests(unittest.TestCase):
    def test_run_name_comes_from_output_directory(self):
        self.assertEqual(run_name(Path("results/stage1/run-002/audit")), "run-002")

    def test_comparison_refuses_existing_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory)
            ensure_fresh_comparison(out_dir)
            (out_dir / "convention-lock.json").write_text("existing", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                ensure_fresh_comparison(out_dir)

    def test_receipt_rejects_same_length_hash_change(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.bin"
            path.write_bytes(b"abc")
            with self.assertRaises(AssertionError):
                receipt(path, "https://example.test/input", 3, "local", "0" * 64)

    def test_duplication_metrics_hand_fixture(self):
        self.assertEqual(
            compute_duplication(FIXTURE, "validation", SPLIT_SIZES),
            {
                "TT": {"numerator": 2, "denominator": 5},
                "EE": {"numerator": 2, "denominator": 4},
                "ET": {"numerator": 3, "denominator": 4},
            },
        )
        self.assertEqual(
            compute_duplication(FIXTURE, "test", SPLIT_SIZES),
            {
                "TT": {"numerator": 2, "denominator": 5},
                "EE": {"numerator": 2, "denominator": 3},
                "ET": {"numerator": 0, "denominator": 3},
            },
        )

    def test_removal_rules_hand_fixture(self):
        self.assertEqual(
            compute_removals(FIXTURE, "validation", 5),
            {
                "A": {"removals": 3, "retained": 2},
                "B": {"removals": 1, "retained": 4},
                "S": {"removals": 4, "retained": 1},
            },
        )
        self.assertEqual(
            compute_removals(FIXTURE, "test", 5),
            {
                "A": {"removals": 1, "retained": 4},
                "B": {"removals": 1, "retained": 4},
                "S": {"removals": 4, "retained": 1},
            },
        )

    def test_evaluation_union_sensitivity(self):
        self.assertEqual(
            compute_removals(FIXTURE, "validation+test", 5),
            {
                "A": {"removals": 3, "retained": 2},
                "B": {"removals": 1, "retained": 4},
                "S": {"removals": 4, "retained": 1},
            },
        )

    def test_keep_membership_crosstab(self):
        self.assertEqual(
            keep_agreement(FIXTURE),
            {"keep0_multi": 11, "keep0_singleton": 0, "keep1_multi": 0, "keep1_singleton": 1},
        )
        changed = [dict(row) for row in FIXTURE]
        changed[0]["keep0"], changed[0]["keep1"] = 1, 0
        changed[1]["keep0"], changed[1]["keep1"] = 1, 1
        self.assertEqual(
            keep_agreement(changed),
            {"keep0_multi": 10, "keep0_singleton": 1, "keep1_multi": 1, "keep1_singleton": 0},
        )

    def test_all_edge_conventions(self):
        histogram = {5: 1, 6: 1, 10: 1, 11: 1, 20: 1, 21: 1, 50: 1, 51: 1, 500: 1, 501: 1, 5000: 1, 5001: 1}
        self.assertEqual(figure_counts(histogram, "dropped"), [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1])
        self.assertEqual(figure_counts(histogram, "low"), [0, 0, 0, 0, 1, 2, 2, 2, 2, 2, 1])
        self.assertEqual(figure_counts(histogram, "high"), [0, 0, 0, 0, 1, 1, 2, 2, 2, 2, 2])

    def test_decimal_half_up(self):
        self.assertEqual(round_half_up(Decimal(432) * 100 / Decimal(163597), 2), Decimal("0.26"))
        self.assertEqual(round_half_up(Decimal(2909540) / Decimal(1000000), 2), Decimal("2.91"))
        self.assertEqual(round_half_up(Decimal("1.005"), 2), Decimal("1.01"))

    def test_convention_lock(self):
        self.assertEqual(
            lock_conventions({"dropped": 11, "low": 9, "high": 9}),
            {"matching_conventions": ["dropped"], "locked_candidate_set": ["dropped"], "primary": "dropped", "status": "PRIMARY_LOCKED"},
        )
        self.assertEqual(
            lock_conventions({"dropped": 10, "low": 11, "high": 11}),
            {"matching_conventions": ["high", "low"], "locked_candidate_set": ["high", "low"], "primary": None, "status": "AMBIGUOUS_CONVENTION"},
        )
        self.assertEqual(
            lock_conventions({"dropped": 10, "low": 9, "high": 8}),
            {"matching_conventions": [], "locked_candidate_set": ["dropped", "high", "low"], "primary": None, "status": "AMBIGUOUS_CONVENTION"},
        )


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def verify_run(run_dir):
    run_dir = Path(run_dir)
    manifest = json.loads((run_dir / "input-manifest.json").read_text(encoding="utf-8"))
    for receipt in manifest["inputs"]:
        path = Path(receipt["local_path"])
        assert path.stat().st_size == receipt["bytes"], f"byte count changed: {path}"
        assert sha256(path) == receipt["sha256"], f"hash changed: {path}"

    rows = read_csv(run_dir / "cluster-composition.csv")
    for row in rows:
        for key in ("n_all", "keep0", "keep1", "n_train", "n_validation", "n_test"):
            row[key] = int(row[key])
    split_sizes = manifest["split_sizes"]
    for arm in ("validation", "test"):
        expected = compute_duplication(rows, arm, split_sizes)
        actual_rows = read_csv(run_dir / "derived-duplication.csv")
        for metric in ("TT", "EE", "ET"):
            actual = next(item for item in actual_rows if item["arm"] == arm and item["metric"] == metric)
            assert int(actual["numerator"]) == expected[metric]["numerator"]
            assert int(actual["denominator"]) == expected[metric]["denominator"]
    for arm in ("validation", "test", "validation+test"):
        expected = compute_removals(rows, arm, split_sizes["train"])
        actual_rows = read_csv(run_dir / "derived-removals.csv")
        for rule in ("A", "B", "S"):
            actual = next(item for item in actual_rows if item["arm"] == arm and item["rule"] == rule)
            assert int(actual["removals"]) == expected[rule]["removals"]
            assert int(actual["retained"]) == expected[rule]["retained"]

    histogram = {}
    for row in rows:
        histogram[row["n_all"]] = histogram.get(row["n_all"], 0) + 1
    figure_rows = read_csv(run_dir / "figure-counts.csv")
    for convention in ("dropped", "low", "high"):
        expected = figure_counts(histogram, convention)
        actual = [int(item["cluster_count"]) for item in figure_rows if item["convention"] == convention]
        assert actual == expected, f"figure mismatch: {convention}"
    assert keep_agreement(rows) == json.loads((run_dir / "derived-summary.json").read_text(encoding="utf-8"))["keep_agreement"]

    for path in run_dir.iterdir():
        if path.suffix in {".json", ".csv", ".md"}:
            data = path.read_bytes()
            data.decode("utf-8")
            assert b"\r\n" not in data, f"CRLF drift: {path}"
            assert b"\r" not in data, f"CR drift: {path}"
    print(f"PASS: verified {len(rows)} clusters, all metrics, figures, input hashes, and UTF-8/LF outputs in {run_dir}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir")
    args = parser.parse_args()
    if args.run_dir:
        verify_run(args.run_dir)
    else:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(ContractTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            raise SystemExit(1)


if __name__ == "__main__":
    main()
