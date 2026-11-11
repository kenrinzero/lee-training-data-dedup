#!/usr/bin/env python3
import argparse
import csv
import json
from decimal import Decimal, getcontext
from pathlib import Path

from stage1_audit import round_half_up, write_csv, write_json

getcontext().prec = 60
COMPARISON_OUTPUTS = (
    "table2-verdicts.csv",
    "table13-verdicts.csv",
    "section5-verdicts.csv",
    "table11-verdicts.csv",
    "random-split-verdict.json",
    "convention-application.json",
    "comparison-summary.json",
    "companion-verdicts.json",
    "report.md",
    "run-manifest.json",
)


def companion_verdicts(removal_rows):
    interval = {}
    for row in removal_rows:
        removals = int(row["derived_removals"])
        interval[row["rule"]] = "CONSISTENT_INTERVAL" if 14380000 < removals < 14400000 else "CONTRADICTION"
    return {
        "section5_rounding": {
            "printed_table2": "4.60%",
            "printed_section5_3": "4.6%",
            "verdict": "MATCH",
            "basis": "printed ROUND_HALF_UP consistency, not a separate split result",
        },
        "printed_difference_interval": interval,
        "printed_difference_interval_bounds": {"lower_exclusive": 14380000, "upper_exclusive": 14400000},
        "tokens": {"original": "NOT_EXECUTABLE_INPUT", "neardup": "NOT_EXECUTABLE_INPUT"},
        "token_reason": "cluster IDs and assignments cannot reproduce the paper's 50k BPE token counts",
    }


def ensure_fresh_comparison(out_dir):
    out_dir = Path(out_dir)
    existing = [name for name in COMPARISON_OUTPUTS if (out_dir / name).exists()]
    if existing:
        raise FileExistsError(f"refusing to overwrite Stage 2 comparison outputs in {out_dir}: {existing}")


def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def precision(value):
    return len(value.partition(".")[2])


def compare(root, out_dir):
    root = Path(root)
    out_dir = Path(out_dir)
    ensure_fresh_comparison(out_dir)
    random_expectation = read_json(out_dir / "random-split-ee.json")
    targets = {row["target_id"]: row for row in read_csv(root / "paper/targets/printed-targets.csv")}
    identity = read_json(out_dir / "release-identity.json")
    assert identity["status"] == "IDENTITY_HOLD"
    summary = read_json(out_dir / "derived-summary.json")
    join_status = summary["split_join"]["status"]
    duplication = {row["metric"]: row for row in read_csv(out_dir / "derived-duplication.csv")}
    target_ids = {
        "TT": "table2-c4-train-train",
        "EE": "table2-c4-valid-valid",
        "ET": "table2-c4-valid-train",
    }
    table2_rows = []
    for metric in ("TT", "EE", "ET"):
        target = targets[target_ids[metric]]
        derived = duplication[metric]
        numerator, denominator = int(derived["numerator"]), int(derived["denominator"])
        percent = Decimal(numerator) * 100 / Decimal(denominator)
        rounded = round_half_up(percent, 2)
        verdict = "MATCH" if rounded == Decimal(target["printed_value"]) else "MISMATCH"
        if join_status != "COMPLETE":
            verdict = "INDETERMINATE_JOIN"
        table2_rows.append({
            "target_id": target["target_id"],
            "metric": metric,
            "printed_value": target["printed_value"],
            "derived_numerator": numerator,
            "derived_denominator": denominator,
            "unrounded_percent": str(percent),
            "rounded_percent": f"{rounded:.2f}",
            "verdict": verdict,
        })
    write_csv(out_dir / "table2-verdicts.csv", tuple(table2_rows[0]), table2_rows)

    random_percent = Decimal(random_expectation["probability"]) * 100
    random_rounded = round_half_up(random_percent, 2)
    write_json(out_dir / "random-split-verdict.json", {
        "printed_target": "table2-c4-valid-valid",
        "printed_value": targets["table2-c4-valid-valid"]["printed_value"],
        "expected_numerator": random_expectation["expected_numerator"],
        "unrounded_percent": str(random_percent),
        "rounded_percent": f"{random_rounded:.2f}",
        "verdict": "MATCH" if random_rounded == Decimal(targets["table2-c4-valid-valid"]["printed_value"]) else "MISMATCH",
        "basis": random_expectation["evaluation"],
    })

    original = Decimal(364868892) / Decimal(1000000)
    original_rounded = round_half_up(original, 2)
    original_printed = Decimal(targets["table13-c4-examples-original"]["printed_value"])
    neardup_printed = Decimal(targets["table13-c4-examples-neardup"]["printed_value"])
    table13_rows = []
    for derived in read_csv(out_dir / "derived-removals.csv"):
        removals, retained = int(derived["removals"]), int(derived["retained"])
        retained_rounded = round_half_up(Decimal(retained) / Decimal(1000000), 2)
        neardup_verdict = "MATCH" if retained_rounded == neardup_printed else "MISMATCH"
        interval_verdict = "CONSISTENT_INTERVAL" if 14383892 < removals <= 14393892 else "CONTRADICTION"
        if join_status != "COMPLETE":
            neardup_verdict = interval_verdict = "INDETERMINATE_JOIN"
        table13_rows.append({
            "arm": "validation",
            "rule": derived["rule"],
            "printed_original": str(original_printed),
            "derived_original_unrounded": str(original),
            "derived_original_rounded": f"{original_rounded:.2f}",
            "original_verdict": "MATCH" if original_rounded == original_printed else "MISMATCH",
            "printed_neardup": str(neardup_printed),
            "derived_removals": removals,
            "derived_retained": retained,
            "derived_retained_rounded": f"{retained_rounded:.2f}",
            "neardup_verdict": neardup_verdict,
            "removal_interval_exclusive_lower": 14383892,
            "removal_interval_inclusive_upper": 14393892,
            "interval_verdict": interval_verdict,
        })
    write_csv(out_dir / "table13-verdicts.csv", tuple(table13_rows[0]), table13_rows)
    companion = companion_verdicts(table13_rows)
    companion["step0_companions"] = {
        "c4_removal_ceiling": "planning/step0/arithmetic.json derivations.c4_removal_ceiling",
        "fig1_bounds": "planning/step0/arithmetic.json derivations.fig1_bounds",
    }
    write_json(out_dir / "companion-verdicts.json", companion)

    facts = read_json(out_dir / "cluster-facts.json")
    pair_rounded = round_half_up(Decimal(facts["pair_clusters"]) / Decimal(1000000), 1)
    section5_rows = [
        {"claim": "approximately 1.8M pair clusters", "printed_value": "1.8", "derived_value": facts["pair_clusters"], "rounded_derived": f"{pair_rounded:.1f}", "verdict": "MATCH" if pair_rounded == Decimal("1.8") else "MISMATCH"},
        {"claim": "majority are pair clusters", "printed_value": "majority", "derived_value": facts["pair_majority"], "rounded_derived": facts["pair_majority"], "verdict": "MATCH" if facts["pair_majority"] else "MISMATCH"},
        {"claim": "clusters over 5000", "printed_value": 280, "derived_value": facts["clusters_over_5000"], "rounded_derived": facts["clusters_over_5000"], "verdict": "MATCH" if facts["clusters_over_5000"] == 280 else "MISMATCH"},
        {"claim": "largest cluster size", "printed_value": 250933, "derived_value": facts["largest_cluster_size"], "rounded_derived": facts["largest_cluster_size"], "verdict": "MATCH" if facts["largest_cluster_size"] == 250933 else "MISMATCH"},
    ]
    write_csv(out_dir / "section5-verdicts.csv", ("claim", "printed_value", "derived_value", "rounded_derived", "verdict"), section5_rows)

    import duckdb
    con = duckdb.connect(str(out_dir / "work/c4.duckdb"), read_only=True)
    table11_rows = []
    for index in range(1, 21):
        total_target = targets[f"table11-c4-r{index:02d}-total"]
        frac_target = targets[f"table11-c4-r{index:02d}-frac"]
        if total_target["printed_value"] == "UNRESOLVED":
            table11_rows.append({
                "row": index,
                "printed_url": "SOURCE_MISSING",
                "derived_url": "",
                "printed_total": "UNRESOLVED",
                "derived_total": "",
                "total_verdict": "SOURCE_MISSING",
                "printed_frac": "UNRESOLVED",
                "derived_frac_keep0": "",
                "derived_membership_frac": "",
                "frac_verdict": "SOURCE_MISSING",
            })
            continue
        url = total_target["split_or_arm"]
        stats = con.execute("SELECT total, keep0, multi_membership FROM url_stats WHERE url = ?", [url]).fetchone()
        if stats is None:
            derived_total, keep0, multi = 0, 0, 0
            frac_verdict = "NOT_EXECUTABLE_INPUT"
            derived_frac = ""
        else:
            derived_total, keep0, multi = stats
            fraction = Decimal(keep0) / Decimal(derived_total)
            digits = precision(frac_target["printed_value"])
            rounded = round_half_up(fraction, digits)
            frac_verdict = "MATCH" if rounded == Decimal(frac_target["printed_value"]) else "MISMATCH"
            derived_frac = str(fraction)
        membership_frac = str(Decimal(multi) / Decimal(derived_total)) if derived_total else ""
        total_verdict = "MATCH" if derived_total == int(total_target["printed_value"]) else "MISMATCH"
        table11_rows.append({
            "row": index,
            "printed_url": url,
            "derived_url": url if stats else "",
            "printed_total": total_target["printed_value"],
            "derived_total": derived_total,
            "total_verdict": total_verdict,
            "printed_frac": frac_target["printed_value"],
            "derived_frac_keep0": derived_frac,
            "derived_membership_frac": membership_frac,
            "frac_verdict": frac_verdict,
        })
    con.close()
    write_csv(out_dir / "table11-verdicts.csv", tuple(table11_rows[0]), table11_rows)
    write_json(out_dir / "convention-application.json", {
        "primary": "dropped",
        "faithful_figure_output": "figure-counts.csv convention=dropped",
        "alternatives": "low/high retained as sensitivities",
        "stage1_lock": "singleton dropped",
        "c4_identity_matches": identity["matching_conventions"],
        "ambiguous_convention": False,
    })
    write_json(out_dir / "comparison-summary.json", {
        "table2_matches": sum(row["verdict"] == "MATCH" for row in table2_rows),
        "table2_mismatches": sum(row["verdict"] == "MISMATCH" for row in table2_rows),
        "table2_indeterminate": sum(row["verdict"] == "INDETERMINATE_JOIN" for row in table2_rows),
        "table13_matches": sum(row["neardup_verdict"] == "MATCH" for row in table13_rows),
        "section5_matches": sum(row["verdict"] == "MATCH" for row in section5_rows),
        "table11_total_matches": sum(row["total_verdict"] == "MATCH" for row in table11_rows),
        "table11_frac_matches": sum(row["frac_verdict"] == "MATCH" for row in table11_rows),
        "table11_source_missing_rows": sum(row["total_verdict"] == "SOURCE_MISSING" for row in table11_rows),
        "join_status": join_status,
        "divergence_status": summary["divergence_status"],
    })
    print(json.dumps({"table2": table2_rows, "section5": section5_rows, "join": join_status}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    compare(args.root, args.out_dir)


if __name__ == "__main__":
    main()
