#!/usr/bin/env python3
import argparse
import csv
import json
from decimal import Decimal, getcontext
from pathlib import Path

import duckdb

from stage1_audit import BIN_LABELS, round_half_up, write_csv, write_json

getcontext().prec = 60
COMPARISON_OUTPUTS = (
    "table2-verdicts.csv",
    "table13-verdicts.csv",
    "table11-verdicts.csv",
    "figure-verdicts.csv",
    "companion-verdicts.json",
    "convention-application.json",
    "comparison-summary.json",
    "report.md",
    "run-manifest.json",
)
TABLE2_TARGETS = {
    "TT": "table2-realnews-train-train",
    "EE": "table2-realnews-valid-valid",
    "ET": "table2-realnews-valid-train",
}


def ceiling_verdict(removals):
    return "CONTRADICTION" if int(removals) <= 2760000 else "CEILING_COMPATIBLE"


def nonexecutable_table2(targets):
    rows = []
    for metric, target_id in TABLE2_TARGETS.items():
        rows.append({
            "target_id": target_id,
            "metric": metric,
            "printed_value": targets[target_id],
            "derived_numerator": "",
            "derived_denominator": "",
            "unrounded_percent": "",
            "rounded_percent": "",
            "verdict": "NOT_EXECUTABLE_INPUT",
            "reason": "no pinned exact public original size or RealNews split mapping",
        })
    return rows


def conditional_table13(physical_rows, removals, printed_original, printed_neardup):
    original = Decimal(physical_rows) / Decimal(1000000)
    retained = physical_rows - removals
    retained_million = Decimal(retained) / Decimal(1000000)
    original_rounded = round_half_up(original, 2)
    retained_rounded = round_half_up(retained_million, 2)
    return {
        "basis": "CONDITIONAL_RELEASE_POPULATION",
        "printed_original": printed_original,
        "printed_neardup": printed_neardup,
        "derived_removals": removals,
        "derived_original_unrounded": str(original),
        "derived_original_rounded": f"{original_rounded:.2f}",
        "original_verdict": "MATCH" if original_rounded == Decimal(printed_original) else "MISMATCH",
        "derived_retained": retained,
        "derived_retained_unrounded": str(retained_million),
        "derived_retained_rounded": f"{retained_rounded:.2f}",
        "neardup_verdict": "MATCH" if retained_rounded == Decimal(printed_neardup) else "MISMATCH",
        "direct_train_removal_verdict": "NOT_EXECUTABLE_INPUT",
    }


def printed_rounding_companion():
    return {
        "section5_rounding": {
            "printed_table2": "14.35%",
            "printed_section5_3": "14.4%",
            "verdict": "MATCH",
            "basis": "printed ROUND_HALF_UP consistency, not reproduction of the unavailable split cell",
        },
        "tokens": {
            "original": "NOT_EXECUTABLE_INPUT",
            "neardup": "NOT_EXECUTABLE_INPUT",
        },
        "token_reason": "cluster IDs and assignments cannot reproduce the paper's 50k BPE token counts",
    }


def precision(value):
    return len(value.partition(".")[2])


def grade_url_value(url, printed_total, printed_frac, stats):
    if stats is None:
        return {
            "printed_url": url,
            "derived_url": "",
            "printed_total": printed_total,
            "derived_total": 0,
            "total_verdict": "MISMATCH" if int(printed_total) != 0 else "MATCH",
            "printed_frac": printed_frac,
            "derived_frac_keep0": "",
            "derived_membership_frac": "",
            "frac_verdict": "NOT_EXECUTABLE_INPUT",
        }
    total, keep0, multi = (int(value) for value in stats)
    fraction = Decimal(keep0) / Decimal(total) if total else None
    membership = Decimal(multi) / Decimal(total) if total else None
    rounded = round_half_up(fraction, precision(printed_frac)) if fraction is not None else None
    return {
        "printed_url": url,
        "derived_url": url,
        "printed_total": printed_total,
        "derived_total": total,
        "total_verdict": "MATCH" if total == int(printed_total) else "MISMATCH",
        "printed_frac": printed_frac,
        "derived_frac_keep0": str(fraction) if fraction is not None else "",
        "derived_membership_frac": str(membership) if membership is not None else "",
        "frac_verdict": ("MATCH" if rounded == Decimal(printed_frac) else "MISMATCH") if rounded is not None else "NOT_EXECUTABLE_INPUT",
    }


def grade_figures(figure_rows, targets):
    verdicts = []
    for row in figure_rows:
        bin_index = int(row["bin_index"])
        target_id = f"fig8-realnews-bin-{bin_index:02d}"
        printed = int(targets[target_id])
        derived = int(row["cluster_count"])
        verdicts.append({
            "convention": row["convention"],
            "bin_index": bin_index,
            "bin_label": row.get("bin_label", BIN_LABELS[bin_index - 1]),
            "target_id": target_id,
            "printed_count": printed,
            "derived_count": derived,
            "verdict": "MATCH" if derived == printed else "MISMATCH",
        })
    return verdicts


def ensure_fresh_comparison(out_dir):
    out_dir = Path(out_dir)
    existing = [name for name in COMPARISON_OUTPUTS if (out_dir / name).exists()]
    if existing:
        raise FileExistsError(f"refusing to overwrite Stage 3 comparison outputs in {out_dir}: {existing}")


def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def compare(root, out_dir):
    root = Path(root)
    out_dir = Path(out_dir)
    ensure_fresh_comparison(out_dir)
    target_rows = read_csv(root / "paper/targets/printed-targets.csv")
    targets = {row["target_id"]: row for row in target_rows}
    printed_values = {target_id: row["printed_value"] for target_id, row in targets.items()}

    table2_rows = nonexecutable_table2(printed_values)
    write_csv(out_dir / "table2-verdicts.csv", tuple(table2_rows[0]), table2_rows)

    ceiling = json.loads((out_dir / "removal-ceiling.json").read_text(encoding="utf-8"))
    summary = json.loads((out_dir / "derived-summary.json").read_text(encoding="utf-8"))
    removals = int(ceiling["removals"])
    ceiling_result = ceiling_verdict(removals)
    table13_row = conditional_table13(
        int(ceiling["physical_rows"]),
        removals,
        targets["table13-realnews-examples-original"]["printed_value"],
        targets["table13-realnews-examples-neardup"]["printed_value"],
    )
    write_csv(out_dir / "table13-verdicts.csv", tuple(table13_row), [table13_row])
    companion = printed_rounding_companion()
    companion["split_free_ceiling"] = {
        "derived_removals": removals,
        "printed_difference_interval": {"lower_exclusive": 2760000, "upper_exclusive": 2780000},
        "verdict": ceiling_result,
        "basis": "split-free keep-one ceiling; CEILING_COMPATIBLE is not a train-size match",
    }
    companion["table13_conditional_basis"] = "measured released archive rows, not a verified exact public original train size"
    write_json(out_dir / "companion-verdicts.json", companion)

    figure_verdicts = grade_figures(read_csv(out_dir / "figure-counts.csv"), printed_values)
    write_csv(out_dir / "figure-verdicts.csv", tuple(figure_verdicts[0]), figure_verdicts)
    figure_matches = {
        convention: sum(row["verdict"] == "MATCH" for row in figure_verdicts if row["convention"] == convention)
        for convention in ("dropped", "low", "high")
    }

    con = duckdb.connect(str(out_dir / "work/realnews.duckdb"), read_only=True)
    table11_rows = []
    for index in range(1, 20):
        total_target = targets[f"table11-realnews-r{index:02d}-total"]
        frac_target = targets[f"table11-realnews-r{index:02d}-frac"]
        url = total_target["split_or_arm"]
        stats = con.execute("SELECT total, keep0, multi_membership FROM url_stats WHERE url = ?", [url]).fetchone()
        row = grade_url_value(url, total_target["printed_value"], frac_target["printed_value"], stats)
        table11_rows.append({"row": index, **row})
    con.close()
    write_csv(out_dir / "table11-verdicts.csv", tuple(table11_rows[0]), table11_rows)

    write_json(out_dir / "convention-application.json", {
        "primary": "dropped",
        "faithful_figure_output": "figure-counts.csv convention=dropped",
        "alternatives": "low/high retained as sensitivities; no convention is selected from RealNews agreement",
        "stage1_lock": "singleton dropped",
        "realnews_figure_match_counts": figure_matches,
    })
    write_json(out_dir / "comparison-summary.json", {
        "table2_not_executable": sum(row["verdict"] == "NOT_EXECUTABLE_INPUT" for row in table2_rows),
        "table13_basis": table13_row["basis"],
        "table13_original_verdict": table13_row["original_verdict"],
        "table13_neardup_verdict": table13_row["neardup_verdict"],
        "ceiling_verdict": ceiling_result,
        "ceiling_removals": removals,
        "figure_match_counts": figure_matches,
        "table11_total_matches": sum(row["total_verdict"] == "MATCH" for row in table11_rows),
        "table11_total_mismatches": sum(row["total_verdict"] == "MISMATCH" for row in table11_rows),
        "table11_frac_matches": sum(row["frac_verdict"] == "MATCH" for row in table11_rows),
        "table11_frac_mismatches": sum(row["frac_verdict"] == "MISMATCH" for row in table11_rows),
        "table11_frac_not_executable": sum(row["frac_verdict"] == "NOT_EXECUTABLE_INPUT" for row in table11_rows),
        "divergence_status": summary["divergence_status"],
        "duplicate_released_ids": summary["duplicate_released_ids"],
    })
    print(json.dumps({
        "rows": ceiling["physical_rows"],
        "ceiling": {"removals": removals, "verdict": ceiling_result},
        "figure_matches": figure_matches,
        "table11_total_matches": sum(row["total_verdict"] == "MATCH" for row in table11_rows),
        "table11_frac_matches": sum(row["frac_verdict"] == "MATCH" for row in table11_rows),
    }, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    compare(args.root, args.out_dir)


if __name__ == "__main__":
    main()
