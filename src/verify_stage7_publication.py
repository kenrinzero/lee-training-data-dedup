#!/usr/bin/env python3
import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from stage7_build import (
    ACCEPTED_RUNS,
    read_json,
    verify_manifest_outputs,
    verify_recorded_inputs,
)
from stage7_publication import (
    STAGE7_RUN,
    build_publication,
    rewrite_root_reader,
    sanitize_text,
    verify_publication,
)

ROOT = Path(__file__).resolve().parents[1]


class PublicationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.temp.name) / "candidate"
        cls.other = Path(cls.temp.name) / "other"
        build_publication(ROOT, cls.out)
        build_publication(ROOT, cls.other)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_audit_narrative_corrections(self):
        audit = (ROOT / "planning/external-audit-2026-11-11.md").read_text(encoding="utf-8")
        self.assertIn("149` size rows", audit)
        self.assertNotIn("556` size rows", audit)
        self.assertNotIn("news.Validation.org", audit)
        self.assertIn("test_coordinated_accepted_output_and_manifest_change_is_rejected", audit)
        self.assertNotIn("test_run_verifier_rejects_stale_input_manifest_hash", audit)
        self.assertIn("1.68%` (external Google Research abstract)", audit)
        self.assertIn("4.60%` (direct validation-with-train)", audit)
        self.assertIn("Correction note", audit)

    def test_sanitize_member_path_variants(self):
        native = str(ROOT)
        posix = native.replace("\\", "/")
        escaped = native.replace("\\", "\\\\")
        wsl = "/mnt/c/" + posix[0].lower() + posix[2:]
        text = "\n".join((native + "\\data\\raw\\clusters", posix + "/data/raw/clusters", escaped + "\\\\data\\\\raw", wsl + "/data/raw"))
        sanitized = sanitize_text(text, ROOT)
        for prefix in (native, posix, escaped, wsl):
            self.assertNotIn(prefix, sanitized)
        self.assertIn("data/raw/clusters", sanitized.replace("\\", "/"))

    def test_root_reader_link_rewrite(self):
        source = '<a href="../../../../paper/targets/printed-targets.csv">source</a><a href="#ledger">ledger</a>'
        self.assertEqual(rewrite_root_reader(source), '<a href="paper/targets/printed-targets.csv">source</a><a href="#ledger">ledger</a>')

    def test_export_exclusions_and_private_paths(self):
        self.assertFalse((self.out / "data/raw/clusters").exists())
        self.assertFalse((self.out / "paper/paper.pdf").exists())
        self.assertFalse((self.out / ".venv").exists())
        self.assertFalse((self.out / "results/stage2/run-004/audit/work").exists())
        for path in self.out.rglob("*"):
            if path.is_file():
                self.assertLess(path.stat().st_size, 100_000_000, path)
                if path.suffix in {".md", ".json", ".csv", ".py", ".html", ".svg", ".txt", ".gitignore", ".gitattributes", ".nojekyll", ""}:
                    content = path.read_bytes()
                    content.decode("utf-8")
                    self.assertNotIn(b"\r", content, path)
                    for prefix in (str(ROOT), str(ROOT).replace("\\", "/"), str(ROOT).replace("\\", "\\\\")):
                        self.assertNotIn(prefix.encode(), content, path)

    def test_receipts_recomputed(self):
        for relative in ACCEPTED_RUNS.values():
            run_dir = self.out / relative
            verify_manifest_outputs(run_dir, read_json(run_dir / "run-manifest.json"))
        result = subprocess.run(
            [sys.executable, "-B", "src/verify_stage7.py", "--run-dir", STAGE7_RUN],
            cwd=self.out,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: Stage 7 deterministic reader", result.stdout)

    def test_release_gate(self):
        verify_publication(ROOT, self.out)
        markers = (
            b"C:" + b"\\\\Users\\\\", b"C:" + b"\\Users\\", b"C:" + b"/Users/",
            b"D:" + b"\\\\Project", b"D:" + b"\\Project", b"D:" + b"/Project/",
            b"/mnt/c/" + b"Users/",
        )
        for path in self.out.rglob("*"):
            if path.is_file():
                content = path.read_bytes()
                for marker in markers:
                    self.assertNotIn(marker, content, path)

    def test_external_interpreter_sanitized(self):
        home = ROOT.parents[2]
        native = str(home) + "\\AppData\\Local\\Programs\\Python\\Python313\\python.exe"
        posix = native.replace("\\", "/")
        escaped = native.replace("\\", "\\\\")
        for value in (native, posix, escaped):
            self.assertEqual(sanitize_text(value, ROOT), "python.exe")
        for relative in ("results/stage1/run-004/audit/input-manifest.json", "results/stage2/run-004/audit/input-manifest.json"):
            manifest = read_json(self.out / relative)
            self.assertNotIn("AppData", manifest["command"][0])
            self.assertEqual(manifest["command"][0], "python.exe")

    def test_public_freeze_count(self):
        spec = importlib.util.spec_from_file_location("public_stage7_build", self.out / "src/stage7_build.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.verify_freeze_contract(self.out)["exact_hash_files_verified"], 11)
        expected = 12 if (ROOT / "paper/paper.pdf").is_file() else 11
        self.assertEqual(module.verify_freeze_contract(ROOT)["exact_hash_files_verified"], expected)

    def test_provenance_byte_identical_labels(self):
        provenance = read_json(self.out / "PACKAGE-PROVENANCE.json")
        for record in provenance["files"]:
            if record["transform"] == "byte-identical allowlisted copy":
                self.assertEqual(
                    (ROOT / record["source"]).read_bytes(),
                    (self.out / record["exported"]).read_bytes(),
                    record["source"],
                )

    def test_reader_has_no_stale_owner_gate_or_missing_interpreter(self):
        for relative in ("index.html", "REPORT.md", "results/stage7/run-002/audit/index.html", "results/stage7/run-002/audit/report.md"):
            text = (self.out / relative).read_text(encoding="utf-8")
            self.assertNotIn("separate user decision", text)
            self.assertIn("aggregate results", text)
        readme = (self.out / "README.md").read_text(encoding="utf-8")
        self.assertNotIn(".venv/Scripts/python", readme)
        self.assertIn("duckdb==2.0.0", readme)

    def test_readme_reader_link_is_public_site(self):
        readme = (self.out / "README.md").read_text(encoding="utf-8")
        self.assertIn("[Open the offline reader](https://kenrinzero.github.io/lee-training-data-dedup/)", readme)
        self.assertNotIn("[Open the offline reader](index.html)", readme)

    def test_reader_links_source_repository(self):
        for relative in ("index.html", "results/stage7/run-001/audit/index.html", "results/stage7/run-002/audit/index.html"):
            text = (self.out / relative).read_text(encoding="utf-8")
            self.assertEqual(text.count('<a href="https://github.com/kenrinzero/lee-training-data-dedup">Source repository</a>'), 1)

    def test_deterministic_build(self):
        first = {str(path.relative_to(self.out)): path.read_bytes() for path in self.out.rglob("*") if path.is_file()}
        second = {str(path.relative_to(self.other)): path.read_bytes() for path in self.other.rglob("*") if path.is_file()}
        self.assertEqual(first, second)

    def test_required_documents_and_credits(self):
        for name in (
            "README.md", "REPORT.md", "AUDIT.md", "CREDITS.md", "LICENSE",
            "REPORT-LICENSE", "THIRD_PARTY_NOTICES.md", "EXCLUDED-FILES.md",
            "PACKAGE-MANIFEST.json", "PACKAGE-PROVENANCE.json", "index.html", ".nojekyll",
        ):
            self.assertTrue((self.out / name).is_file(), name)
        credits = (self.out / "CREDITS.md").read_text(encoding="utf-8")
        readme = (self.out / "README.md").read_text(encoding="utf-8")
        self.assertIn("Kimi K3.1 Pro", credits)
        self.assertIn("Gemini 4 Argon", credits)
        self.assertIn("Kimi K3.1 Pro", readme)
        self.assertIn("Gemini 4 Argon", readme)
        self.assertIn("MIT License", (self.out / "LICENSE").read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--run-dir", type=Path)
    args = parser.parse_args()
    if args.run_dir:
        verify_publication(args.root, args.run_dir)
    else:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(PublicationContractTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            raise SystemExit(1)


if __name__ == "__main__":
    main()
