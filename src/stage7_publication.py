#!/usr/bin/env python3
import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

from stage1_audit import sha256
from stage7_build import ACCEPTED_RUNS, read_json, write_json, write_text

STAGE7_RUN = "results/stage7/run-002/audit"

TOP_LEVEL = (
    "AGENTS.md", "CLAIM_INVENTORY.md", "PREREGISTRATION.md", "README.md",
    "SCOPE.md", "STEP0_DERIVATIONS.md",
)
EXPORT_DIRECTORIES = (
    "src", "paper/targets", "planning/step0",
    "results/stage1/run-004/audit", "results/stage2/run-004/audit",
    "results/stage3/run-002/audit", "results/stage7/run-001/audit",
    "results/stage7/run-002/audit",
)
EXTRA_FILES = (
    "paper/PROVENANCE.md", "data/raw/MANIFEST.md",
    "planning/FREEZE-v1.json", "planning/SEED-2026-09-30.md",
    "planning/preregistration-v1.md", "planning/claim-inventory-v1.md",
    "planning/step0-derivations-v1.md", "planning/external-audit-2026-11-10.md",
    "planning/external-audit-2026-11-11.md", "results/README.md",
    "results/stage1/run-004/progress.md", "results/stage2/run-004/progress.md",
    "results/stage2/run-002/split-acquisition-manifest.json",
    "results/stage2/run-002/train-source-metadata.json",
    "results/stage3/run-002/acquisition-manifest.json",
    "results/stage3/run-002/progress.md", "results/stage7/run-001/progress.md",
    "results/stage7/run-001/cold-disk-verification.log",
    "results/stage7/run-001/second-reader-ruleset.json",
    "results/stage7/run-002/progress.md",
)
TEXT_SUFFIXES = {".md", ".json", ".csv", ".py", ".html", ".svg", ".txt", ".log", ""}


def export_files(root):
    root = Path(root)
    files = {root / relative for relative in TOP_LEVEL + EXTRA_FILES}
    for relative in EXPORT_DIRECTORIES:
        for path in (root / relative).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and "work" not in path.parts:
                files.add(path)
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def path_variants(root):
    root = Path(root).resolve()
    native = str(root)
    posix = native.replace("\\", "/")
    escaped = native.replace("\\", "\\\\")
    wsl = "/mnt/c/" + posix[0].lower() + posix[2:]
    return escaped, native, posix, wsl


def sanitize_text(text, root):
    stripped = text.strip()
    if stripped.lower().endswith("python.exe") and "users" in stripped.lower() and (":\\" in stripped or ":/" in stripped):
        return "python.exe"
    for prefix in path_variants(root):
        text = text.replace(prefix, ".")
    return text


def publication_language(text):
    replacement = "This package redistributes code and aggregate results only; raw inputs and the source PDF are not included."
    for old in (
        "Publication remains a separate user decision.",
        "Publication and any redistribution require separate user decisions.",
        "Publication requires independent scientific and reader review and a separate user decision.",
        "Publication is a separate user decision.",
        "Publication is separately gated by the user.",
    ):
        text = text.replace(old, replacement)
    return text


def sanitize_value(value, root):
    if isinstance(value, str):
        return sanitize_text(value, root)
    if isinstance(value, list):
        return [sanitize_value(item, root) for item in value]
    if isinstance(value, dict):
        return {key: sanitize_value(item, root) for key, item in value.items()}
    return value


def rewrite_root_reader(text):
    text = text.replace("../../../../", "")
    text = text.replace('href="report.md"', 'href="REPORT.md"')
    for name in ("input-manifest.json", "run-manifest.json", "fig1-c4.svg", "fig8-lm1b.svg", "fig8-realnews.svg", "fig8-wiki40b.svg"):
        text = text.replace(f'href="{name}"', f'href="{STAGE7_RUN}/{name}"')
    return text


def refresh_run_receipts(out_dir):
    for relative in ACCEPTED_RUNS.values():
        run_dir = out_dir / relative
        manifest_path = run_dir / "run-manifest.json"
        manifest = read_json(manifest_path)
        for name in manifest["outputs"]:
            path = run_dir / name
            manifest["outputs"][name] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
        write_json(manifest_path, manifest)
    build_path = out_dir / "src/stage7_build.py"
    build_text = build_path.read_text(encoding="utf-8")
    build_text = build_text.replace(
        '        assert path.is_file(), f"missing frozen file: {relative}"\n        assert sha256(path) == freeze["sha256"][relative], f"frozen file hash changed: {relative}"',
        '        if relative == "paper/paper.pdf" and not path.exists():\n            continue\n        assert path.is_file(), f"missing frozen file: {relative}"\n        assert sha256(path) == freeze["sha256"][relative], f"frozen file hash changed: {relative}"',
    )
    build_text = build_text.replace(
        '        "exact_hash_files_verified": len(exact_files),',
        '        "exact_hash_files_verified": len(exact_files) - (0 if (root / "paper/paper.pdf").is_file() else 1),',
    )
    build_text = build_text.replace(
        '        "postfreeze_manifest": {"bytes": manifest.stat().st_size, "sha256": sha256(manifest)},\n    }',
        '        "postfreeze_manifest": {"bytes": manifest.stat().st_size, "sha256": sha256(manifest)},\n        "excluded_sources": ["paper/paper.pdf"],\n    }',
    )
    language_helper = '''def publication_language(text):
    replacement = "This package redistributes code and aggregate results only; raw inputs and the source PDF are not included."
    for old in (
        "Publication remains a separate user decision.",
        "Publication and any redistribution require separate user decisions.",
        "Publication requires independent scientific and reader review and a separate user decision.",
        "Publication is a separate user decision.",
        "Publication is separately gated by the user.",
    ):
        text = text.replace(old, replacement)
    return text


def verify_manifest_outputs(run_dir, manifest):'''
    build_text = build_text.replace("def verify_manifest_outputs(run_dir, manifest):", language_helper, 1)
    build_text = build_text.replace('    return "".join(parts)', '    return publication_language("".join(parts))')
    build_text = build_text.replace('    return "\\n".join(lines)', '    return publication_language("\\n".join(lines))')
    assert 'excluded_sources' in build_text and 'and not path.exists()' in build_text
    write_text(build_path, build_text)
    verifier_path = out_dir / "src/verify_stage7.py"
    verifier_text = verifier_path.read_text(encoding="utf-8")
    verifier_text = verifier_text.replace(
        '            for relative in set(freeze["sha256"]) | set(freeze["snapshot_files"]) | {"planning/FREEZE-v1.json"}:\n                destination = copied / relative',
        '            for relative in set(freeze["sha256"]) | set(freeze["snapshot_files"]) | {"planning/FREEZE-v1.json"}:\n                if relative == "paper/paper.pdf":\n                    continue\n                destination = copied / relative',
    )
    verifier_text = verifier_text.replace(
        '            for relative in required:\n                destination = fake_root / relative',
        '            for relative in required:\n                if relative == "paper/paper.pdf":\n                    continue\n                destination = fake_root / relative',
    )
    assert verifier_text.count('relative == "paper/paper.pdf"') >= 2
    write_text(verifier_path, verifier_text)
    for stage7_relative in ("results/stage7/run-001/audit", STAGE7_RUN):
        stage7_dir = out_dir / stage7_relative
        input_path = stage7_dir / "input-manifest.json"
        inputs = read_json(input_path)
        inputs["freeze"]["excluded_sources"] = ["paper/paper.pdf"]
        inputs["freeze"]["exact_hash_files_verified"] = 11
        for stage, relative in ACCEPTED_RUNS.items():
            manifest_path = out_dir / relative / "run-manifest.json"
            manifest = read_json(manifest_path)
            inputs["accepted_runs"][stage]["run_manifest"] = {
                "bytes": manifest_path.stat().st_size,
                "sha256": sha256(manifest_path),
            }
            inputs["accepted_runs"][stage]["outputs"] = manifest["outputs"]
        write_json(input_path, inputs)
        stage7_manifest_path = stage7_dir / "run-manifest.json"
        stage7_manifest = read_json(stage7_manifest_path)
        for name in stage7_manifest["outputs"]:
            path = stage7_dir / name
            stage7_manifest["outputs"][name] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
        stage7_manifest["code_sha256"]["stage7_build.py"] = sha256(build_path)
        stage7_manifest["code_sha256"]["verify_stage7.py"] = sha256(verifier_path)
        write_json(stage7_manifest_path, stage7_manifest)


MIT_LICENSE = """MIT License

Copyright (c) 2026 kenrinzero

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

REPORT_LICENSE = """Creative Commons Attribution 4.0 International

Copyright 2026 kenrinzero.

The project's original prose, report, and figures are offered under CC BY 4.0,
to the extent the project can license them: share and adapt with attribution
and a link to this licence. Third-party materials remain under their own terms;
see THIRD_PARTY_NOTICES.md.

https://creativecommons.org/licenses/by/4.0/
"""

CREDITS = """# Credits

Directed by **Kenrin** ([@kenrinzero](https://github.com/kenrinzero)).

- **Kimi K3.1 Pro** — Stage 1–3 and Stage 7 implementation and verification,
  integrated reader, publication packaging, and documentation corrections.
- **Gemini 4 Argon (High)** — independent cross-family scientific and reader
  review of Step 0 and Stages 1–2, and of RealNews Stage 3 and final Stage 7.
- **Fresh-context Kimi reviewer (agent-0)** — independent numerical and reader
  review of the Stage 7 candidate and its correction requirements.

## Source work

Katherine Lee, Daphne Ippolito, Andrew Nystrom, Chiyuan Zhang, Douglas Eck,
Chris Callison-Burch, and Nicholas Carlini (2022), *Deduplicating Training Data
Makes Language Models Better*, ACL 2022, pp. 8424–8445.
https://doi.org/10.18653/v1/2022.acl-long.577

The authors' released NEARDUP cluster assignments and public dataset metadata
made this bounded verification possible. This package is an independent audit,
not an official Google product or a reproduction of the authors' trained models.
"""

README = """# Lee et al.: duplication statistics against the released clusters

A pre-registered, executable audit of Lee et al. (2022),
*[Deduplicating Training Data Makes Language Models Better](https://doi.org/10.18653/v1/2022.acl-long.577)*.

**[Open the offline reader](https://kenrinzero.github.io/lee-training-data-dedup/)** · **[Read the integrated report](REPORT.md)** · **[Independent audit](AUDIT.md)**

## Principal finding

The released C4, RealNews, and Wiki-40B cluster assignments reproduce **all 33
printed figure bars** when exact bin-edge sizes are dropped. Direct C4
train-with-train membership is nevertheless **4.63%**, not the printed **3.04%**.
C4 Table 13 reproduces under evaluation-preferred Rule A, while Rule B and the
all-train sensitivity do not. These are rule-derived interpretations, not
observed author deletions.

The audit also preserves the negative and bounded results: Wiki-40B's printed
`valid` remains unresolved between public validation and test; RealNews split
cells are non-executable, while its split-free ceiling is compatible; LM1B stays
printed-only; and exact full-ID URL misses are not promoted to host-level
contradictions. No claim about model quality, perplexity, or memorization follows
from this package.

## Read and reproduce

The root reader and the nested reader at
`results/stage7/run-002/audit/index.html` are dependency-free HTML/CSS/JavaScript
and SVG. They work offline without a server. The complete ledger contains **286
entries covering all 193 printed-oracle rows**, including alternative evaluation
arms, removal rules, conventions, and explicit non-executable reasons.

From the repository root:

```bash
python -B src/verify_stage1.py
python -B src/verify_stage2.py
python -B src/verify_stage3.py
python -B src/verify_stage7.py
python -B src/verify_stage1_report.py --run-dir results/stage1/run-004/audit
python -B src/verify_stage2_report.py --run-dir results/stage2/run-004/audit
python -B src/verify_stage3_report.py --run-dir results/stage3/run-002/audit
python -B src/verify_stage7.py --run-dir results/stage7/run-002/audit
python -B src/verify_stage7_publication.py --run-dir .
```

Stages 2 and 3 use DuckDB only for their original raw-data audits; install the
recorded version in your chosen environment with
`python -m pip install duckdb==2.0.0` before running those two test suites.
Stage 7 and the publication exporter use only the Python standard library.
Raw clusters, dataset rows, and DuckDB stores are not included, so full raw-data
reacquisition and full original-stage audits are intentionally not part of this
public package. The included checks verify the accepted aggregate artifacts and
the deterministic Stage 7/export integration.

## Package boundary

`EXCLUDED-FILES.md` lists the omitted raw, private, superseded, and environmental
material. `PACKAGE-PROVENANCE.json` records the export transform, and
`PACKAGE-MANIFEST.json` records every released file's bytes and SHA-256. The
immutable local runs were not edited: workstation paths were relativized only in
this public copy, with dependent receipts recomputed.

## License and credits

Project code is under the [MIT License](LICENSE). Original prose and figures are
under [CC BY 4.0](REPORT-LICENSE), to the extent this project can license them.
Third-party sources and limitations are recorded in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Directed by **Kenrin** ([@kenrinzero](https://github.com/kenrinzero)); built and
packaged by **Kimi K3.1 Pro**; independently reviewed across model families by
**Gemini 4 Argon (High)**. See [CREDITS.md](CREDITS.md) for the full record and
the original paper citation.
"""

THIRD_PARTY_NOTICES = """# Third-party notices

- Katherine Lee et al. (2022), *Deduplicating Training Data Makes Language Models
  Better*, is the audited source work. The ACL PDF is not included. Its preserved
  source copy carries no explicit paper licence; no unrestricted redistribution
  right is inferred. https://doi.org/10.18653/v1/2022.acl-long.577
- The authors' `google-research/deduplicate-text-datasets` repository is
  Apache-2.0 at commit 4e9888ac3f95dc4f6169867a04c4c19df02dafe3. No separate
  cluster-CSV licence was established. Cluster CSVs and dataset rows are excluded.
- Wiki-40B, C4, and LM1B public dataset metadata are used only for the documented
  split sizes and derivations. Dataset rows are excluded.
- The Google Research publication page's separate 1.68% C4 statement is quoted as
  external context with unresolved basis, not as a substitute for the PDF.
- Numerical figure bars, table cells, and short factual values are reported for
  verification and commentary. No full article text or trained model is included.
"""

EXCLUDED_FILES = """# Excluded material

The public export is allowlisted. It excludes:

- Raw cluster archives, public dataset rows, Parquet/JSON shards, and DuckDB work
  stores; only aggregate audit outputs and the raw-input manifest remain.
- The source paper PDF and its local study unit.
- Python virtual environments, caches, temporary browser/server files, design
  reference downloads, and local scratch state.
- Superseded Stage 1–3 runs and their correction lineage. Final accepted run
  reports and final progress ledgers remain; Stage 7 run-001 and run-002 remain
  to preserve the final correction and independent review chain.
- Local Atelier control-plane files, private session records, and absolute
  workstation paths. Public receipt copies use member-relative paths and have
  recomputed byte and SHA-256 receipts.
- Deferred substring, EXACTSUBSTR, memorization, perplexity, and model-quality
  inputs and experiments, which were outside the authorized project scope.
"""


def write_public_documents(root, out_dir):
    write_text(out_dir / "README.md", README)
    write_text(out_dir / "REPORT.md", publication_language(sanitize_text((root / STAGE7_RUN / "report.md").read_text(encoding="utf-8"), root)))
    write_text(out_dir / "AUDIT.md", sanitize_text((root / "planning/external-audit-2026-11-11.md").read_text(encoding="utf-8"), root))
    write_text(out_dir / "CREDITS.md", CREDITS)
    write_text(out_dir / "LICENSE", MIT_LICENSE)
    write_text(out_dir / "REPORT-LICENSE", REPORT_LICENSE)
    write_text(out_dir / "THIRD_PARTY_NOTICES.md", THIRD_PARTY_NOTICES)
    write_text(out_dir / "EXCLUDED-FILES.md", EXCLUDED_FILES)
    write_text(out_dir / ".nojekyll", "")
    write_text(out_dir / ".gitattributes", "* text=auto eol=lf\n")
    write_text(out_dir / ".gitignore", "data/raw/*\n!data/raw/MANIFEST.md\npaper/paper.pdf\n.venv/\n__pycache__/\n*.pyc\n")
    for name in ("ledger.csv", "ledger.json", "figures.json"):
        source = root / STAGE7_RUN / name
        target = out_dir / name
        if source.suffix == ".json":
            write_json(target, sanitize_value(read_json(source), root))
        else:
            write_text(target, sanitize_text(source.read_text(encoding="utf-8"), root))


def build_publication(root, out_dir):
    root = Path(root).resolve()
    out_dir = Path(out_dir)
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError(f"refusing to overwrite publication output: {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)
    provenance = []
    for source in export_files(root):
        relative = source.relative_to(root).as_posix()
        target = out_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        content = source.read_bytes()
        text = content.decode("utf-8")
        reader_files = {
            "results/stage7/run-001/audit/index.html", "results/stage7/run-001/audit/report.md",
            "results/stage7/run-002/audit/index.html", "results/stage7/run-002/audit/report.md",
        }
        if relative in reader_files:
            text = publication_language(text)
        if relative == "paper/PROVENANCE.md":
            text = text.replace("[paper.pdf](paper.pdf)", "[ACL Anthology PDF](https://aclanthology.org/2022.acl-long.577.pdf)")
        private = any(prefix in text for prefix in path_variants(root))
        if relative in reader_files:
            write_text(target, sanitize_text(text, root))
            transform = "public package-boundary wording; dependent receipts refreshed"
        elif relative == "paper/PROVENANCE.md":
            write_text(target, sanitize_text(text, root))
            transform = "canonical ACL source link replaces excluded local PDF link"
        elif b"\r" in content:
            write_text(target, sanitize_text(text.replace("\r\n", "\n").replace("\r", "\n"), root))
            transform = "UTF-8/LF normalized allowlisted copy"
        elif not private:
            target.write_bytes(content)
            transform = "byte-identical allowlisted copy"
        elif source.suffix == ".json":
            write_json(target, sanitize_value(read_json(source), root))
            transform = "member-absolute paths relativized; dependent receipts refreshed"
        else:
            write_text(target, sanitize_text(text, root))
            transform = "member-absolute paths relativized"
        provenance.append({"source": relative, "exported": relative, "transform": transform})
    nested_reader = out_dir / STAGE7_RUN / "index.html"
    root_reader_text = rewrite_root_reader(nested_reader.read_text(encoding="utf-8"))
    write_text(out_dir / "index.html", root_reader_text)
    write_public_documents(root, out_dir)
    refresh_run_receipts(out_dir)
    transform_overrides = {
        "README.md": "regenerated publication README",
        "results/stage1/run-004/audit/run-manifest.json": "sanitized outputs with recomputed receipts",
        "results/stage2/run-004/audit/run-manifest.json": "sanitized outputs with recomputed receipts",
        "results/stage3/run-002/audit/run-manifest.json": "sanitized outputs with recomputed receipts",
        "results/stage7/run-001/audit/input-manifest.json": "source-free exclusions and refreshed accepted-source receipts",
        "results/stage7/run-001/audit/run-manifest.json": "sanitized outputs with recomputed code and output receipts",
        "results/stage7/run-002/audit/input-manifest.json": "source-free exclusions and refreshed accepted-source receipts",
        "results/stage7/run-002/audit/run-manifest.json": "sanitized outputs with recomputed code and output receipts",
        "src/stage7_build.py": "source-free public verifier adaptation; actual successful hash count",
        "src/verify_stage7.py": "source-free public fixture adaptation",
        "src/stage7_publication.py": "VCS-aware publication verification",
        "src/verify_stage7_publication.py": "public checkout test portability and VCS-aware verification",
    }
    for record in provenance:
        if record["source"] in transform_overrides:
            record["transform"] = transform_overrides[record["source"]]
    provenance.extend([
        {"source": f"{STAGE7_RUN}/index.html", "exported": "index.html", "transform": "root reader; four-level relative links rewritten to repository root"},
        {"source": f"{STAGE7_RUN}/report.md", "exported": "REPORT.md", "transform": "root report copy"},
        {"source": "planning/external-audit-2026-11-11.md", "exported": "AUDIT.md", "transform": "corrected independent audit copy"},
        {"source": "publication metadata", "exported": "PACKAGE-MANIFEST.json and PACKAGE-PROVENANCE.json", "transform": "dependent run receipts recomputed; deterministic package receipts"},
    ])
    write_json(out_dir / "PACKAGE-PROVENANCE.json", {
        "schema_version": 1,
        "publication_date": "2026-11-11",
        "accepted_stage7": "run-002",
        "scientific_content_changed": False,
        "files": provenance,
    })
    outputs = {}
    for path in sorted(out_dir.rglob("*")):
        if path.is_file() and path.name != "PACKAGE-MANIFEST.json":
            outputs[path.relative_to(out_dir).as_posix()] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    write_json(out_dir / "PACKAGE-MANIFEST.json", {
        "schema_version": 1,
        "package": "lee-training-data-dedup",
        "publication_date": "2026-11-11",
        "file_count": len(outputs),
        "outputs": outputs,
    })
    return out_dir


class ReaderLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.hrefs = []
        self.external_assets = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a" and "href" in attrs:
            self.hrefs.append(attrs["href"])
        if tag == "script" and "src" in attrs:
            self.external_assets.append(attrs["src"])
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.external_assets.append(attrs.get("href"))
        if tag == "img" and "src" in attrs:
            self.external_assets.append(attrs["src"])


def verify_publication(root, run_dir):
    root = Path(root).resolve()
    run_dir = Path(run_dir)
    before = {path.relative_to(run_dir).as_posix(): path.read_bytes() for path in run_dir.rglob("*") if path.is_file() and ".git" not in path.parts}
    required = ("index.html", "README.md", "REPORT.md", "AUDIT.md", "CREDITS.md", "LICENSE", "REPORT-LICENSE", "THIRD_PARTY_NOTICES.md", "EXCLUDED-FILES.md", "PACKAGE-MANIFEST.json", "PACKAGE-PROVENANCE.json")
    for relative in required:
        assert (run_dir / relative).is_file(), f"missing publication file: {relative}"
    assert not (run_dir / "data/raw/clusters").exists()
    assert not (run_dir / "paper/paper.pdf").exists()
    assert not (run_dir / ".venv").exists()
    private_prefixes = [prefix.encode() for prefix in path_variants(root)]
    generic_markers = (
        b"C:" + b"\\\\Users\\\\", b"C:" + b"\\Users\\", b"C:" + b"/Users/",
        b"D:" + b"\\\\Project", b"D:" + b"\\Project", b"D:" + b"/Project/",
        b"/mnt/c/" + b"Users/",
    )
    for relative, content in before.items():
        path = run_dir / relative
        assert path.stat().st_size < 100_000_000, f"GitHub file-size limit: {relative}"
        assert "work" not in path.parts, f"work store included: {relative}"
        for prefix in private_prefixes + list(generic_markers):
            assert prefix not in content, f"private path survived in {relative}"
        if path.suffix in TEXT_SUFFIXES:
            content.decode("utf-8")
            assert b"\r" not in content, f"CR byte found: {relative}"
    audit = (run_dir / "AUDIT.md").read_text(encoding="utf-8")
    assert "news.Validation.org" not in audit
    assert "test_run_verifier_rejects_stale_input_manifest_hash" not in audit
    assert "556` size rows" not in audit
    link_count = 0
    for relative in ("index.html", "results/stage7/run-001/audit/index.html", "results/stage7/run-002/audit/index.html"):
        reader_path = run_dir / relative
        parser = ReaderLinks()
        parser.feed(reader_path.read_text(encoding="utf-8"))
        assert len(parser.ids) == len(set(parser.ids)), f"duplicate IDs: {relative}"
        assert not parser.external_assets, f"external runtime assets: {relative}"
        for href in parser.hrefs:
            if href.startswith("#"):
                assert href[1:] in parser.ids, f"broken anchor {href} in {relative}"
            elif not href.startswith(("https://", "http://", "mailto:")):
                target = (reader_path.parent / unquote(href)).resolve()
                assert target.is_file(), f"broken relative link {href} in {relative}"
                link_count += 1
    manifest = read_json(run_dir / "PACKAGE-MANIFEST.json")
    expected = {relative for relative in before if relative != "PACKAGE-MANIFEST.json"}
    assert set(manifest["outputs"]) == expected, "package manifest file set differs"
    assert manifest["file_count"] == len(expected)
    for relative, receipt in manifest["outputs"].items():
        content = before[relative]
        assert len(content) == receipt["bytes"], f"package byte receipt changed: {relative}"
        from hashlib import sha256 as hash_sha256
        assert hash_sha256(content).hexdigest() == receipt["sha256"], f"package hash receipt changed: {relative}"
    after = {path.relative_to(run_dir).as_posix(): path.read_bytes() for path in run_dir.rglob("*") if path.is_file() and ".git" not in path.parts}
    assert before == after, "publication verification modified files"
    print(f"PASS: publication package {len(before)} files, {link_count} root/nested relative links, privacy, receipts, UTF-8/LF verified without modification: {run_dir}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        verify_publication(args.root, args.out_dir)
    else:
        print(build_publication(args.root, args.out_dir))


if __name__ == "__main__":
    main()
