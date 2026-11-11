#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from stage1_audit import run_name, write_json, write_text


def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines.extend("| " + " | ".join(str(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


def ensure_fresh_report(out_dir):
    out_dir = Path(out_dir)
    if (out_dir / "report.md").exists() or (out_dir / "run-manifest.json").exists():
        raise FileExistsError(f"refusing to overwrite report outputs in {out_dir}")


def superseded_run(run):
    prefix, number = run.rsplit("-", 1)
    sequence = int(number)
    return None if sequence == 1 else f"{prefix}-{sequence - 1:03d}"


def render_report(root, out_dir):
    root = Path(root)
    out_dir = Path(out_dir)
    ensure_fresh_report(out_dir)
    run = run_name(out_dir)
    summary = read_json(out_dir / "derived-summary.json")
    lock = read_json(out_dir / "convention-lock.json")
    manifest = read_json(out_dir / "input-manifest.json")
    table2 = read_csv(out_dir / "table2-verdicts.csv")
    table13 = read_csv(out_dir / "table13-verdicts.csv")
    figures = read_csv(out_dir / "figure-verdicts.csv")
    edges = read_csv(out_dir / "edge-sizes.csv")
    join = summary["split_join"]
    keep = summary["keep_agreement"]

    lines = [
        f"# Stage 1 — Wiki-40B released-cluster audit ({run})",
        "",
        "**Contract:** FROZEN v1. **Population:** released archive, all splits. "
        "C4 content was not opened. The historical seed's exposed values were regeneration targets, not blind predictions.",
        "",
        "## Findings",
        "",
        "- Train-with-train is **20,465 / 2,926,536 = 0.699290…%**, rounding to **0.70%** versus the printed **0.39%**: `MISMATCH`.",
        "- Validation-with-validation and test-with-validation-arm EE both round to **0.26%** and match the printed cell at displayed precision.",
        "- Validation-with-train is **0.70%** (`MISMATCH`); test-with-train is **0.72%** (`MATCH`). This retains both evaluation arms and **does not rename or relabel** the paper's printed `valid` column.",
        "- All evaluated rule-derived retained sizes round to **2.91M**. The all-train rows are sensitivity analyses only; their rounded agreement is not evidence that the authors used that rule.",
        f"- Figure convention lock: **{lock['status']}**; primary **{lock['primary']}**; candidates **{', '.join(lock['locked_candidate_set'])}**. Match counts: dropped {lock['match_counts']['dropped']}/11, low {lock['match_counts']['low']}/11, high {lock['match_counts']['high']}/11.",
        "",
        "## Input identity and reproducibility",
        "",
        f"- Cluster archive: `{manifest['inputs'][0]['local_path']}`; {manifest['inputs'][0]['bytes']:,} bytes; SHA-256 `{manifest['inputs'][0]['sha256']}`.",
        f"- Archive member `{manifest['archive']['member']}`; {manifest['archive']['decompressed_bytes']:,} decompressed bytes; header `{','.join(manifest['archive']['header'])}`.",
        f"- Public split revision: `{manifest['split_revision']}`; 23 pinned Parquet shards; PyArrow {manifest['pyarrow']}.",
        f"- Run identity: {manifest['stage']}; command `python -B src/stage1_audit.py --out-dir results/stage1/{run}/audit`.",
        "- Raw inputs remain local. No raw cluster or dataset redistribution is authorized by this report.",
        "",
        "## Row, schema, keep and join diagnostics",
        "",
        table(
            ("Check", "Result"),
            (
                ("Physical released rows", f"{summary['physical_rows']:,}"),
                ("Unique released IDs", f"{summary['unique_ids']:,}"),
                ("Unique clusters", f"{summary['unique_clusters']:,}"),
                ("Malformed / empty-field rows", f"{summary['malformed_rows']} / {summary['empty_field_rows']}"),
                ("Duplicate released IDs / extra rows", f"{summary['duplicate_released_ids']} / {summary['duplicate_released_rows']}"),
                ("keep=0 multi / singleton", f"{keep['keep0_multi']:,} / {keep['keep0_singleton']}"),
                ("keep=1 multi / singleton", f"{keep['keep1_multi']} / {keep['keep1_singleton']:,}"),
                ("Keep-membership discrepancy rows", summary["keep_discrepancy_rows"]),
                ("Join status", join["status"]),
                ("Public unique keys", f"{join['public_unique_keys']:,}"),
                ("Duplicate public keys / rows", f"{join['duplicate_public_keys']} / {join['duplicate_public_rows']}"),
                ("Cross-split public keys / released rows", f"{join['cross_split_public_keys']} / {join['cross_split_released_rows']}"),
                ("Unmatched released / missing public rows", f"{join['unmatched_released_rows']} / {join['missing_public_rows']}"),
                ("Population balance train / validation / test", f"{join['population_balance']['train']:,} / {join['population_balance']['validation']:,} / {join['population_balance']['test']:,}"),
            ),
        ),
        "",
        "The join is exact-key, released-physical-row weighted. No normalization, trimming, deduplication, or arbitrary split assignment was applied.",
        "",
        "## Table 2 — printed versus derived",
        "",
        table(
            ("Printed target", "Arm", "Metric", "Printed %", "Numerator", "Denominator", "Rounded %", "Verdict"),
            ((row["printed_label"], row["arm"], row["metric"], row["printed_value"], row["derived_numerator"], row["derived_denominator"], row["rounded_percent"], row["verdict"]) for row in table2),
        ),
        "",
        "Exact unrounded percentages and ratios are preserved in `derived-duplication.csv` and `table2-verdicts.csv`. TT is repeated for each evaluation arm because the frozen ledger grades the complete three-column target against both arms; its value is arm-invariant.",
        "",
        "## Table 13 — original, retained sizes and removal intervals",
        "",
        table(
            ("Arm", "Rule", "Original", "Removals", "Retained", "Rounded M", "NEARDUP verdict", "Interval verdict"),
            ((row["arm"], row["rule"], row["derived_original_rounded"], row["derived_removals"], row["derived_retained"], row["derived_retained_rounded"], row["neardup_verdict"], row["interval_verdict"]) for row in table13),
        ),
        "",
        "Rule A is evaluation-preferred keep-one; Rule B is uniform train keep-one; Rule S is the all-train sensitivity. The exact-original compatible removal interval is **(11,536, 21,536]**. Every printed original cell rounds to 2.93M and matches. Full columns, including printed values and interval endpoints, are in `table13-verdicts.csv`.",
        "",
        "## Figure 8 bottom panel — all conventions",
        "",
        table(
            ("Convention", "Bin", "Printed", "Derived", "Verdict"),
            ((row["convention"], row["bin_label"], row["printed_count"], row["derived_count"], row["verdict"]) for row in figures),
        ),
        "",
        "### Exact edge sizes omitted by `dropped`",
        "",
        table(
            ("Cluster size", "Clusters", "Documents"),
            ((row["cluster_size"], row["cluster_count"], row["document_count"]) for row in edges),
        ),
        "",
        f"The locked candidate set was selected solely by Wiki-40B printed fidelity: **{', '.join(lock['locked_candidate_set'])}**. C4 cannot break or shrink this lock. C4 content was not opened.",
        "",
        "## Outputs and verification",
        "",
        "- `input-manifest.json`: URLs, revisions, byte counts, SHA-256 receipts, parser and runtime identity.",
        "- `cluster-composition.csv`, `cluster-histogram.csv`, `edge-sizes.csv`: exact cluster aggregates.",
        "- `derived-duplication.csv`, `derived-removals.csv`, `figure-counts.csv`: complete derived values and sensitivities.",
        "- `table2-verdicts.csv`, `table13-verdicts.csv`, `figure-verdicts.csv`: every printed comparison.",
        "- Diagnostic CSVs preserve empty as well as nonempty discrepancy sets.",
        "- `verify_stage1.py` checks hand-derived fixtures, all input hashes, every composition-derived metric, every figure convention, and UTF-8/LF outputs.",
        "- `verify_stage1_report.py` checks that this report carries every verdict and the frozen lock.",
        "",
        f"The original run commands are recorded below. To reproduce them, replace `{run}` with an unused run name throughout; existing named runs are immutable:", 
        "",
        "```bash",
        f"python -B src/stage1_audit.py --out-dir results/stage1/{run}/audit",
        f"python -B src/stage1_compare.py --out-dir results/stage1/{run}/audit",
        f"python -B src/verify_stage1.py --run-dir results/stage1/{run}/audit",
        f"python -B src/stage1_report.py --out-dir results/stage1/{run}/audit",
        f"python -B src/verify_stage1_report.py --run-dir results/stage1/{run}/audit",
        "```",
        "",
        "The audit command refuses to overwrite an existing output directory; corrections require a new named run.",
        "",
    ]
    report_path = out_dir / "report.md"
    write_text(report_path, "\n".join(lines))

    output_files = {}
    for path in sorted(out_dir.iterdir()):
        if path.is_file() and path.name != "run-manifest.json":
            output_files[path.name] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    write_json(out_dir / "run-manifest.json", {
        "stage": f"Stage 1 / {run}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "supersedes": superseded_run(run),
        "c4_content_opened": False,
        "outputs": output_files,
        "code_sha256": {
            path.name: sha256(path)
            for path in (root / "src").glob("stage1*.py")
        },
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
