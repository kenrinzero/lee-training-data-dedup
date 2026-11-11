#!/usr/bin/env python3
import argparse
import csv
import json
import os
import shutil
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from stage1_audit import sha256
from stage7_build import (
    ACCEPTED_RUNS,
    build_figures,
    build_ledger,
    build_report,
    build_stage7,
    render_html,
    render_panel_svg,
    verify_manifest_outputs,
    verify_freeze_contract,
    verify_recorded_inputs,
    write_csv,
)

ROOT = Path(__file__).resolve().parents[1]


class ReaderParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.hrefs = []
        self.external_assets = []
        self.labels = set()
        self.controls = set()
        self.main_count = 0
        self.h1_count = 0
        self.table_count = 0
        self.live_regions = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a" and "href" in attrs:
            self.hrefs.append(attrs["href"])
        if tag == "script" and "src" in attrs:
            self.external_assets.append(attrs["src"])
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.external_assets.append(attrs.get("href"))
        if tag == "label" and "for" in attrs:
            self.labels.add(attrs["for"])
        if tag in {"input", "select", "button"} and "id" in attrs:
            self.controls.add(attrs["id"])
        if tag == "main":
            self.main_count += 1
        if tag == "h1":
            self.h1_count += 1
        if tag == "table":
            self.table_count += 1
        if attrs.get("aria-live") == "polite":
            self.live_regions += 1


class Stage7ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = build_ledger(ROOT)
        cls.figures = build_figures(ROOT)
        cls.html = render_html(ROOT, cls.ledger, cls.figures)
        cls.report = build_report(ROOT, cls.ledger, cls.figures)

    def test_oracle_coverage_and_external_context(self):
        with (ROOT / "paper/targets/printed-targets.csv").open(encoding="utf-8", newline="") as handle:
            target_ids = {row["target_id"] for row in csv.DictReader(handle)}
        covered = {row["target_id"] for row in self.ledger if row["target_id"]}
        self.assertEqual(target_ids, covered)
        for row in self.ledger:
            self.assertTrue(row["verdict"], row["entry_id"])
            self.assertTrue(row["source_path"], row["entry_id"])
            if row["verdict"] == "NOT_EXECUTABLE_INPUT":
                self.assertTrue(row["qualification"], row["entry_id"])
        external = [row for row in self.ledger if row["entry_id"] == "external-c4-publication-abstract"]
        self.assertEqual(len(external), 1)
        self.assertEqual(external[0]["printed_value"], "1.68")
        self.assertIn("not a PDF Table 2 substitute", external[0]["qualification"])

    def test_released_figures_preserve_conventions_and_edges(self):
        panels = {panel["id"]: panel for panel in self.figures["panels"]}
        self.assertEqual(set(panels), {"fig1-c4", "fig8-realnews", "fig8-wiki40b", "fig8-lm1b"})
        expected_matches = {
            "fig1-c4": {"dropped": 11, "low": 7, "high": 7},
            "fig8-realnews": {"dropped": 11, "low": 8, "high": 8},
            "fig8-wiki40b": {"dropped": 11, "low": 9, "high": 9},
        }
        for panel_id in ("fig1-c4", "fig8-realnews", "fig8-wiki40b"):
            panel = panels[panel_id]
            self.assertEqual(set(panel["conventions"]), {"dropped", "low", "high"})
            for convention, rows in panel["conventions"].items():
                self.assertEqual(len(rows), 11)
                self.assertEqual(sum(row["verdict"] == "MATCH" for row in rows), expected_matches[panel_id][convention])
        self.assertEqual([row["cluster_count"] for row in panels["fig1-c4"]["edges"]], [9974, 2400, 788, 4, 0])
        self.assertEqual([row["cluster_count"] for row in panels["fig8-wiki40b"]["edges"]], [39, 10, 0, 0, 0])
        self.assertEqual([row["cluster_count"] for row in panels["fig8-realnews"]["edges"]], [703, 24, 6, 0, 0])
        lm1b = panels["fig8-lm1b"]
        self.assertFalse(lm1b["released"])
        self.assertEqual(len(lm1b["printed_counts"]), 11)
        self.assertEqual(lm1b["verdict"], "NOT_EXECUTABLE_INPUT")

    def test_wiki_arms_and_random_split_bases(self):
        wiki = [row for row in self.ledger if row["target_id"].startswith("table2-wiki40b-")]
        self.assertEqual(len(wiki), 6)
        self.assertEqual({row["basis"] for row in wiki}, {"validation", "test"})
        random_rows = [row for row in self.ledger if row["entry_id"] == "c4-random-split-ee"]
        self.assertEqual(len(random_rows), 1)
        row = random_rows[0]
        self.assertEqual(row["verdict"], "MISMATCH")
        self.assertIn("N × E[P_EE]", row["qualification"])
        self.assertIn("V × E[P_EE]", row["qualification"])
        self.assertIn("5,849.19", row["derived_value"])
        self.assertIn("1.60%", row["derived_value"])

    def test_limitations_and_conditional_verdicts_survive(self):
        rows = self.ledger
        realnews_table2 = [row for row in rows if row["target_id"].startswith("table2-realnews-")]
        self.assertEqual(len(realnews_table2), 3)
        self.assertTrue(all(row["verdict"] == "NOT_EXECUTABLE_INPUT" for row in realnews_table2))
        self.assertTrue(all("split mapping" in row["qualification"] for row in realnews_table2))
        realnews_table13 = [row for row in rows if row["target_id"] == "table13-realnews-examples-neardup"]
        self.assertEqual(realnews_table13[0]["verdict"], "MISMATCH")
        self.assertIn("CONDITIONAL_RELEASE_POPULATION", realnews_table13[0]["basis"])
        c4_missing = [row for row in rows if row["target_id"] in {"table11-c4-r20-total", "table11-c4-r20-frac"}]
        self.assertTrue(all(row["verdict"] == "SOURCE_MISSING" for row in c4_missing))
        for row in rows:
            if row["target_id"].startswith("table11-") and row["verdict"] != "SOURCE_MISSING":
                self.assertIn("exact full-id", row["qualification"].lower())
                self.assertIn("host-level", row["qualification"])

    def test_manifest_hash_mutation_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            output = run_dir / "value.txt"
            output.write_bytes(b"ab")
            manifest = {"outputs": {"value.txt": {"bytes": 2, "sha256": sha256(output)}}}
            verify_manifest_outputs(run_dir, manifest)
            output.write_bytes(b"cd")
            with self.assertRaises(AssertionError):
                verify_manifest_outputs(run_dir, manifest)

    def test_html_is_offline_accessible_and_links_resolve(self):
        parser = ReaderParser()
        parser.feed(self.html)
        self.assertEqual(parser.main_count, 1)
        self.assertEqual(parser.h1_count, 1)
        self.assertGreaterEqual(parser.table_count, 5)
        self.assertGreaterEqual(parser.live_regions, 1)
        self.assertEqual(parser.external_assets, [])
        self.assertLessEqual(parser.labels, parser.controls)
        for href in parser.hrefs:
            if href.startswith("#"):
                self.assertIn(href[1:], parser.ids)
        self.assertIn("4.63%", self.html)
        self.assertIn("2,782,768", self.html)
        self.assertIn("No LM1B cluster archive is pinned", self.html)
        self.assertIn("host-level", self.html)

    def test_svg_preserves_zero_bars_and_accessible_description(self):
        panel = next(panel for panel in self.figures["panels"] if panel["id"] == "fig1-c4")
        svg = render_panel_svg(panel, "dropped")
        self.assertIn('role="img"', svg)
        self.assertIn("<title id=", svg)
        self.assertIn("<desc id=", svg)
        self.assertEqual(svg.count('class="bar"'), 11)
        realnews = next(panel for panel in self.figures["panels"] if panel["id"] == "fig8-realnews")
        self.assertIn('data-count="0"', render_panel_svg(realnews, "dropped"))
        self.assertIn("log10(groups + 1)", svg)

    def test_integrated_report_preserves_headlines_and_alternative_bases(self):
        for required in (
            "4.63%",
            "1.58%",
            "1.60%",
            "3.943870419601502%",
            "8,001,466",
            "14,410,977",
            "2,782,768",
            "CEILING_COMPATIBLE",
            "not a train-size match",
            "1.68%",
            "not a PDF Table 2 substitute",
            "5,849.19",
        ):
            self.assertIn(required, self.report)

    def test_build_refuses_to_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "audit"
            out_dir.mkdir()
            (out_dir / "index.html").write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                build_stage7(ROOT, out_dir)
            self.assertEqual((out_dir / "index.html").read_text(encoding="utf-8"), "keep")

    def test_freeze_contract_and_mutation_detection(self):
        receipt = verify_freeze_contract(ROOT)
        self.assertTrue(receipt["preregistration_prefix_extension"])
        freeze = json.loads((ROOT / "planning/FREEZE-v1.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            copied = Path(tmp)
            for relative in set(freeze["sha256"]) | set(freeze["snapshot_files"]) | {"planning/FREEZE-v1.json"}:
                if relative == "paper/paper.pdf":
                    continue
                destination = copied / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((ROOT / relative).read_bytes())
            verify_freeze_contract(copied)
            snapshot = copied / "planning/preregistration-v1.md"
            snapshot.write_bytes(snapshot.read_bytes() + b"x")
            with self.assertRaises(AssertionError):
                verify_freeze_contract(copied)

    def test_end_to_end_run_identity_receipts_and_encoding(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "run-009" / "audit"
            build_stage7(ROOT, out_dir)
            manifest = json.loads((out_dir / "run-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["stage"], "Stage 7 / run-009")
            self.assertIn("run-009", (out_dir / "report.md").read_text(encoding="utf-8"))
            verify_manifest_outputs(out_dir, manifest)
            verify_run(ROOT, out_dir)
            for path in out_dir.iterdir():
                if path.suffix in {".html", ".md", ".csv", ".json", ".svg"}:
                    content = path.read_bytes()
                    content.decode("utf-8")
                    self.assertNotIn(b"\r", content, path.name)

    def test_coordinated_accepted_output_and_manifest_change_is_rejected(self):
        freeze = json.loads((ROOT / "planning/FREEZE-v1.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            fake_root = Path(tmp) / "root"
            for relative in ACCEPTED_RUNS.values():
                source_dir = ROOT / relative
                destination_dir = fake_root / relative
                destination_dir.mkdir(parents=True)
                for source in source_dir.iterdir():
                    if source.is_file():
                        os.link(source, destination_dir / source.name)
            required = set(freeze["sha256"]) | set(freeze["snapshot_files"]) | {
                "planning/FREEZE-v1.json",
                "planning/step0/arithmetic.md",
                "planning/step0/arithmetic.json",
            }
            for relative in required:
                if relative == "paper/paper.pdf":
                    continue
                destination = fake_root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                os.link(ROOT / relative, destination)
            candidate = Path(tmp) / "candidate"
            shutil.copytree(ROOT / "results/stage7/run-001/audit", candidate)
            changed = fake_root / ACCEPTED_RUNS["stage1"] / "comparison-summary.json"
            changed.unlink()
            changed.write_bytes(b"{}\n")
            manifest_path = fake_root / ACCEPTED_RUNS["stage1"] / "run-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["outputs"]["comparison-summary.json"] = {"bytes": 3, "sha256": sha256(changed)}
            manifest_path.unlink()
            manifest_path.write_bytes((json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
            with self.assertRaises(AssertionError):
                verify_recorded_inputs(fake_root, candidate)

    def test_non_html_output_and_manifest_change_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "run-001" / "audit"
            shutil.copytree(ROOT / "results/stage7/run-001/audit", candidate)
            changed = candidate / "ledger.csv"
            changed.write_bytes(b"changed\n")
            manifest_path = candidate / "run-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["outputs"]["ledger.csv"] = {"bytes": changed.stat().st_size, "sha256": sha256(changed)}
            manifest_path.write_bytes((json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
            with self.assertRaises(AssertionError):
                verify_run(ROOT, candidate)


def check_output_hashes(run_dir, manifest):
    run_dir = Path(run_dir)
    for name, receipt in manifest["outputs"].items():
        path = run_dir / name
        assert path.is_file(), f"missing output: {name}"
        assert path.stat().st_size == receipt["bytes"], f"output byte count changed: {name}"
        assert sha256(path) == receipt["sha256"], f"output hash changed: {name}"


def verify_run(root, run_dir):
    root = Path(root)
    run_dir = Path(run_dir)
    before = {path.name: path.read_bytes() for path in run_dir.iterdir() if path.is_file()}
    verify_recorded_inputs(root, run_dir)
    ledger = build_ledger(root)
    figures = build_figures(root)
    expected_html = render_html(root, ledger, figures)
    expected_report = build_report(root, ledger, figures, run_dir.parent.name)
    assert (run_dir / "index.html").read_text(encoding="utf-8") == expected_html
    assert (run_dir / "report.md").read_text(encoding="utf-8") == expected_report
    expected_json = lambda value: (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    assert (run_dir / "ledger.json").read_bytes() == expected_json(ledger)
    assert (run_dir / "figures.json").read_bytes() == expected_json(figures)
    with tempfile.TemporaryDirectory() as tmp:
        expected_csv = Path(tmp) / "ledger.csv"
        write_csv(expected_csv, ledger)
        assert (run_dir / "ledger.csv").read_bytes() == expected_csv.read_bytes()
    for panel in figures["panels"]:
        convention = panel["primary"] if panel["released"] else "dropped"
        expected_svg = (render_panel_svg(panel, convention) + "\n").encode("utf-8")
        assert (run_dir / f"{panel['id']}.svg").read_bytes() == expected_svg
    for name, content in before.items():
        assert b"\r" not in content, f"CR byte found: {name}"
        if name.endswith((".html", ".md", ".csv", ".json", ".svg")):
            content.decode("utf-8")
    manifest = json.loads((run_dir / "run-manifest.json").read_text(encoding="utf-8"))
    check_output_hashes(run_dir, manifest)
    for name, expected_hash in manifest["code_sha256"].items():
        assert sha256(root / "src" / name) == expected_hash, f"code hash changed: {name}"
    after = {path.name: path.read_bytes() for path in run_dir.iterdir() if path.is_file()}
    assert before == after, "verification modified the run"
    print(f"PASS: Stage 7 deterministic reader, ledger, figures, receipts and UTF-8/LF verified without modification: {run_dir}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--run-dir", type=Path)
    args = parser.parse_args()
    if args.run_dir:
        verify_run(args.root, args.run_dir)
    else:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Stage7ContractTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            raise SystemExit(1)


if __name__ == "__main__":
    main()
