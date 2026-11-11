#!/usr/bin/env python3
import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from stage1_audit import run_name, sha256, write_json, write_text
from stage1_report import ensure_fresh_report, superseded_run, table


def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def render_report(root, out_dir):
    root = Path(root)
    out_dir = Path(out_dir)
    ensure_fresh_report(out_dir)
    run = run_name(out_dir)
    manifest = read_json(out_dir / "input-manifest.json")
    summary = read_json(out_dir / "derived-summary.json")
    ceiling = read_json(out_dir / "removal-ceiling.json")
    comparison = read_json(out_dir / "comparison-summary.json")
    convention = read_json(out_dir / "convention-application.json")
    companion = read_json(out_dir / "companion-verdicts.json")
    table2 = read_csv(out_dir / "table2-verdicts.csv")
    table13 = read_csv(out_dir / "table13-verdicts.csv")[0]
    table11 = read_csv(out_dir / "table11-verdicts.csv")
    top20 = read_csv(out_dir / "table11-top20.csv")
    figures = read_csv(out_dir / "figure-verdicts.csv")
    edges = read_csv(out_dir / "edge-sizes.csv")
    keep = summary["keep_agreement"]
    receipt = manifest["inputs"][0]

    lines = [
        f"# Stage 3 — RealNews released-cluster audit ({run})",
        "",
        "**Contract:** FROZEN v1. **Population:** released archive, all splits. The historical seed's exposed values were regeneration targets, not blind predictions.",
        "",
        "## Input identity and row diagnostics",
        "",
        f"Cluster archive `data/raw/clusters/realnews.tar.gz`: {receipt['bytes']:,} bytes; SHA-256 `{receipt['sha256']}`. Streamed member `{manifest['archive']['member']}` ({manifest['archive']['decompressed_bytes']:,} decompressed bytes) without extracting the full CSV. Header: `{','.join(manifest['archive']['header'])}`.",
        "",
        table(("Check", "Result"), (
            ("Physical released rows", f"{summary['physical_rows']:,}"),
            ("Unique released IDs", f"{summary['unique_ids']:,}"),
            ("Unique clusters", f"{summary['unique_clusters']:,}"),
            ("Malformed / empty-field rows", f"{summary['malformed_rows']} / {summary['empty_field_rows']}"),
            ("Duplicate released IDs / extra rows", f"{summary['duplicate_released_ids']:,} / {summary['duplicate_released_rows']:,}"),
            ("Singleton documents", f"{summary['singleton_documents']:,}"),
            ("Multi-document clusters / documents", f"{summary['multi_clusters']:,} / {summary['multi_documents']:,}"),
            ("keep=0 multi / singleton", f"{keep['keep0_multi']:,} / {keep['keep0_singleton']:,}"),
            ("keep=1 multi / singleton", f"{keep['keep1_multi']:,} / {keep['keep1_singleton']:,}"),
            ("Keep-membership discrepancy rows", f"{summary['keep_discrepancy_rows']:,}"),
            ("Keep-membership status", summary["divergence_status"]),
            ("URL divergence rows", f"{summary['url_divergence_count']:,}"),
        )),
        "",
        "IDs are compared as exact UTF-8 strings without host, scheme, path or URL normalization. Duplicate physical IDs remain in the estimand. Raw inputs and the disk-backed row store remain local.",
        "",
        "## Split-free removal ceiling",
        "",
        f"Multi-document rows **{ceiling['multi_documents']:,}** minus multi-document clusters **{ceiling['multi_clusters']:,}** give **U = {ceiling['removals']:,}**. The frozen keep-one formula is `{ceiling['formula']}`.",
        "",
        f"The independently rounded printed difference implies removals in **(2,760,000, 2,780,000)**. Because the smallest compatible integer is 2,760,001, the verdict for this U is **{comparison['ceiling_verdict']}**. `CEILING_COMPATIBLE` is only a ceiling result, not a train-size match.",
        "",
        "## Table 2 — split-dependent cells",
        "",
        table(("Metric", "Printed %", "Derived", "Verdict"), (
            (row["metric"], row["printed_value"], row["rounded_percent"], row["verdict"])
            for row in table2
        )),
        "",
        "All three cells are `NOT_EXECUTABLE_INPUT`: no exact public original size or RealNews split mapping is pinned. No train/validation/test assignments are inferred from the released archive.",
        "",
        "## Table 13 — conditional release-population comparison",
        "",
        f"Basis: **{table13['basis']}** — {companion['table13_conditional_basis']}. This is not a verified public train population and not a verified public train-size reproduction.",
        "",
        table(("Basis", "Original M", "Original verdict", "Removals", "Retained", "Retained M", "NEARDUP verdict", "Direct train removal"), (
            (table13["basis"], table13["derived_original_rounded"], table13["original_verdict"], table13["derived_removals"], table13["derived_retained"], table13["derived_retained_rounded"], table13["neardup_verdict"], table13["direct_train_removal_verdict"]),
        )),
        "",
        "### Companion dispositions",
        "",
        f"- §5.3 printed rounding: **{companion['section5_rounding']['printed_table2']} → {companion['section5_rounding']['printed_section5_3']}**, **{companion['section5_rounding']['verdict']}** as printed ROUND_HALF_UP consistency, not reproduction of the unavailable split cell.",
        f"- Table 13 ORIGINAL and NEARDUP token cells: **{companion['tokens']['original']}** and **{companion['tokens']['neardup']}**; {companion['token_reason']}.",
        "",
        "## Table 11 — exact released-ID audit",
        "",
        "Faithful `Frac Dups` is physical `keep=0 / # Total`; multi-document membership is sensitivity only. Direct lookups include every released ID, including IDs occurring only with `keep=1`. Exact-ID mismatches do not by themselves reconstruct or contradict a source-native host-level aggregation; no normalization was introduced.",
        "",
        table(("Row", "Printed URL", "Printed total", "Derived total", "Total verdict", "Printed frac", "Derived frac", "Frac verdict"), (
            (row["row"], row["printed_url"], row["printed_total"], row["derived_total"], row["total_verdict"], row["printed_frac"], row["derived_frac_keep0"], row["frac_verdict"])
            for row in table11
        )),
        "",
        "### Derived ranking — first five of up to 20",
        "",
        "The separate derived ranking includes every ID with `total >= 10`, then sorts by faithful unrounded fraction descending, total descending and URL bytewise ascending. It does not apply C4's all-duplicate-only filter.",
        "",
        table(("Rank", "URL", "Total", "keep0", "Frac Dups", "Membership fraction"), (
            (row["rank"], row["url"], row["total"], row["keep0"], row["frac_dups"], row["membership_fraction"])
            for row in top20[:5]
        )),
        "",
        "## Figure 8(b) — all predeclared conventions",
        "",
        f"Match counts: dropped {convention['realnews_figure_match_counts']['dropped']}/11, low {convention['realnews_figure_match_counts']['low']}/11, high {convention['realnews_figure_match_counts']['high']}/11. The Stage 1 primary remains `dropped`; RealNews agreement does not select a new convention.",
        "",
        table(("Convention", "Bin", "Printed", "Derived", "Verdict"), (
            (row["convention"], row["bin_label"], row["printed_count"], row["derived_count"], row["verdict"])
            for row in figures
        )),
        "",
        "### Exact omitted edge sizes",
        "",
        table(("Cluster size", "Clusters", "Documents"), (
            (row["cluster_size"], row["cluster_count"], row["document_count"])
            for row in edges
        )),
        "",
        "## Verification and reproduction",
        "",
        f"- Audit runtime: {manifest['elapsed_seconds']:.3f} seconds; local work-store bytes at receipt: {manifest['scratch_bytes']:,}.",
        "- `verify_stage3.py`: hand-derived fixtures, archive identity, histogram, cluster/URL diagnostics, figures, ceiling, ranking, conditional arithmetic and comparison checks.",
        "- `verify_stage3_report.py`: read-only reader-claim, output-hash and code-receipt checks.",
        "- Method provenance: shared receipt, rounding, figure and table helpers are imported from Stages 1–2; the RealNews streaming audit and comparisons are new for Stage 3.",
        "- Reports and aggregate outputs contain no full document text. Publication remains a separate rights and user decision.",
        "",
        f"The original commands are recorded below. To reproduce, replace `{run}` with an unused run name throughout; existing named runs are immutable:",
        "",
        "```bash",
        ".venv/Scripts/python -B src/verify_stage3.py",
        f".venv/Scripts/python -B src/stage3_audit.py --out-dir results/stage3/{run}/audit",
        f".venv/Scripts/python -B src/verify_stage3.py --full --run-dir results/stage3/{run}/audit",
        f".venv/Scripts/python -B src/stage3_compare.py --out-dir results/stage3/{run}/audit",
        f".venv/Scripts/python -B src/stage3_report.py --out-dir results/stage3/{run}/audit",
        f".venv/Scripts/python -B src/verify_stage3.py --full --run-dir results/stage3/{run}/audit",
        f".venv/Scripts/python -B src/verify_stage3_report.py --run-dir results/stage3/{run}/audit",
        "```",
        "",
    ]
    report_path = out_dir / "report.md"
    write_text(report_path, "\n".join(lines))
    outputs = {}
    for path in sorted(out_dir.iterdir()):
        if path.is_file() and path.name != "run-manifest.json":
            outputs[path.name] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    code_names = (
        "stage1_audit.py",
        "stage1_report.py",
        "stage3_audit.py",
        "stage3_compare.py",
        "stage3_report.py",
        "verify_stage3.py",
        "verify_stage3_report.py",
    )
    write_json(out_dir / "run-manifest.json", {
        "stage": f"Stage 3 / {run}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "supersedes": superseded_run(run),
        "realnews_content_opened": True,
        "work_store": "work/realnews.duckdb (local scratch and independent verification input; not a reader output)",
        "outputs": outputs,
        "code_sha256": {name: sha256(root / "src" / name) for name in code_names},
    })
    return report_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    print(render_report(args.root, args.out_dir))


if __name__ == "__main__":
    main()
