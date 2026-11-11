#!/usr/bin/env python3
import argparse
import csv
import hashlib
import html
import json
import math
import re
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from stage1_audit import sha256

ACCEPTED_RUNS = {
    "stage1": "results/stage1/run-004/audit",
    "stage2": "results/stage2/run-004/audit",
    "stage3": "results/stage3/run-002/audit",
}
BINS = ("1", "2", "3", "4", "5", "[6, 10)", "[11, 20)", "[21, 50)", "[51, 500)", "[501, 5000)", "[5001, ∞)")
EDGE_SIZES = (10, 20, 50, 500, 5000)
LEDGER_FIELDS = (
    "entry_id", "target_id", "claim_id", "corpus", "locator", "basis",
    "value_class", "printed_value", "unit", "derived_value", "verdict",
    "qualification", "source_path",
)


def read_csv(path):
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_text(path, text):
    Path(path).write_bytes(text.encode("utf-8"))


def write_json(path, value):
    write_text(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def write_csv(path, rows, fields=LEDGER_FIELDS):
    from io import StringIO
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    write_text(path, stream.getvalue())


def number(value):
    decimal = Decimal(str(value))
    if decimal == decimal.to_integral_value():
        return f"{int(decimal):,}"
    return f"{decimal:,}"


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


def verify_manifest_outputs(run_dir, manifest):
    run_dir = Path(run_dir)
    for name, receipt in manifest["outputs"].items():
        path = run_dir / name
        assert path.is_file(), f"missing accepted output: {path}"
        assert path.stat().st_size == receipt["bytes"], f"accepted output byte count changed: {path}"
        assert sha256(path) == receipt["sha256"], f"accepted output hash changed: {path}"


def verify_freeze_contract(root):
    root = Path(root)
    freeze = read_json(root / "planning/FREEZE-v1.json")
    postfreeze_files = {"PREREGISTRATION.md", "data/raw/MANIFEST.md"}
    exact_files = sorted(set(freeze["sha256"]) - postfreeze_files)
    for relative in exact_files:
        path = root / relative
        if relative == "paper/paper.pdf" and not path.exists():
            continue
        assert path.is_file(), f"missing frozen file: {relative}"
        assert sha256(path) == freeze["sha256"][relative], f"frozen file hash changed: {relative}"
    current = (root / "PREREGISTRATION.md").read_bytes()
    snapshot = (root / freeze["snapshot_byte_equality"]["PREREGISTRATION.md"]).read_bytes()
    assert current.startswith(snapshot), "PREREGISTRATION.md is not an append-only extension of frozen v1"
    suffix = current[len(snapshot):].decode("utf-8")
    assert "2026-11-09 — Amendment A1: streamed C4 train custody" in suffix, "missing dated Amendment A1"
    manifest = root / "data/raw/MANIFEST.md"
    return {
        "exact_hash_files_verified": len(exact_files) - (0 if (root / "paper/paper.pdf").is_file() else 1),
        "snapshot_files_verified": list(freeze["snapshot_files"]),
        "preregistration_prefix_extension": True,
        "amendments": ["2026-11-09 — Amendment A1: streamed C4 train custody"],
        "postfreeze_manifest": {"bytes": manifest.stat().st_size, "sha256": sha256(manifest)},
        "excluded_sources": ["paper/paper.pdf"],
    }


def verify_accepted_sources(root):
    root = Path(root)
    receipts = {"accepted_runs": {}, "frozen_inputs": {}, "freeze": verify_freeze_contract(root)}
    for stage, relative in ACCEPTED_RUNS.items():
        run_dir = root / relative
        manifest_path = run_dir / "run-manifest.json"
        manifest = read_json(manifest_path)
        verify_manifest_outputs(run_dir, manifest)
        receipts["accepted_runs"][stage] = {
            "path": relative,
            "run_manifest": {
                "bytes": manifest_path.stat().st_size,
                "sha256": sha256(manifest_path),
            },
            "outputs": manifest["outputs"],
        }
    for relative in (
        "paper/targets/printed-targets.csv",
        "paper/targets/figure-bars.csv",
        "paper/targets/README.md",
        "planning/step0/arithmetic.json",
        "planning/step0/arithmetic.md",
        "PREREGISTRATION.md",
        "CLAIM_INVENTORY.md",
    ):
        path = root / relative
        assert path.is_file(), f"missing frozen input: {relative}"
        receipts["frozen_inputs"][relative] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    return receipts


def verify_recorded_inputs(root, run_dir):
    recorded = read_json(Path(run_dir) / "input-manifest.json")
    fresh = verify_accepted_sources(root)
    assert recorded == fresh, "accepted-source receipts differ from the candidate input manifest"
    return fresh


def _figures(root):
    root = Path(root)
    specs = (
        ("fig1-c4", "Figure 1 — C4", "C4", "stage1", "stage2", "fig1-c4-bin"),
        ("fig8-realnews", "Figure 8 middle — RealNews", "RealNews", "stage3", "stage3", "fig8-realnews-bin"),
        ("fig8-wiki40b", "Figure 8 bottom — Wiki-40B", "Wiki-40B", "stage1", "stage1", "fig8-wiki40b-bin"),
    )
    panels = []
    for panel_id, title, corpus, count_stage, verdict_stage, prefix in specs:
        count_dir = root / ACCEPTED_RUNS[count_stage]
        verdict_dir = root / ACCEPTED_RUNS[verdict_stage]
        verdicts = read_csv(verdict_dir / "figure-verdicts.csv")
        conventions = {}
        for convention in ("dropped", "low", "high"):
            rows = []
            for row in verdicts:
                if row["convention"] != convention:
                    continue
                index = int(row["bin_index"])
                rows.append({
                    "bin_index": index,
                    "bin_label": row["bin_label"],
                    "target_id": f"{prefix}-{index:02d}",
                    "printed_count": int(row["printed_count"]),
                    "derived_count": int(row["derived_count"]),
                    "verdict": row["verdict"],
                })
            rows.sort(key=lambda row: row["bin_index"])
            assert [row["bin_label"] for row in rows] == list(BINS)
            conventions[convention] = rows
        if (verdict_dir / "edge-sizes.csv").is_file():
            edges = [
                {
                    "cluster_size": int(row["cluster_size"]),
                    "cluster_count": int(row["cluster_count"]),
                    "document_count": int(row["document_count"]),
                }
                for row in read_csv(verdict_dir / "edge-sizes.csv")
            ]
        else:
            histogram = {int(row["cluster_size"]): row for row in read_csv(verdict_dir / "cluster-histogram.csv")}
            edges = [
                {
                    "cluster_size": size,
                    "cluster_count": int(histogram.get(size, {}).get("cluster_count", 0)),
                    "document_count": int(histogram.get(size, {}).get("document_count", 0)),
                }
                for size in EDGE_SIZES
            ]
        panels.append({
            "id": panel_id,
            "title": title,
            "corpus": corpus,
            "released": True,
            "population": "released archive, all splits",
            "primary": "dropped",
            "conventions": conventions,
            "match_counts": {
                convention: sum(row["verdict"] == "MATCH" for row in rows)
                for convention, rows in conventions.items()
            },
            "edges": edges,
            "source_path": f"{ACCEPTED_RUNS[verdict_stage]}/figure-verdicts.csv",
        })
    oracle = read_csv(root / "paper/targets/printed-targets.csv")
    lm1b_rows = []
    for row in oracle:
        if not row["target_id"].startswith("fig8-lm1b-bin-"):
            continue
        index = int(row["target_id"].rsplit("-", 1)[1])
        lm1b_rows.append({
            "bin_index": index,
            "bin_label": BINS[index - 1],
            "target_id": row["target_id"],
            "printed_count": int(row["printed_value"]),
            "verdict": "NOT_EXECUTABLE_INPUT",
        })
    lm1b_rows.sort(key=lambda row: row["bin_index"])
    assert len(lm1b_rows) == 11
    panels.append({
        "id": "fig8-lm1b",
        "title": "Figure 8 top — LM1B (printed only)",
        "corpus": "LM1B",
        "released": False,
        "population": "printed bars; split not stated",
        "printed_counts": lm1b_rows,
        "verdict": "NOT_EXECUTABLE_INPUT",
        "qualification": "No LM1B cluster archive is pinned; the released endpoint returned 404. Bars remain printed-only and no edge convention is inferred.",
        "source_path": "paper/targets/figure-bars.csv",
    })
    return {"panels": panels}


def build_figures(root):
    verify_accepted_sources(root)
    return _figures(root)


def _base_entries(root):
    entries = []
    for row in read_csv(root / "paper/targets/printed-targets.csv"):
        reason = row["notes"] or "Printed context only; no authorized executable reproduction under Stages 1–3 and 7."
        entries.append({
            "entry_id": row["target_id"],
            "target_id": row["target_id"],
            "claim_id": row["claim_id"],
            "corpus": row["corpus"],
            "locator": f"PDF p. {row['page']}, {row['locator']}",
            "basis": row["split_or_arm"],
            "value_class": "printed context",
            "printed_value": row["printed_value"],
            "unit": row["unit"],
            "derived_value": "",
            "verdict": "NOT_EXECUTABLE_INPUT",
            "qualification": reason,
            "source_path": "paper/targets/printed-targets.csv",
        })
    return entries


def _extra(entry_id, claim_id, corpus, locator, basis, value_class, printed, unit, derived, verdict, qualification, source):
    return {
        "entry_id": entry_id,
        "target_id": "",
        "claim_id": claim_id,
        "corpus": corpus,
        "locator": locator,
        "basis": basis,
        "value_class": value_class,
        "printed_value": printed,
        "unit": unit,
        "derived_value": derived,
        "verdict": verdict,
        "qualification": qualification,
        "source_path": source,
    }


def _build_ledger(root):
    root = Path(root)
    entries = _base_entries(root)
    by_target = {}
    for entry in entries:
        by_target.setdefault(entry["target_id"], []).append(entry)
    templates = {target_id: dict(matches[0]) for target_id, matches in by_target.items()}

    def overlay(target_id, **values):
        matches = by_target.get(target_id, [])
        assert matches, f"missing oracle target: {target_id}"
        matches[0].update(values)

    def expand(target_id, occurrence, **values):
        matches = by_target.get(target_id, [])
        assert matches, f"missing oracle target: {target_id}"
        if occurrence == 0:
            entry = matches[0]
        else:
            entry = dict(templates[target_id])
            entries.append(entry)
            matches.append(entry)
        entry.update(values)

    def add(**values):
        entry = _extra(**values)
        entries.append(entry)
        return entry

    stage1 = root / ACCEPTED_RUNS["stage1"]
    stage2 = root / ACCEPTED_RUNS["stage2"]
    stage3 = root / ACCEPTED_RUNS["stage3"]

    wiki_arm_occurrences = {}
    for row in read_csv(stage1 / "table2-verdicts.csv"):
        occurrence = wiki_arm_occurrences.get(row["target_id"], 0)
        wiki_arm_occurrences[row["target_id"]] = occurrence + 1
        expand(
            row["target_id"],
            occurrence,
            entry_id=f"{row['target_id']}-{row['arm']}",
            basis=row["arm"],
            value_class="directly recomputed",
            derived_value=f"{number(row['derived_numerator'])} / {number(row['derived_denominator'])} = {row['rounded_percent']}% (unrounded {row['unrounded_percent']}%)",
            verdict=row["verdict"],
            qualification="Exact-key complete join; validation and test are separate arms. The printed valid label is not renamed.",
            source_path=f"{ACCEPTED_RUNS['stage1']}/table2-verdicts.csv",
        )
    for row in read_csv(stage2 / "table2-verdicts.csv"):
        overlay(
            row["target_id"],
            value_class="directly recomputed",
            derived_value=f"{number(row['derived_numerator'])} / {number(row['derived_denominator'])} = {row['rounded_percent']}% (unrounded {row['unrounded_percent']}%)",
            verdict=row["verdict"],
            qualification="Direct observed cluster membership after release identity and complete exact-key split join.",
            source_path=f"{ACCEPTED_RUNS['stage2']}/table2-verdicts.csv",
        )
    for row in read_csv(stage3 / "table2-verdicts.csv"):
        overlay(
            row["target_id"],
            verdict=row["verdict"],
            qualification=row["reason"] + ". No train/validation/test assignments are inferred.",
            source_path=f"{ACCEPTED_RUNS['stage3']}/table2-verdicts.csv",
        )
    for target_id in ("table2-lm1b-train-train", "table2-lm1b-valid-valid", "table2-lm1b-valid-train"):
        overlay(
            target_id,
            qualification="No LM1B cluster archive is pinned; the endpoint returned 404. No NEARDUP reimplementation is authorized.",
            source_path="data/raw/MANIFEST.md",
        )

    for stage, run_dir in (("stage1", stage1), ("stage2", stage2)):
        rows = read_csv(run_dir / "table13-verdicts.csv")
        first = rows[0]
        original_target = "table13-wiki40b-examples-original" if stage == "stage1" else "table13-c4-examples-original"
        neardup_target = "table13-wiki40b-examples-neardup" if stage == "stage1" else "table13-c4-examples-neardup"
        overlay(
            original_target,
            value_class="directly recomputed from pinned public metadata",
            derived_value=f"{first['derived_original_unrounded']}M → {first['derived_original_rounded']}M",
            verdict=first["original_verdict"],
            qualification="Exact public original train size rounded half up at printed precision.",
            source_path=f"{ACCEPTED_RUNS[stage]}/table13-verdicts.csv",
        )
        for occurrence, row in enumerate(rows):
            sensitivity = " Sensitivity only; not an observed author deletion." if row["rule"] == "S" else " Alternative interpretation, not an observed author deletion."
            expand(
                neardup_target,
                occurrence,
                entry_id=f"{neardup_target}-{row['arm']}-rule-{row['rule']}",
                basis=f"{row['arm']} / Rule {row['rule']}",
                value_class="rule-derived",
                derived_value=f"removals {number(row['derived_removals'])}; retained {number(row['derived_retained'])} → {row['derived_retained_rounded']}M; exact-original interval {row['interval_verdict']}",
                verdict=row["neardup_verdict"],
                qualification=f"Exact-original removal interval ({number(row['removal_interval_exclusive_lower'])}, {number(row['removal_interval_inclusive_upper'])}].{sensitivity}",
                source_path=f"{ACCEPTED_RUNS[stage]}/table13-verdicts.csv",
            )

    realnews13 = read_csv(stage3 / "table13-verdicts.csv")[0]
    for target_id, derived_key, verdict_key in (
        ("table13-realnews-examples-original", "derived_original_rounded", "original_verdict"),
        ("table13-realnews-examples-neardup", "derived_retained_rounded", "neardup_verdict"),
    ):
        overlay(
            target_id,
            basis=realnews13["basis"],
            value_class="rule-derived" if target_id.endswith("neardup") else "directly recomputed",
            derived_value=f"{realnews13[derived_key]}M; removals {number(realnews13['derived_removals'])}; retained {number(realnews13['derived_retained'])}",
            verdict=realnews13[verdict_key],
            qualification="CONDITIONAL_RELEASE_POPULATION: measured released archive rows, not a verified exact public original train size or a train-size reproduction.",
            source_path=f"{ACCEPTED_RUNS['stage3']}/table13-verdicts.csv",
        )

    arithmetic = read_json(root / "planning/step0/arithmetic.json")
    derivations = {row["id"]: row for row in arithmetic["derivations"]}
    lm1b_floor = derivations["lm1b_printed_only_floor"]
    overlay(
        "table13-lm1b-examples-original",
        value_class="printed-only with public metadata",
        derived_value="30.301028M → 30.30M",
        verdict="MATCH",
        qualification="Pinned public train size rounded half up; this does not supply missing LM1B clusters.",
        source_path="planning/step0/arithmetic.json",
    )
    overlay(
        "table13-lm1b-examples-neardup",
        value_class="printed-only",
        derived_value="held-out-adjusted train-removal floor 510,877; robust minimum excess 70,877",
        verdict="CONTRADICTION",
        qualification="Conditional on full-population Figure 8 coverage, public-test evaluation mapping and evaluation-preferred keep-one semantics.",
        source_path="planning/step0/arithmetic.json",
    )
    overlay(
        "table13-c4-examples-exactsubstr",
        value_class="printed-only",
        derived_value="Table 13 implies 14,390,000 removed; Appendix C implies approximately 364.8M retained",
        verdict="CONTRADICTION",
        qualification="Internal source consistency finding; a copy/transcription error is not established and EXACTSUBSTR reproduction is deferred.",
        source_path="planning/step0/arithmetic.json",
    )
    for row in entries:
        if row["target_id"].startswith("table13-") and "tokens" in row["target_id"]:
            row["qualification"] = "Cluster IDs and assignments cannot reproduce the paper's 50k BPE token counts; EXACTSUBSTR reproduction is outside scope."

    for stage, run_dir, corpus in (("stage2", stage2, "c4"), ("stage3", stage3, "realnews")):
        for row in read_csv(run_dir / "table11-verdicts.csv"):
            row_number = int(row["row"])
            prefix = f"table11-{corpus}-r{row_number:02d}"
            qualification = "Exact full-ID lookup only; zero or nonzero exact-ID counts do not reconstruct or contradict the source-native host-level aggregation. No URL normalization was applied."
            if row["total_verdict"] == "SOURCE_MISSING":
                qualification = "The promised twentieth C4 URL, total and fraction are absent from the PDF; a derived ranking candidate is not a recovered printed value."
            for suffix, derived, verdict in (
                ("total", row["derived_total"], row["total_verdict"]),
                ("frac", row["derived_frac_keep0"], row["frac_verdict"]),
            ):
                target_id = f"{prefix}-{suffix}"
                if target_id not in by_target:
                    continue
                overlay(
                    target_id,
                    value_class="directly recomputed" if verdict != "SOURCE_MISSING" else "source sentinel",
                    derived_value=derived,
                    verdict=verdict,
                    qualification=qualification,
                    source_path=f"{ACCEPTED_RUNS[stage]}/table11-verdicts.csv",
                )

    figures = _figures(root)
    for panel in figures["panels"]:
        if not panel["released"]:
            for row in panel["printed_counts"]:
                overlay(
                    row["target_id"],
                    qualification=panel["qualification"],
                    source_path=panel["source_path"],
                )
            continue
        for occurrence, (convention, rows) in enumerate(panel["conventions"].items()):
            for row in rows:
                expand(
                    row["target_id"],
                    occurrence,
                    entry_id=f"{row['target_id']}-{convention}",
                    basis=convention,
                    value_class="directly recomputed" if convention == "dropped" else "sensitivity",
                    derived_value=number(row["derived_count"]),
                    verdict=row["verdict"],
                    qualification=f"{panel['population']}; bars count clusters, not documents. Primary is dropped; low/high remain visible sensitivities.",
                    source_path=panel["source_path"],
                )

    section_rows = read_csv(stage2 / "section5-verdicts.csv")
    section_map = {
        "section5-c4-pair-clusters": section_rows[0],
        "section5-c4-large-clusters": section_rows[2],
        "section5-c4-largest-cluster": section_rows[3],
    }
    for target_id, row in section_map.items():
        overlay(
            target_id,
            value_class="directly recomputed",
            derived_value=f"{number(row['derived_value'])} (rounded {row['rounded_derived']})",
            verdict=row["verdict"],
            qualification="Exact cluster histogram over all released rows; pair clusters means size-2 clusters.",
            source_path=f"{ACCEPTED_RUNS['stage2']}/section5-verdicts.csv",
        )
    overlay(
        "section5-c4-large-cluster-threshold",
        value_class="directly recomputed",
        derived_value="0 clusters of exactly 5,000; 280 clusters over 5,000",
        verdict="MATCH",
        qualification="The prose 'over 5,000' excludes size 5,000, which is counted separately from Figure 1's [5001, ∞) bin.",
        source_path=f"{ACCEPTED_RUNS['stage2']}/cluster-facts.json",
    )
    add(
        entry_id="c4-pair-majority", claim_id="C3", corpus="C4", locator="PDF p. 5, §5.1",
        basis="released archive, all splits", value_class="directly recomputed", printed="majority", unit="boolean",
        derived="True: 1,861,744 > 2,515,214 / 2", verdict="MATCH",
        qualification="Majority is evaluated among multi-document clusters.", source=f"{ACCEPTED_RUNS['stage2']}/section5-verdicts.csv",
    )

    repeated = derivations["c4_repeated_sentence_percentages"]
    overlay(
        "intro-c4-repeat-share",
        value_class="printed-only with public metadata",
        derived_value="train 0.016728200550459642%; validation 0.01673029664735826%; both round to 0.02%",
        verdict="CONSISTENT_INTERVAL",
        qualification="Both independently computed percentages round to the printed 0.02%; no substring recount was run.",
        source_path="planning/step0/arithmetic.json",
    )
    for target_id in (
        "appendix-c-c4-original-examples", "appendix-c-c4-neardup-examples",
        "appendix-c-c4-original-steps", "appendix-c-c4-neardup-steps",
        "appendix-c-c4-batch-size", "appendix-c-c4-epochs", "appendix-d-c4-size-reduction",
    ):
        overlay(
            target_id,
            value_class="printed-only",
            derived_value="Table 13 reduction 3.943870419601502% → 3.9%; steps imply 364.8M / 350.4M examples",
            verdict="CONSISTENT_INTERVAL",
            qualification="Approximate appendix anchors and rounded Table 13 values agree at printed precision; TT 3.04% is not a removal percentage.",
            source_path="planning/step0/arithmetic.json",
        )
    for target_id, public_key in (
        ("c4-exact-train-size", "c4_train"), ("c4-exact-validation-size", "c4_validation"),
        ("lm1b-exact-train-size", "lm1b_train"), ("lm1b-exact-validation-size", "lm1b_evaluation"),
    ):
        public = arithmetic["public_split_inputs"][public_key]
        overlay(
            target_id,
            value_class="public metadata",
            derived_value=f"{number(public['value'])} {public['unit']}",
            verdict="SOURCE_MISSING",
            qualification=f"Exact count is absent from the PDF and supplied separately by pinned {public['dataset']} metadata, split {public['split']}, revision {public['revision']}.",
            source_path="planning/step0/arithmetic.json",
        )

    random_ee = read_json(stage2 / "random-split-ee.json")
    random_verdict = read_json(stage2 / "random-split-verdict.json")
    expected_validation = (Decimal(random_ee["probability"]) * Decimal(random_ee["evaluation_size"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    add(
        entry_id="c4-random-split-ee", claim_id="C1", corpus="C4", locator="PDF p. 5, Table 2 validation-with-validation",
        basis="uniform fixed-size validation split; secondary model-based check", value_class="directly recomputed",
        printed="1.59", unit="%",
        derived=f"E[P_EE] = {random_verdict['unrounded_percent']}% → {random_verdict['rounded_percent']}%; V × E[P_EE] = {number(expected_validation)} expected validation documents; N × E[P_EE] = {random_ee['expected_numerator']}",
        verdict=random_verdict["verdict"],
        qualification=f"N × E[P_EE] is the whole-population weighted numerator; V × E[P_EE] is the expected validation-split count. Distinct from direct observed EE; {random_ee['evaluation']}.",
        source=f"{ACCEPTED_RUNS['stage2']}/random-split-ee.json",
    )
    ceiling = derivations["c4_removal_ceiling"]
    add(
        entry_id="step0-c4-removal-ceiling", claim_id="C2", corpus="C4", locator="PDF p. 5 Table 2 and p. 21 Table 13",
        basis="common population and evaluation-preferred keep-one", value_class="printed-only", printed="3.04% and 364.87M → 350.48M", unit="mixed",
        derived=f"robust strict ceiling < {ceiling['outputs']['rounding_aware_ceiling_strict_upper']:,.4f}; robust minimum shortfall {ceiling['outputs']['robust_minimum_shortfall']:,.4f}",
        verdict="CONTRADICTION", qualification=ceiling["interpretation"], source="planning/step0/arithmetic.json",
    )
    fig1_bounds = derivations["fig1_bounds"]
    add(
        entry_id="step0-fig1-bounds", claim_id="C2", corpus="C4", locator="PDF p. 5 Figure 1 and p. 21 Table 13",
        basis="full public train+validation coverage and keep-one", value_class="printed-only", printed="11 Figure 1 bars and 364.87M → 350.48M", unit="mixed",
        derived="train-removal interval [8,001,466, 14,410,977]; upper 3.949631584377437% of train; lower 2.192970180642311% of train",
        verdict="CONSISTENT_INTERVAL", qualification=fig1_bounds["interpretation"], source="planning/step0/arithmetic.json",
    )
    add(
        entry_id="step0-lm1b-floor", claim_id="C6", corpus="LM1B", locator="PDF p. 22 Figure 8 top and p. 21 Table 13",
        basis="full public train+test coverage, test/evaluation mapping and keep-one", value_class="printed-only", printed="29.87", unit="million examples",
        derived="train-removal floor 510,877; Table 13 interval (420,000, 440,000); robust minimum excess 70,877",
        verdict="CONTRADICTION", qualification=lm1b_floor["interpretation"], source="planning/step0/arithmetic.json",
    )
    c4_summary = read_json(stage2 / "derived-summary.json")
    multi_documents = c4_summary["keep_agreement"]["keep0_multi"]
    release_rows = c4_summary["physical_rows"]
    multi_share = (Decimal(100) * Decimal(multi_documents) / Decimal(release_rows)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    add(
        entry_id="c4-release-multidoc-share", claim_id="C1", corpus="C4", locator="PDF p. 5 Figure 1 population diagnostic",
        basis="released archive, all splits", value_class="directly recomputed", printed="Figure 1 implies a population-dependent bound", unit="%",
        derived=f"{number(multi_documents)} / {number(release_rows)} = {multi_share}%", verdict="MATCH",
        qualification="All-document multi-document membership share, not TT, EE, ET or a removal percentage.", source=f"{ACCEPTED_RUNS['stage2']}/derived-summary.json",
    )
    for stage, companion_path, corpus in (("stage2", stage2, "c4"), ("stage3", stage3, "realnews")):
        companion = read_json(companion_path / "companion-verdicts.json")
        rounding = companion["section5_rounding"]
        add(
            entry_id=f"{corpus}-section5-rounding", claim_id="C1" if corpus == "c4" else "C5", corpus=corpus.upper() if corpus == "c4" else "RealNews",
            locator="PDF p. 6, §5.3", basis="printed ROUND_HALF_UP consistency", value_class="printed-only",
            printed=rounding["printed_section5_3"], unit="%", derived=f"{rounding['printed_table2']} → {rounding['printed_section5_3']}",
            verdict=rounding["verdict"], qualification=rounding["basis"], source=f"{ACCEPTED_RUNS[stage]}/companion-verdicts.json",
        )
    c4_companion = read_json(stage2 / "companion-verdicts.json")
    for rule, verdict in c4_companion["printed_difference_interval"].items():
        removals = read_json(stage2 / "derived-summary.json")["removals"][rule]
        add(
            entry_id=f"c4-printed-difference-rule-{rule}", claim_id="C2", corpus="C4", locator="PDF p. 21, Table 13",
            basis=f"independently rounded printed cells / Rule {rule}", value_class="rule-derived", printed="364.87M → 350.48M", unit="million examples",
            derived=f"removals {number(removals)} against (14,380,000, 14,400,000)", verdict=verdict,
            qualification="Distinct from the exact-original interval; Rule S is sensitivity only and no rule is an observed author deletion.",
            source=f"{ACCEPTED_RUNS['stage2']}/companion-verdicts.json",
        )
    realnews_ceiling = read_json(stage3 / "removal-ceiling.json")
    add(
        entry_id="realnews-split-free-ceiling", claim_id="C5", corpus="RealNews", locator="PDF p. 21, Table 13",
        basis="split-free keep-one ceiling", value_class="directly recomputed", printed="31.16M → 28.39M", unit="million examples",
        derived=f"U = {number(realnews_ceiling['multi_documents'])} − {number(realnews_ceiling['multi_clusters'])} = {number(realnews_ceiling['removals'])}",
        verdict="CEILING_COMPATIBLE", qualification="Printed-difference interval is (2,760,000, 2,780,000). CEILING_COMPATIBLE is only a ceiling result, not a train-size match.",
        source=f"{ACCEPTED_RUNS['stage3']}/removal-ceiling.json",
    )
    add(
        entry_id="realnews-zero-eligibility-ranking", claim_id="C5", corpus="RealNews", locator="PDF p. 21, Table 11 derived diagnostic",
        basis="exact full IDs with total >= 10", value_class="directly recomputed", printed="19 printed host-like rows", unit="IDs",
        derived="0 eligible exact full IDs; derived ranking is empty", verdict="MISMATCH",
        qualification="The zero-eligibility ranking follows the frozen exact-ID rule and does not establish a host-level contradiction.", source=f"{ACCEPTED_RUNS['stage3']}/table11-top20.csv",
    )
    add(
        entry_id="external-c4-publication-abstract", claim_id="C7", corpus="C4", locator="Google Research publication abstract, accessed 2026-11-08",
        basis="external publication-page statement; denominator/basis unresolved", value_class="external context", printed="1.68", unit="%",
        derived="No cluster-derived basis assigned", verdict="NOT_EXECUTABLE_INPUT",
        qualification="External publication-page statement, not a PDF Table 2 substitute or a replacement for 3.04%, 4.60%, Table 13 or Figure 1.",
        source="https://research.google/pubs/deduplicating-training-data-makes-language-models-better/",
    )
    return entries


def build_ledger(root):
    verify_accepted_sources(root)
    entries = _build_ledger(root)
    ids = [row["entry_id"] for row in entries]
    assert len(ids) == len(set(ids)), "duplicate ledger entry IDs"
    return entries


def render_panel_svg(panel, convention="dropped"):
    if panel["released"]:
        rows = panel["conventions"][convention]
        counts = [row["derived_count"] for row in rows]
        title = f"{panel['title']} — {convention}"
        description = f"Eleven horizontal bars count clusters over the {panel['population']}. Exact values are supplied in the adjacent data table. Match count: {panel['match_counts'][convention]} of 11."
    else:
        rows = panel["printed_counts"]
        counts = [row["printed_count"] for row in rows]
        title = panel["title"]
        description = f"Eleven printed-only horizontal bars. {panel['qualification']}"
    width = 1000
    row_height = 52
    height = 105 + row_height * len(rows)
    left = 126
    plot_width = 620
    maximum = max(counts)
    denominator = math.log10(maximum + 1) if maximum else 1
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="{panel["id"]}-{convention}-title {panel["id"]}-{convention}-desc" viewBox="0 0 {width} {height}">',
        f'<title id="{panel["id"]}-{convention}-title">{html.escape(title)}</title>',
        f'<desc id="{panel["id"]}-{convention}-desc">{html.escape(description)}</desc>',
        f'<text class="chart-title" x="{left}" y="28">{html.escape(title)}</text>',
        f'<line class="axis" x1="{left}" y1="52" x2="{left}" y2="{height - 43}"/>',
    ]
    for index, (row, count) in enumerate(zip(rows, counts)):
        y = 67 + index * row_height
        bar_width = 0 if count == 0 else max(1, round(plot_width * math.log10(count + 1) / denominator, 3))
        parts.extend([
            f'<text class="bin-label" x="{left - 12}" y="{y + 14}" text-anchor="end">{html.escape(row["bin_label"])}</text>',
            f'<rect class="bar" data-count="{count}" x="{left}" y="{y}" width="{bar_width}" height="24" rx="2"/>',
            f'<text class="value-label" x="{left + plot_width + 14}" y="{y + 17}">{number(count)}</text>',
        ])
    parts.extend([
        f'<text class="axis-label" x="{left}" y="{height - 10}">0</text>',
        f'<text class="axis-label" x="{left + plot_width}" y="{height - 10}" text-anchor="end">log10(groups + 1) = {denominator:.3f}</text>',
        "</svg>",
    ])
    return "\n".join(parts)


def _status(verdict):
    return f'<span class="verdict verdict-{html.escape(verdict.lower().replace("_", "-"))}">{html.escape(verdict)}</span>'


def _source_link(source_path, text="source"):
    href = source_path if source_path.startswith("https://") else f"../../../../{source_path}"
    return f'<a href="{html.escape(href, quote=True)}">{html.escape(text)}</a>'


def render_html(root, ledger, figures):
    root = Path(root)
    c4_summary = read_json(root / ACCEPTED_RUNS["stage2"] / "derived-summary.json")
    realnews_summary = read_json(root / ACCEPTED_RUNS["stage3"] / "derived-summary.json")
    c4_direct = {row["metric"]: row for row in read_csv(root / ACCEPTED_RUNS["stage2"] / "table2-verdicts.csv")}
    claims = sorted({row["claim_id"] for row in ledger})
    verdicts = sorted({row["verdict"] for row in ledger})
    parts = ["""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lee et al. duplication audit | Released-cluster ledger</title>
<style>
:root { color-scheme: light; --ink:#17202a; --muted:#56616f; --paper:#f4f6f8; --surface:#fff; --line:#d9dfe6; --accent:#155eef; --nav:#102a43; --good:#136f4a; --bad:#a32929; --warn:#875b00; }
* { box-sizing:border-box; }
html { scroll-behavior:smooth; }
body { margin:0; background:var(--paper); color:var(--ink); font:16px/1.58 system-ui,-apple-system,"Segoe UI",sans-serif; }
a { color:#0b55c4; text-underline-offset:3px; }
a:any-link, button, input, select, summary { min-block-size:24px; }
:where(a:any-link,button,input,select,summary,[tabindex]):focus-visible { outline:3px solid #d97706; outline-offset:3px; }
.skip-link { position:absolute; inset-inline-start:1rem; inset-block-start:-5rem; background:#fff; padding:.65rem 1rem; z-index:10; }
.skip-link:focus { inset-block-start:.5rem; }
.site-header { background:var(--nav); color:#fff; }
.nav-inner,.wrap { width:min(1420px,94vw); margin-inline:auto; }
.nav-inner { display:flex; align-items:center; justify-content:space-between; gap:2rem; padding-block:1rem; }
.brand { color:#fff; font-weight:750; text-decoration:none; letter-spacing:.01em; }
nav ul { display:flex; flex-wrap:wrap; gap:1.25rem; list-style:none; margin:0; padding:0; }
nav a { color:#dcebff; }
.hero { padding:3.4rem 0 2.2rem; }
.eyebrow { color:var(--accent); font-size:.78rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }
h1 { max-width:1000px; margin:.4rem 0 1rem; font-size:clamp(2rem,4vw,3.65rem); line-height:1.08; letter-spacing:-.035em; }
h2 { margin-top:0; font-size:clamp(1.45rem,2vw,2rem); line-height:1.2; }
h3 { line-height:1.25; }
.lede { max-width:900px; color:var(--muted); font-size:1.08rem; }
.meta { display:flex; flex-wrap:wrap; gap:.6rem 1.5rem; margin-top:1.4rem; color:var(--muted); font-size:.9rem; }
main section { margin-bottom:1.5rem; }
.panel { background:var(--surface); border:1px solid var(--line); border-radius:14px; padding:clamp(1rem,2.5vw,2rem); box-shadow:0 4px 18px rgb(16 42 67 / .04); }
.summary-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:1rem; margin-top:1.6rem; }
.metric { background:var(--surface); border:1px solid var(--line); border-radius:12px; padding:1.15rem; }
.metric-label { color:var(--muted); font-size:.83rem; font-weight:700; text-transform:uppercase; letter-spacing:.05em; }
.metric-value { display:block; margin:.3rem 0; font-size:clamp(1.65rem,3vw,2.5rem); font-weight:780; line-height:1.1; }
.metric p { margin:.35rem 0 0; color:var(--muted); font-size:.88rem; }
.findings { display:grid; grid-template-columns:1.3fr 1fr; gap:1.5rem; }
.callout { border-inline-start:4px solid var(--accent); background:#eef4ff; padding:1rem 1.2rem; }
.callout.warning { border-color:#b26a00; background:#fff7e8; }
.callout p:last-child { margin-bottom:0; }
.figure-block { border-top:1px solid var(--line); margin-top:2rem; padding-top:1.5rem; }
.figure-head { display:flex; align-items:start; justify-content:space-between; gap:1rem; flex-wrap:wrap; }
.control { display:flex; align-items:center; gap:.5rem; }
label { font-weight:650; }
input,select { border:1px solid #9aa7b5; border-radius:6px; background:#fff; color:var(--ink); padding:.48rem .6rem; font:inherit; }
.chart { overflow-x:auto; }
.chart svg { display:block; inline-size:100%; min-inline-size:680px; block-size:auto; }
.chart-title { font:700 18px system-ui,sans-serif; fill:var(--ink); }
.bin-label,.value-label,.axis-label { font:13px ui-monospace,SFMono-Regular,Consolas,monospace; fill:var(--ink); }
.axis { stroke:#7c8794; stroke-width:1; }
.bar { fill:#2f6fde; }
details { margin-top:1rem; }
summary { cursor:pointer; font-weight:700; padding:.45rem 0; }
.table-wrapper { overflow:auto; max-inline-size:100%; margin-top:1rem; border:1px solid var(--line); border-radius:8px; background:#fff; container-type:inline-size; }
table { width:100%; border-collapse:separate; border-spacing:0; font-size:.88rem; }
caption { text-align:left; padding:.8rem; font-weight:750; }
th,td { padding:.62rem .7rem; border-bottom:1px solid #e5e9ee; text-align:left; vertical-align:top; }
thead { position:sticky; inset-block-start:0; z-index:1; background:#edf1f5; }
tbody th { position:sticky; inset-inline-start:0; background:#fff; }
tbody tr:last-child > * { border-bottom:0; }
.num { font-variant-numeric:tabular-nums; white-space:nowrap; }
.verdict { display:inline-block; border-radius:999px; padding:.12rem .48rem; font-size:.72rem; font-weight:800; letter-spacing:.025em; }
.verdict-match,.verdict-consistent-interval,.verdict-ceiling-compatible { color:#0c5b3c; background:#dff4e9; }
.verdict-mismatch,.verdict-contradiction { color:#8e2222; background:#fde5e5; }
.verdict-not-executable-input,.verdict-source-missing { color:#735000; background:#fff0c9; }
.filters { display:grid; grid-template-columns:2fr 1fr 1.4fr; gap:1rem; align-items:end; }
.filters > div { display:grid; gap:.3rem; }
#ledger-status { margin:.8rem 0 0; color:var(--muted); }
.ledger-table { min-width:1120px; }
.ledger-table td:nth-child(4),.ledger-table td:nth-child(6) { min-width:260px; }
.small { color:var(--muted); font-size:.88rem; }
footer { padding:2rem 0 3rem; color:var(--muted); }
@media (max-width:1000px) { .summary-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } .findings { grid-template-columns:1fr; } }
@media (max-width:700px) { .nav-inner { align-items:start; flex-direction:column; gap:.7rem; } .summary-grid,.filters { grid-template-columns:1fr; } .hero { padding-top:2rem; } .panel { border-radius:9px; } }
@media (pointer:coarse) { a:any-link,button,input,select,summary { min-block-size:44px; } }
@media (prefers-reduced-motion:reduce) { html { scroll-behavior:auto; } }
@media print { .site-header,.filters,.control,.skip-link { display:none; } body { background:#fff; } .panel,.metric { box-shadow:none; break-inside:avoid; } details > * { display:block; } }
</style>
</head>
<body>
<a class="skip-link" href="#content">Skip to main content</a>
<header class="site-header">
<div class="nav-inner">
<a class="brand" href="#content">Paper claim audit · 2107.06499</a>
<nav aria-label="Reader sections"><ul>
<li><a href="#findings">Findings</a></li><li><a href="#figures">Figures</a></li><li><a href="#ledger">Claim ledger</a></li><li><a href="#methods">Methods &amp; limits</a></li><li><a href="https://github.com/kenrinzero/lee-training-data-dedup">Source repository</a></li>
</ul></nav>
</div>
</header>
<main id="content" class="wrap" tabindex="-1">
<section class="hero" aria-labelledby="page-title">
<p class="eyebrow">Integrated Stage 7 · FROZEN v1</p>
<h1 id="page-title">Released clusters reproduce the figures—not the headline C4 rate</h1>
<p class="lede">A bounded executable audit of Lee et al. (2022), <cite>Deduplicating Training Data Makes Language Models Better</cite>. All 33 released C4, RealNews and Wiki-40B bars match when exact edge sizes are dropped. Direct cluster membership instead gives C4 train-with-train <strong>4.63%</strong>, not the printed <strong>3.04%</strong>.</p>
<div class="meta"><span>Sources: Stage 1 run-004 · Stage 2 run-004 · Stage 3 run-002</span><span>193 printed-oracle rows preserved</span><span>Offline · no runtime dependencies</span></div>
<div class="summary-grid">
<div class="metric"><span class="metric-label">C4 train-with-train</span><strong class="metric-value">4.63%</strong><p>16,892,539 / 364,868,892 · printed 3.04% · MISMATCH</p></div>
<div class="metric"><span class="metric-label">C4 Table 13 · Rule A</span><strong class="metric-value">350.48M</strong><p>14,393,547 rule-derived removals · MATCH · not observed author deletions</p></div>
<div class="metric"><span class="metric-label">Released figure bars</span><strong class="metric-value">33 / 33</strong><p>dropped primary · low/high alternatives retained</p></div>
<div class="metric"><span class="metric-label">RealNews keep-one ceiling</span><strong class="metric-value">2,782,768</strong><p>CEILING_COMPATIBLE · not a train-size match</p></div>
</div>
</section>
<section id="findings" class="panel" aria-labelledby="findings-title">
<h2 id="findings-title">What the audit supports</h2>
<div class="findings">
<div>
<div class="callout"><p><strong>C4’s direct Table 2 row is mixed.</strong> TT is 4.63% (MISMATCH), observed validation-with-validation is 1.58% (MISMATCH), and validation-with-train is 4.60% (MATCH). A separate uniform fixed-size split expectation is 1.60% (MISMATCH), with an expected validation count of 5,849.19.</p></div>
<p><strong>Table 13 distinguishes removal rules.</strong> Evaluation-preferred Rule A reproduces C4’s rounded 350.48M; uniform train keep-one Rule B gives 350.49M and the all-train sensitivity gives 347.97M. These are interpretations, not observed author deletions.</p>
<p><strong>Wiki-40B needs both evaluation arms.</strong> TT is 0.70% versus 0.39%. EE matches 0.26% under validation and test; ET is 0.70% under validation but 0.72% under test. The printed label <code>valid</code> is not renamed.</p>
</div>
<div>
<div class="callout warning"><p><strong>RealNews remains split-limited.</strong> Its three Table 2 cells are NOT_EXECUTABLE_INPUT. The released rows support a split-free ceiling and a conditional release-population comparison, not a public train-size reproduction.</p></div>
<p><strong>Table 11 is an exact-ID diagnostic.</strong> Exact full-ID misses do not reconstruct or contradict the source-native host-level aggregation. C4’s promised twentieth printed row remains SOURCE_MISSING; RealNews has zero exact full IDs eligible for its derived ranking.</p>
<p><strong>LM1B remains printed-only.</strong> No LM1B cluster archive is pinned. Its conditional printed-only removal floor is 510,877, exceeding Table 13’s largest printed-difference-compatible value by 70,877.</p>
</div>
</div>
<h3>C4’s percentages are not interchangeable</h3>
<div class="table-wrapper" tabindex="0" role="region" aria-labelledby="percentage-caption"><table>
<caption id="percentage-caption">Alternative C4 values, with basis attached</caption>
<thead><tr><th scope="col">Value</th><th scope="col">Source / derived basis</th><th scope="col">Disposition</th></tr></thead>
<tbody>
<tr><th scope="row">1.68%</th><td>External Google Research abstract; denominator unresolved; not a PDF Table 2 substitute</td><td>NOT_EXECUTABLE_INPUT</td></tr>
<tr><th scope="row">3.04%</th><td>Printed Table 2 train-with-train; direct recount is 4.63%</td><td>MISMATCH</td></tr>
<tr><th scope="row">3.943870…% → 3.9%</th><td>Table 13’s independently rounded sizes; Appendix D anchor</td><td>CONSISTENT_INTERVAL</td></tr>
<tr><th scope="row">[8,001,466, 14,410,977]</th><td>Conditional Figure 1 train-removal bounds; upper is 3.949631…% of train</td><td>CONSISTENT_INTERVAL</td></tr>
<tr><th scope="row">4.63%</th><td>Direct train-with-train and, separately, released all-document multi-cluster share</td><td>Distinct numerators and denominators</td></tr>
<tr><th scope="row">4.60%</th><td>Direct validation-with-train; §5.3 prints 4.6%</td><td>MATCH</td></tr>
</tbody></table></div>
<p><a href="report.md">Read the complete integrated report</a> · <a href="ledger.csv">Download the complete ledger (CSV)</a> · <a href="figures.json">Figure data (JSON)</a></p>
</section>
<section id="figures" class="panel" aria-labelledby="figures-title">
<h2 id="figures-title">Figures rebuilt from immutable outputs</h2>
<p>Bars count <strong>clusters</strong>, not documents. Horizontal lengths use <code>log10(groups + 1)</code> so singleton and rare-cluster bars remain legible together; exact labels and semantic tables carry the values. The dropped convention omits exact sizes 10, 20, 50, 500 and 5000. Low and high remain visible sensitivities.</p>
"""]
    for panel in figures["panels"]:
        parts.append(f'<article class="figure-block" aria-labelledby="{panel["id"]}-heading">')
        parts.append(f'<div class="figure-head"><div><h3 id="{panel["id"]}-heading">{html.escape(panel["title"])}</h3>')
        if panel["released"]:
            counts = panel["match_counts"]
            parts.append(f'<p class="small">dropped {counts["dropped"]}/11 · low {counts["low"]}/11 · high {counts["high"]}/11 · {html.escape(panel["population"])}</p></div>')
            select_id = f'convention-{panel["id"]}'
            options = "".join(f'<option value="{name}"{ " selected" if name == "dropped" else ""}>{name}</option>' for name in ("dropped", "low", "high"))
            parts.append(f'<div class="control"><label for="{select_id}">Convention</label><select id="{select_id}" data-convention-select="{panel["id"]}">{options}</select></div></div>')
            for convention in ("dropped", "low", "high"):
                hidden = "" if convention == "dropped" else " hidden"
                parts.append(f'<div class="chart" data-convention-panel="{panel["id"]}" data-convention="{convention}"{hidden}>{render_panel_svg(panel, convention)}</div>')
            parts.append(f'<p class="small">Primary SVG: <a href="{panel["id"]}.svg">{panel["id"]}.svg</a> · {_source_link(panel["source_path"], "accepted figure verdicts")}</p>')
            parts.append(f'<details><summary>Data table: all three conventions</summary><div class="table-wrapper" tabindex="0" role="region" aria-label="{html.escape(panel["title"])} data"><table><thead><tr><th scope="col">Convention</th><th scope="col">Bin</th><th scope="col">Printed clusters</th><th scope="col">Derived clusters</th><th scope="col">Verdict</th></tr></thead><tbody>')
            for convention in ("dropped", "low", "high"):
                for row in panel["conventions"][convention]:
                    parts.append(f'<tr><th scope="row">{convention}</th><td>{html.escape(row["bin_label"])}</td><td class="num">{number(row["printed_count"])}</td><td class="num">{number(row["derived_count"])}</td><td>{_status(row["verdict"])}</td></tr>')
            parts.append('</tbody></table></div></details>')
            parts.append(f'<details><summary>Exact edge sizes omitted by dropped</summary><div class="table-wrapper" tabindex="0" role="region" aria-label="{html.escape(panel["title"])} omitted edge sizes"><table><thead><tr><th scope="col">Cluster size</th><th scope="col">Clusters</th><th scope="col">Documents</th></tr></thead><tbody>')
            for row in panel["edges"]:
                parts.append(f'<tr><th scope="row">{row["cluster_size"]}</th><td class="num">{number(row["cluster_count"])}</td><td class="num">{number(row["document_count"])}</td></tr>')
            parts.append('</tbody></table></div></details>')
        else:
            parts.append(f'<p class="small">{html.escape(panel["qualification"])}</p></div></div>')
            parts.append(f'<div class="chart">{render_panel_svg(panel)}</div>')
            parts.append(f'<p class="small">Printed-only SVG: <a href="{panel["id"]}.svg">{panel["id"]}.svg</a> · {_source_link(panel["source_path"], "printed figure oracle")}</p>')
            parts.append('<details><summary>Printed data table</summary><div class="table-wrapper" tabindex="0" role="region" aria-label="LM1B printed data"><table><thead><tr><th scope="col">Bin</th><th scope="col">Printed clusters</th><th scope="col">Verdict</th></tr></thead><tbody>')
            for row in panel["printed_counts"]:
                parts.append(f'<tr><th scope="row">{html.escape(row["bin_label"])}</th><td class="num">{number(row["printed_count"])}</td><td>{_status(row["verdict"])}</td></tr>')
            parts.append('</tbody></table></div></details>')
        parts.append('</article>')
    parts.append("""</section>
<section id="ledger" class="panel" aria-labelledby="ledger-title">
<h2 id="ledger-title">Complete printed-value and verdict ledger</h2>
<p>Every printed-oracle row is represented. Multi-arm, multi-rule and multi-convention checks expand into separate entries. Non-executable rows name the missing input or scope limit; context rows are not silently promoted to reproductions.</p>
<search aria-label="Filter claim ledger"><div class="filters">
<div><label for="ledger-query">Search ID, value or qualification</label><input id="ledger-query" type="search" autocomplete="off"></div>
<div><label for="ledger-claim">Claim group</label><select id="ledger-claim"><option value="">All claims</option>""")
    for claim in claims:
        parts.append(f'<option value="{html.escape(claim)}">{html.escape(claim)}</option>')
    parts.append("""</select></div>
<div><label for="ledger-verdict">Verdict</label><select id="ledger-verdict"><option value="">All verdicts</option>""")
    for verdict in verdicts:
        parts.append(f'<option value="{html.escape(verdict)}">{html.escape(verdict)}</option>')
    parts.append("""</select></div></div></search>
<p id="ledger-status" aria-live="polite" aria-atomic="true"></p>
<div class="table-wrapper" tabindex="0" role="region" aria-labelledby="ledger-caption"><table class="ledger-table">
<caption id="ledger-caption">Printed, directly recomputed, rule-derived, printed-only and external values</caption>
<thead><tr><th scope="col">Entry / output</th><th scope="col">Corpus / basis</th><th scope="col">Printed</th><th scope="col">Derived</th><th scope="col">Verdict</th><th scope="col">Qualification</th></tr></thead><tbody>
""")
    for row in ledger:
        search = " ".join(str(row[field]) for field in ("entry_id", "target_id", "printed_value", "derived_value", "qualification")).lower()
        entry_id = re.sub(r"[^a-zA-Z0-9_-]", "-", row["entry_id"])
        printed = f'{row["printed_value"]} {row["unit"]}'.strip()
        parts.append(
            f'<tr id="entry-{entry_id}" data-claim="{html.escape(row["claim_id"])}" data-verdict="{html.escape(row["verdict"])}" data-search="{html.escape(search, quote=True)}">'
            f'<th scope="row"><code>{html.escape(row["entry_id"])}</code><br><span class="small">{html.escape(row["claim_id"])} · {_source_link(row["source_path"])}</span></th>'
            f'<td>{html.escape(row["corpus"])}<br><span class="small">{html.escape(row["basis"])}</span></td>'
            f'<td>{html.escape(printed)}</td><td>{html.escape(row["derived_value"])}</td><td>{_status(row["verdict"])}</td><td>{html.escape(row["qualification"])}</td></tr>'
        )
    parts.append("""</tbody></table></div>
<p><a href="ledger.json">Machine-readable ledger</a> · <a href="input-manifest.json">Accepted-source receipts</a> · <a href="run-manifest.json">Output and code receipts</a></p>
</section>
<section id="methods" class="panel" aria-labelledby="methods-title">
<h2 id="methods-title">Methods, custody and limits</h2>
<ul>
<li><strong>Source contract:</strong> FROZEN v1 with Amendment A1. Accepted run outputs are hash-verified before Stage 7 writes anything. Earlier runs and raw inputs remain unchanged.</li>
<li><strong>Populations:</strong> figures use all released rows. Table 2 uses complete exact-key split joins. Table 13 Rule A/B are interpretations; Rule S is sensitivity only.</li>
<li><strong>Table 11:</strong> faithful fractions use physical keep=0 rows divided by physical totals. Exact full-ID and host-level estimands stay separate.</li>
<li><strong>Non-goals:</strong> no substring recount, EXACTSUBSTR run, NEARDUP reimplementation, memorization, perplexity or model-quality conclusion.</li>
<li><strong>Rights:</strong> raw clusters, dataset rows and the source PDF remain local. This reader contains aggregate values only. Publication is a separate user decision.</li>
</ul>
<p><a href="../../../../README.md">Project README</a> · <a href="../../../../PREREGISTRATION.md">Frozen analysis contract</a> · <a href="../../../../CLAIM_INVENTORY.md">Claim inventory</a></p>
</section>
</main>
<footer class="wrap">Stage 7 integrated offline reader · generated deterministically from accepted aggregate artifacts.</footer>
<script>
(() => {
  const status = document.getElementById('ledger-status');
  const query = document.getElementById('ledger-query');
  const claim = document.getElementById('ledger-claim');
  const verdict = document.getElementById('ledger-verdict');
  const rows = Array.from(document.querySelectorAll('.ledger-table tbody tr'));
  const filter = () => {
    const needle = query.value.trim().toLowerCase();
    let visible = 0;
    for (const row of rows) {
      const show = (!needle || row.dataset.search.includes(needle)) && (!claim.value || row.dataset.claim === claim.value) && (!verdict.value || row.dataset.verdict === verdict.value);
      row.hidden = !show;
      if (show) visible += 1;
    }
    status.textContent = `${visible} of ${rows.length} ledger entries shown`;
  };
  query.addEventListener('input', filter);
  claim.addEventListener('change', filter);
  verdict.addEventListener('change', filter);
  filter();
  for (const select of document.querySelectorAll('[data-convention-select]')) {
    select.addEventListener('change', () => {
      for (const panel of document.querySelectorAll(`[data-convention-panel="${select.dataset.conventionSelect}"]`)) {
        panel.hidden = panel.dataset.convention !== select.value;
      }
    });
  }
})();
</script>
</body>
</html>
""")
    return publication_language("".join(parts))


def build_report(root, ledger, figures, run="run-001"):
    root = Path(root)
    arithmetic = read_json(root / "planning/step0/arithmetic.json")
    random_ee = read_json(root / ACCEPTED_RUNS["stage2"] / "random-split-ee.json")
    expected_validation = (Decimal(random_ee["probability"]) * Decimal(random_ee["evaluation_size"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    supporting = next(row for row in arithmetic["derivations"] if row["id"] == "c4_neardup_supporting_anchors")
    lines = [
        "# Integrated report — Lee et al. released-cluster duplication audit",
        "",
        f"**Contract:** FROZEN v1 with custody Amendment A1. **Stage 7 candidate:** {run}. **Reader:** [offline visualizer and complete ledger](index.html).",
        "",
        "## Principal result",
        "",
        "The released C4, RealNews and Wiki-40B archives reproduce all **33/33 printed bars** under the predeclared `dropped` edge convention. They do not reproduce the printed C4 train-with-train rate: direct membership gives **16,892,539 / 364,868,892 = 4.63%**, versus **3.04%** (`MISMATCH`). This is a bounded duplication-statistics audit, not a test of model quality, perplexity or memorization.",
        "",
        "## C4 findings",
        "",
        "- Direct Table 2: TT **4.63%** (`MISMATCH`), observed validation-with-validation **1.58%** (`MISMATCH`), validation-with-train **4.60%** (`MATCH`).",
        f"- Secondary random-split EE: **1.60%** (`MISMATCH`) under a uniform fixed-size validation split. The whole-population weighted numerator **N × E[P_EE]** is {random_ee['expected_numerator']}; the expected validation-split count **V × E[P_EE]** is **{number(expected_validation)}**. These bases are distinct from each other and from direct observed EE.",
        "- Table 13: Rule A removes **14,393,547**, retains **350,475,345 → 350.48M** (`MATCH`); Rule B retains **350.49M** (`MISMATCH`); all-train Rule S retains **347.97M** (`MISMATCH`). Rules A/B are interpretations, not observed author deletions; Rule S is sensitivity only.",
        "- §5.1: size-2 clusters **1,861,744 → 1.9M**, not printed 1.8M; pair majority `MATCH`; 280 clusters over 5,000 and largest 250,933 both `MATCH`.",
        "- Table 11: exact full-ID totals are zero for all 19 printed strings, but this does not reproduce or contradict the host-like estimand. The promised twentieth row remains `SOURCE_MISSING`.",
        "",
        "### Alternative C4 percentages and bounds",
        "",
        "| Value | Basis | Disposition |",
        "|---|---|---|",
        "| 1.68% | External Google Research abstract; unresolved denominator | External context; not a PDF Table 2 substitute |",
        "| 3.04% | Printed Table 2 TT | Direct recount 4.63%, `MISMATCH` |",
        f"| {supporting['outputs']['table13_reduction_percent']}% → 3.9% | Independently rounded Table 13 sizes and Appendix D | `CONSISTENT_INTERVAL` |",
        "| 14.39M nominal removal | Difference of rounded Table 13 sizes | Exact-original and printed-difference intervals remain separate |",
        "| [8,001,466, 14,410,977] | Conditional Figure 1 train-removal bounds | `CONSISTENT_INTERVAL`; upper is 3.949631584377437% of train |",
        "| 4.63% | Direct TT; separately, all-release multi-document membership share | Different estimands; neither is interchangeable with removals |",
        "",
        "The Step-0 common-population keep-one ceiling remains `CONTRADICTION`, with robust minimum shortfall **2,905,134.2386**. Figure 1's conditional printed-only bounds remain `CONSISTENT_INTERVAL` with Table 13.",
        "",
        "## Wiki-40B findings",
        "",
        "TT is **20,465 / 2,926,536 = 0.70%** versus printed 0.39% (`MISMATCH`). Validation EE/ET are **0.26% / 0.70%** (`MATCH` / `MISMATCH`); test EE/ET are **0.26% / 0.72%** (`MATCH` / `MATCH`). The paper's `valid` label is not renamed. All evaluated retained sizes round to 2.91M, without identifying an author deletion rule.",
        "",
        "## RealNews findings",
        "",
        "The split-free keep-one ceiling is **U = 4,880,719 − 2,097,951 = 2,782,768**, so `CEILING_COMPATIBLE`. This is **not a train-size match**. Conditional release-population Table 13 sizes are 32.80M and 30.01M (`MISMATCH` each), not verified public train sizes. All three Table 2 cells and direct train removals remain `NOT_EXECUTABLE_INPUT`.",
        "",
        "All 19 exact full-ID URL totals are zero; fractions are non-executable. Zero IDs meet the derived ranking's exact-ID `total >= 10` filter, so the empty ranking is expected under that rule and is not a host-level contradiction.",
        "",
        "## LM1B and printed-only checks",
        "",
        "No LM1B cluster archive is pinned; all Table 2 cells and cluster recounts remain `NOT_EXECUTABLE_INPUT`. The conditional printed-only train-removal floor is **510,877**, exceeding Table 13's largest printed-difference-compatible value by **70,877** (`CONTRADICTION`). The conclusion depends on full-population figure coverage, public-test evaluation mapping and keep-one semantics.",
        "",
        "Repeated-sentence percentages round to 0.02%; NEARDUP Table 13 and Appendix C/D anchors are consistent; C4 EXACTSUBSTR's 350.48M conflicts with Appendix C and method context (`CONTRADICTION`) without establishing a copy error.",
        "",
        "## Figures and complete ledger",
        "",
    ]
    for panel in figures["panels"]:
        if panel["released"]:
            counts = panel["match_counts"]
            edge_text = ", ".join(f"{row['cluster_size']}: {number(row['cluster_count'])} clusters / {number(row['document_count'])} documents" for row in panel["edges"])
            lines.append(f"- **{panel['title']}:** dropped {counts['dropped']}/11, low {counts['low']}/11, high {counts['high']}/11. Exact omitted edges — {edge_text}.")
        else:
            lines.append("- **Figure 8 top — LM1B:** all 11 bars are printed-only; no archive or edge convention is inferred.")
    lines.extend([
        "",
        f"The [complete ledger](ledger.csv) contains {len(ledger)} entries covering all 193 printed-oracle rows, expanded evaluation arms, removal rules and figure conventions, plus secondary and external context. Every entry links its source output and verdict. Non-executable entries carry explicit reasons.",
        "",
        "## Verification and reproduction",
        "",
        "Stage 7 verifies every accepted Stage 1–3 output against its immutable run manifest before writing outputs. The build is standard-library Python; the reader is dependency-free HTML/CSS/JavaScript/SVG with semantic chart tables and no runtime network requirement.",
        "",
        "```bash",
        "python -B src/verify_stage7.py",
        f"python -B src/stage7_build.py --out-dir results/stage7/{run}/audit",
        f"python -B src/verify_stage7.py --run-dir results/stage7/{run}/audit",
        "```",
        "",
        f"To regenerate, replace `{run}` with an unused run name. Named runs are immutable. Raw clusters, source rows and the PDF remain local; only aggregates enter the reader. Publication and any redistribution require separate user decisions.",
        "",
    ])
    return publication_language("\n".join(lines))


def build_stage7(root, out_dir):
    root = Path(root)
    out_dir = Path(out_dir)
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError(f"refusing to overwrite Stage 7 outputs in {out_dir}")
    run = out_dir.parent.name
    match = re.fullmatch(r"run-(\d{3})", run)
    assert match, f"invalid Stage 7 run name: {run}"
    sequence = int(match.group(1))
    receipts = verify_accepted_sources(root)
    ledger = _build_ledger(root)
    figures = _figures(root)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "input-manifest.json", receipts)
    write_csv(out_dir / "ledger.csv", ledger)
    write_json(out_dir / "ledger.json", ledger)
    write_json(out_dir / "figures.json", figures)
    write_text(out_dir / "index.html", render_html(root, ledger, figures))
    write_text(out_dir / "report.md", build_report(root, ledger, figures, run))
    for panel in figures["panels"]:
        convention = panel["primary"] if panel["released"] else "dropped"
        write_text(out_dir / f"{panel['id']}.svg", render_panel_svg(panel, convention) + "\n")
    outputs = {}
    for path in sorted(out_dir.iterdir()):
        if path.is_file() and path.name != "run-manifest.json":
            outputs[path.name] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    write_json(out_dir / "run-manifest.json", {
        "stage": f"Stage 7 / {run}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "supersedes": None if sequence == 1 else f"run-{sequence - 1:03d}",
        "accepted_runs": ACCEPTED_RUNS,
        "reader_entry": "index.html",
        "oracle_rows": 193,
        "ledger_entries": len(ledger),
        "outputs": outputs,
        "code_sha256": {
            name: sha256(root / "src" / name)
            for name in ("stage1_audit.py", "stage7_build.py", "verify_stage7.py")
        },
    })
    return out_dir


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    print(build_stage7(args.root, args.out_dir))


if __name__ == "__main__":
    main()
