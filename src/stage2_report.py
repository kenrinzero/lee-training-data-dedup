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
    identity = read_json(out_dir / "release-identity.json")
    manifest = read_json(out_dir / "input-manifest.json")
    figures = read_csv(out_dir / "figure-verdicts.csv")
    full = identity["status"] == "IDENTITY_HOLD"
    lines = [
        f"# Stage 2 — C4 released-cluster audit ({run})",
        "",
        "**Contract:** FROZEN v1. **Population:** released archive, all splits. "
        "Stage 1 locked `dropped` as the sole primary before any C4 content was opened.",
        "",
        "## Release identity",
        "",
        f"**{identity['status']}**. Physical rows **{identity['physical_rows']:,}** versus required **{identity['expected_rows']:,}**. "
        f"Figure matches: dropped {identity['figure_match_counts']['dropped']}/11, low {identity['figure_match_counts']['low']}/11, high {identity['figure_match_counts']['high']}/11.",
        "",
        f"Cluster archive `data/raw/clusters/c4.tar.gz`: {manifest['inputs'][0]['bytes']:,} bytes; SHA-256 `{manifest['inputs'][0]['sha256']}`. "
        f"Streamed member `{manifest['archive']['member']}` ({manifest['archive']['decompressed_bytes']:,} decompressed bytes) without extracting the full CSV.",
        "",
        "The historical seed's exposed values were regeneration targets, not blind predictions. The kill test precedes every faithful printed-cell verdict.",
        "",
    ]
    if not full:
        lines.extend([
            "The release-identity branch stopped the faithful C4 cluster reproduction. Required unavailable cells receive `KILL_RELEASE_IDENTITY`; no convention, duplicate-row or join rule was tuned to force agreement.",
            "",
            "The independent Step-0 printed arithmetic remains valid, including the C4 removal-ceiling contradiction and the corrected Figure 1 train-removal interval.",
            "",
        ])
    else:
        summary = read_json(out_dir / "derived-summary.json")
        full_manifest = read_json(out_dir / "full-input-manifest.json")
        table2 = read_csv(out_dir / "table2-verdicts.csv")
        table13 = read_csv(out_dir / "table13-verdicts.csv")
        section5 = read_csv(out_dir / "section5-verdicts.csv")
        table11 = read_csv(out_dir / "table11-verdicts.csv")
        top20 = read_csv(out_dir / "table11-top20.csv")
        random_verdict = read_json(out_dir / "random-split-verdict.json")
        companion = read_json(out_dir / "companion-verdicts.json")
        join = summary["split_join"]
        lines.extend([
            "## Split provenance and join diagnostics",
            "",
            f"Split source: `{full_manifest['split_source']}`, root revision `{full_manifest['split_root_sha']}`. "
            f"The {full_manifest['streamed_train_shards']} train shards total {full_manifest['streamed_train_bytes']:,} compressed bytes and were streamed once per acquisition attempt under Amendment A1; exact URLs and per-shard SHA-256 receipts are retained without compressed document bodies. "
            f"Validation uses two full Parquet files totaling {sum(row['bytes'] for row in full_manifest['inputs']):,} bytes. The 2,207,027-row partial Parquet train was excluded. The preserved public URL store was hash-checked before processing.",
            "",
            table(("Check", "Result"), (
                ("Join status", join["status"]),
                ("Public train / validation rows", f"{join['public_physical_counts']['train']:,} / {join['public_physical_counts']['validation']:,}"),
                ("Population balance train / validation", f"{join['population_balance']['train']:,} / {join['population_balance']['validation']:,}"),
                ("Public unique keys", f"{join['public_unique_keys']:,}"),
                ("Duplicate public keys / rows", f"{join['duplicate_public_keys']:,} / {join['duplicate_public_rows']:,}"),
                ("Duplicate released URLs / extra rows", f"{join['duplicate_released_urls']:,} / {join['duplicate_released_rows']:,}"),
                ("Cross-split public keys / released rows", f"{join['cross_split_public_keys']:,} / {join['cross_split_released_rows']:,}"),
                ("Unmatched released / missing public rows", f"{join['unmatched_released_rows']:,} / {join['missing_public_rows']:,}"),
                ("Keep-membership status", summary["divergence_status"]),
                ("URL divergence rows", f"{summary['url_divergence_count']:,}"),
            )),
            "",
            "Joins compare exact UTF-8 URL strings without normalization. Repeated public keys map through one URL mask, so they never multiply released rows. Cross-split and unmatched keys are not arbitrarily assigned. The estimand is released-physical-row weighted.",
            "",
            "## Table 2 — direct observed cluster membership",
            "",
            table(("Metric", "Printed %", "Numerator", "Denominator", "Rounded %", "Verdict"), (
                (row["metric"], row["printed_value"], row["derived_numerator"], row["derived_denominator"], row["rounded_percent"], row["verdict"])
                for row in table2
            )),
            "",
            "TT means train-with-train; EE means validation-with-validation; ET means validation-with-train. Exact unrounded values are in `table2-verdicts.csv`.",
            "",
            "### Secondary random-split EE check",
            "",
            f"Expected numerator **{random_verdict['expected_numerator']}**; unrounded percent **{random_verdict['unrounded_percent']}**; rounded **{random_verdict['rounded_percent']}%** versus printed **{random_verdict['printed_value']}%**: **{random_verdict['verdict']}**. "
            "This assumes a uniform fixed-size validation split and is separate from the direct observed EE cell. The expectation was serialized before the comparison routine read the printed 1.59%.",
            "",
            "## Table 13 — original, removals and retained train size",
            "",
            table(("Rule", "Original M", "Removals", "Retained", "Retained M", "NEARDUP", "Interval"), (
                (row["rule"], row["derived_original_rounded"], row["derived_removals"], row["derived_retained"], row["derived_retained_rounded"], row["neardup_verdict"], row["interval_verdict"])
                for row in table13
            )),
            "",
            "Rule A is evaluation-preferred keep-one; Rule B is uniform train keep-one; Rule S is the all-train sensitivity. Rules A and B are alternative interpretations, not observed author deletions; rounded agreement does not identify the authors' rule. The exact-original removal interval is **(14,383,892, 14,393,892]**.",
            "",
            "### Companion dispositions required by the coverage ledger",
            "",
            f"- §5.3 printed rounding: **{companion['section5_rounding']['printed_table2']} → {companion['section5_rounding']['printed_section5_3']}**, **{companion['section5_rounding']['verdict']}** as printed rounding consistency, not a separate split result.",
            f"- Independently rounded printed-difference interval **(14,380,000, 14,400,000)**: A **{companion['printed_difference_interval']['A']}**, B **{companion['printed_difference_interval']['B']}**, S **{companion['printed_difference_interval']['S']}**. This is distinct from the exact-original interval above.",
            f"- Table 13 ORIGINAL and NEARDUP token cells: **{companion['tokens']['original']}** and **{companion['tokens']['neardup']}**; {companion['token_reason']}.",
            f"- Step-0 removal-ceiling companion: **{companion['step0_companions']['c4_removal_ceiling']['verdict']}**, robust minimum shortfall **{companion['step0_companions']['c4_removal_ceiling']['robust_minimum_shortfall']}**, preserved in `planning/step0/arithmetic.json` under `c4_removal_ceiling`.",
            f"- Step-0 Figure 1 companion: **{companion['step0_companions']['fig1_bounds']['verdict']}**, conditional train-removal interval **[{companion['step0_companions']['fig1_bounds']['train_removal_lower']:,}, {companion['step0_companions']['fig1_bounds']['train_removal_upper']:,}]**, preserved under `fig1_bounds`.",
            "",
            "## §5.1 cluster facts",
            "",
            table(("Claim", "Printed", "Derived", "Verdict"), (
                (row["claim"], row["printed_value"], row["derived_value"], row["verdict"])
                for row in section5
            )),
            "",
            "Size 5,000 is reported separately from the prose's 'over 5,000'. Figure bars count clusters, not documents.",
            "",
            "## Table 11 — printed URL rows",
            "",
            "Faithful `Frac Dups` is physical `keep=0 / # Total`; the multi-document-cluster fraction is diagnostic only. The twentieth printed URL is absent and remains `SOURCE_MISSING`; a derived ranking candidate is not a recovered printed value.",
            "",
            "These zero exact-ID counts test only exact full-URL identity. They do **not** reproduce the source-native host-level estimand or establish 19 substantive numerical contradictions in the paper's host-like aggregation. Host extraction, scheme/path removal or other normalization would require a dated amendment with prior-exposure disclosure and a new run; none was introduced.",
            "",
            table(("Row", "Printed URL", "Printed total", "Derived total", "Total verdict", "Printed frac", "Derived frac", "Frac verdict"), (
                (row["row"], row["printed_url"], row["printed_total"], row["derived_total"], row["total_verdict"], row["printed_frac"], row["derived_frac_keep0"], row["frac_verdict"])
                for row in table11
            )),
            "",
            "### Derived full-URL diagnostic — first five of 20",
            "",
            "Candidates were first restricted to URLs whose unrounded `keep=0` share equals 1, then sorted by total descending and URL bytewise ascending. Because every released full URL is unique, every eligible total is 1. This is a full-URL diagnostic, **not** a reconstruction of the printed host-like frequency ranking. The remaining 15 rows are preserved in `table11-top20.csv`.",
            "",
            table(("Rank", "URL", "Total", "keep0", "Membership fraction"), (
                (row["rank"], row["url"], row["total"], row["keep0"], row["membership_fraction"])
                for row in top20[:5]
            )),
            "",
        ])
    lines.extend([
        "## Figure 1 — all predeclared conventions",
        "",
        table(("Convention", "Bin", "Printed", "Derived", "Verdict"), (
            (row["convention"], row["bin_label"], row["printed_count"], row["derived_count"], row["verdict"])
            for row in figures
        )),
        "",
        "The faithful convention-dependent output uses `dropped`; `low` and `high` remain sensitivities and cannot displace the Stage 1 lock.",
        "",
        "## Verification and reproduction",
        "",
        "- `verify_stage2.py`: hand-derived identity, random-split and ranking fixtures; source hashes; histogram-derived identity; full split receipts; direct metrics, removals, cluster facts, random expectation and Table 11 ranking.",
        "- `verify_stage2_report.py`: read-only reader-claim, output-hash and code-receipt checks.",
        "- Method provenance: shared `figure_counts`, receipt and output helpers are imported from Stage 1; the streamed DuckDB audit and comparisons are new for Stage 2.",
        "- Raw inputs and the disk-backed row store remain local. Reports and aggregate CSV/JSON outputs contain no full document text.",
        "",
        f"The original commands are recorded below. To reproduce, replace `{run}` with an unused run name throughout; existing named runs are immutable:",
        "",
        "```bash",
        f"python -B src/stage2_identity.py --out-dir results/stage2/{run}/audit",
        f"python -B src/verify_stage2.py --run-dir results/stage2/{run}/audit",
        f".venv/Scripts/python -B src/stage2_acquire.py --out-dir results/stage2/{run}",
        f".venv/Scripts/python -B src/stage2_audit.py --out-dir results/stage2/{run}/audit",
        f".venv/Scripts/python -B src/stage2_compare.py --out-dir results/stage2/{run}/audit",
        f"python -B src/stage2_finalize.py --out-dir results/stage2/{run}/audit",
        f".venv/Scripts/python -B src/verify_stage2.py --full --run-dir results/stage2/{run}/audit",
        f"python -B src/stage2_report.py --out-dir results/stage2/{run}/audit",
        f"python -B src/verify_stage2_report.py --run-dir results/stage2/{run}/audit",
        "```",
        "",
    ])
    report_path = out_dir / "report.md"
    write_text(report_path, "\n".join(lines))
    outputs = {}
    for path in sorted(out_dir.iterdir()):
        if path.is_file() and path.name != "run-manifest.json":
            outputs[path.name] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    code_names = (
        "stage1_audit.py",
        "stage2_identity.py",
        "stage2_acquire.py",
        "stage2_audit.py",
        "stage2_compare.py",
        "stage2_finalize.py",
        "stage2_report.py",
        "verify_stage2.py",
        "verify_stage2_report.py",
    )
    write_json(out_dir / "run-manifest.json", {
        "stage": f"Stage 2 / {run}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "supersedes": superseded_run(run),
        "release_identity": identity["status"],
        "c4_content_opened": True,
        "work_store": "work/c4.duckdb (local scratch and independent verification input; not a reader output)",
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
