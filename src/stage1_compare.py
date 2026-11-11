#!/usr/bin/env python3
import argparse
import csv
import json
from decimal import Decimal, getcontext
from pathlib import Path

from stage1_audit import round_half_up, write_csv, write_json

getcontext().prec = 50


def lock_conventions(match_counts):
    matching = sorted(name for name, count in match_counts.items() if count == 11)
    locked = matching if matching else sorted(match_counts)
    return {
        "matching_conventions": matching,
        "locked_candidate_set": locked,
        "primary": locked[0] if len(locked) == 1 else None,
        "status": "PRIMARY_LOCKED" if len(locked) == 1 else "AMBIGUOUS_CONVENTION",
    }


def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def ensure_fresh_comparison(out_dir):
    out_dir = Path(out_dir)
    outputs = (
        "table2-verdicts.csv",
        "table13-verdicts.csv",
        "figure-verdicts.csv",
        "convention-lock.json",
        "comparison-summary.json",
        "report.md",
        "run-manifest.json",
    )
    existing = [name for name in outputs if (out_dir / name).exists()]
    if existing:
        raise FileExistsError(f"refusing to overwrite comparison outputs in {out_dir}: {existing}")


def compare(root, out_dir):
    root = Path(root)
    out_dir = Path(out_dir)
    ensure_fresh_comparison(out_dir)
    targets = {
        row["target_id"]: row
        for row in read_csv(root / "paper/targets/printed-targets.csv")
    }
    join_status = json.loads((out_dir / "derived-summary.json").read_text(encoding="utf-8"))["split_join"]["status"]
    duplication = read_csv(out_dir / "derived-duplication.csv")
    table2_rows = []
    target_ids = {
        "TT": "table2-wiki40b-train-train",
        "EE": "table2-wiki40b-valid-valid",
        "ET": "table2-wiki40b-valid-train",
    }
    for arm in ("validation", "test"):
        for metric in ("TT", "EE", "ET"):
            derived = next(row for row in duplication if row["arm"] == arm and row["metric"] == metric)
            target = targets[target_ids[metric]]
            numerator = int(derived["numerator"])
            denominator = int(derived["denominator"])
            percent = Decimal(numerator) * 100 / Decimal(denominator)
            rounded = round_half_up(percent, 2)
            printed = Decimal(target["printed_value"])
            verdict = "MATCH" if rounded == printed else "MISMATCH"
            if join_status != "COMPLETE":
                verdict = "INDETERMINATE_JOIN"
            table2_rows.append({
                "target_id": target["target_id"],
                "printed_label": target["split_or_arm"],
                "arm": arm,
                "metric": metric,
                "printed_value": target["printed_value"],
                "derived_numerator": numerator,
                "derived_denominator": denominator,
                "unrounded_percent": str(percent),
                "rounded_percent": f"{rounded:.2f}",
                "verdict": verdict,
            })
    write_csv(out_dir / "table2-verdicts.csv", tuple(table2_rows[0]), table2_rows)

    removal_rows = read_csv(out_dir / "derived-removals.csv")
    table13_rows = []
    original = Decimal("2926536") / Decimal(1000000)
    original_rounded = round_half_up(original, 2)
    original_printed = Decimal(targets["table13-wiki40b-examples-original"]["printed_value"])
    neardup_printed = Decimal(targets["table13-wiki40b-examples-neardup"]["printed_value"])
    for derived in removal_rows:
        removals = int(derived["removals"])
        retained = int(derived["retained"])
        retained_rounded = round_half_up(Decimal(retained) / Decimal(1000000), 2)
        interval_verdict = "CONSISTENT_INTERVAL" if 11536 < removals <= 21536 else "CONTRADICTION"
        neardup_verdict = "MATCH" if retained_rounded == neardup_printed else "MISMATCH"
        if join_status != "COMPLETE":
            neardup_verdict = interval_verdict = "INDETERMINATE_JOIN"
        table13_rows.append({
            "arm": derived["arm"],
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
            "removal_interval_exclusive_lower": 11536,
            "removal_interval_inclusive_upper": 21536,
            "interval_verdict": interval_verdict,
        })
    write_csv(out_dir / "table13-verdicts.csv", tuple(table13_rows[0]), table13_rows)

    printed_bars = [
        row for row in read_csv(root / "paper/targets/figure-bars.csv")
        if row["figure"] == "Figure 8(c)"
    ]
    figure_counts = read_csv(out_dir / "figure-counts.csv")
    figure_rows = []
    match_counts = {}
    for convention in ("dropped", "low", "high"):
        match_counts[convention] = 0
        for printed in printed_bars:
            derived = next(row for row in figure_counts if row["convention"] == convention and row["bin_index"] == printed["bin_index"])
            verdict = "MATCH" if int(derived["cluster_count"]) == int(printed["printed_count"]) else "MISMATCH"
            if verdict == "MATCH":
                match_counts[convention] += 1
            figure_rows.append({
                "convention": convention,
                "bin_index": printed["bin_index"],
                "bin_label": printed["bin_label"],
                "printed_count": printed["printed_count"],
                "derived_count": derived["cluster_count"],
                "verdict": verdict,
            })
    write_csv(out_dir / "figure-verdicts.csv", tuple(figure_rows[0]), figure_rows)
    lock = lock_conventions(match_counts)
    lock["match_counts"] = match_counts
    lock["basis"] = "Wiki-40B Figure 8 bottom-panel printed fidelity only; C4 content was not opened"
    write_json(out_dir / "convention-lock.json", lock)
    write_json(out_dir / "comparison-summary.json", {
        "table2_matches": sum(row["verdict"] == "MATCH" for row in table2_rows),
        "table2_mismatches": sum(row["verdict"] == "MISMATCH" for row in table2_rows),
        "table2_indeterminate": sum(row["verdict"] == "INDETERMINATE_JOIN" for row in table2_rows),
        "table13_matches": sum(row["neardup_verdict"] == "MATCH" for row in table13_rows),
        "figure_match_counts": match_counts,
        "convention_lock": lock,
    })
    print(json.dumps(lock, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    compare(args.root, args.out_dir)


if __name__ == "__main__":
    main()
