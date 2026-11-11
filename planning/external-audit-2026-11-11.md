# External Audit Report: Stage 3 (`RealNews`) and Final Stage 7 (`run-002`)

- **Date:** 2026-11-11
- **Auditor:** Gemini 4 Argon (High) — Katflow session `#2856` (`Review [review]`)
- **Project:** `paper-claims/lee-training-data-dedup` (`2107.06499-deduplicating-training-data-makes-language-models-better`)
- **Scope:** Cross-family Type-B independent review + Type-A verification of Stage 3 (`results/stage3/run-002/audit/`), Stage 7 (`results/stage7/run-002/audit/`), closure of the four Stage 3–7 guardrails from `planning/external-audit-2026-11-10.md`, evaluation of the deferred Minor items in `results/stage3/run-002/progress.md` and `results/stage7/run-002/progress.md`, and Pre-Publication Reader Gate (`INVESTIGATION_CHECKLIST.md` Layer A & Layer B) + publication-safety inspection.
- **Overall Verdict:** **PASS** (Zero blocking scientific, reader-clarity, or verification defects; 3 non-blocking publication-packaging / portability observations).
- **Correction note (2026-11-11, Kimi K3.1 Pro):** Five narrative transcription errors identified during the independent post-audit check were corrected below: the Stage 3 histogram row count, a nonexistent printed URL, the custody regression-test name, the external 1.68% source, and the direct 4.60% estimand. These corrections do not change any numerical result or the PASS verdict.

---

## 1. Independent Verification Executed

1. **Automated Unit Tests & Run Verifiers:**
   - `python -B src/verify_stage1.py` (10/10 unit tests PASS) and `python -B src/verify_stage1_report.py --run-dir results/stage1/run-004/audit` (PASS).
   - `python -B src/verify_stage2.py` (13/13 unit tests PASS) and `python -B src/verify_stage2_report.py --run-dir results/stage2/run-004/audit` (PASS).
   - `python -B src/verify_stage3.py` (19/19 unit tests PASS) and `python -B src/verify_stage3_report.py --run-dir results/stage3/run-002/audit` (PASS).
   - `python -B src/verify_stage7.py` (13/13 unit tests PASS) and `python -B src/verify_stage7.py --run-dir results/stage7/run-002/audit` (PASS).

2. **Stage 3 (`RealNews`, `results/stage3/run-002/audit/`) Independent Re-Derivation:**
   - Independently re-summed `results/stage3/run-002/audit/cluster-histogram.csv` (`149` size rows) and queried `work/realnews.duckdb` read-only:
     - `32,797,763` physical rows, `32,797,763` unique released IDs (`0` duplicate IDs), `30,014,995` unique `group_id` clusters (`27,917,044` singletons with `keep=1`; `2,097,951` multi-document clusters with `4,880,719` rows, all `keep=0`).
     - Split-free keep-one removal ceiling: `U = 4,880,719 - 2,097,951 = 2,782,768 > 2,760,000` (`CEILING_COMPATIBLE`, explicitly qualified as not a train-size match).
     - Figure 8(b) convention check: `dropped` matches `11/11` bars (`low` `8/11`, `high` `8/11`; omitted exact edge sizes `10: 703`, `20: 24`, `50: 6`, `500: 0`, `5000: 0`; `2,097,218` plotted multi-document clusters).
     - Conditional release-population Table 13 check: `32.80M` (`32,797,763`) vs printed `31.16M` and `30.01M` (`30,014,995`) vs printed `28.39M`, properly labeled `CONDITIONAL_RELEASE_POPULATION` (`MISMATCH`), while Table 2 split cells (`TT`, `EE`, `ET`, random-split EE) and direct train removals remain `NOT_EXECUTABLE_INPUT`.
     - Table 11 URL granularity check: in `work/realnews.duckdb`, every `id` is a full article URL (`https://allafrica.com/stories/...`) with `MAX(total) = 1`, whereas printed Table 11 lists bare domains (`medicalnewstoday.com.`, `dodbuzz.com`, `ftp.screenrant.com`), confirming that exact-ID `0` counts and the empty `total >= 10` derived ranking do not contradict host-level aggregation.

3. **Closure of Prior External Audit Guardrails (`planning/external-audit-2026-11-10.md`):**
   - **Guardrail 1 (Random-Split EE Basis Labeling):** Verified in `src/stage7_build.py`, `results/stage7/run-002/audit/report.md`, `index.html`, and `ledger.csv` (`c4-random-split-ee`): both `V × E[P_EE] = 5,849.19` (expected validation-split count over `V = 364,608`, comparable to observed `5,754`) and `N × E[P_EE] = 5,859,223.55...` (whole-population weighted numerator over `N = 365,233,500`) are reported with explicit basis labels.
   - **Guardrail 2 (Stage 3 `url_stats` Without `keep=0` Pre-Filter):** Verified in `src/stage3_audit.py` lines 253–264 and pinned by `test_url_stats_preserves_keep1_only_and_duplicate_ids` and `test_keep1_only_url_omission_is_rejected` in `src/verify_stage3.py`.
   - **Guardrail 3 (Freeze Contract Verification):** Verified in `src/stage7_build.py` (`verify_freeze_contract`) and `src/verify_stage7.py`: all 12 unchanged files in `planning/FREEZE-v1.json` match their frozen SHA-256 digests byte-for-byte, and `PREREGISTRATION.md` satisfies `current.startswith(snapshot)` with only dated Amendment A1 (`2026-11-09`) appended.
   - **Guardrail 4 (Cold-Disk Full Verification):** Verified in `results/stage7/run-001/cold-disk-verification.log`: `verify_stage1.py --run-dir results/stage1/run-004/audit`, `verify_stage2.py --full --run-dir results/stage2/run-004/audit`, and `verify_stage3.py --full --run-dir results/stage3/run-002/audit` all exited `0`.

4. **Stage 7 (`results/stage7/run-002/audit/`) Integration & Verifier Independence:**
   - Verified 100% coverage of all 193 rows in `paper/targets/printed-targets.csv` across the 286 ledger entries in `ledger.csv` and `ledger.json`.
   - Verified that all 9 numerical and reader artifacts (`index.html`, `ledger.csv`, `ledger.json`, `figures.json`, `input-manifest.json`, and 4 standalone SVGs) are byte-for-byte identical between `results/stage7/run-001/audit/` and `results/stage7/run-002/audit/`, while `src/verify_stage7.py` now enforces fresh accepted-source SHA-256 verification against `input-manifest.json` (`test_coordinated_accepted_output_and_manifest_change_is_rejected`).
   - Verified that all 302 relative file links, 6 internal `#anchor` links, and 1 external link in `results/stage7/run-002/audit/index.html` resolve cleanly, with zero external runtime assets (`<script src>`, `<link href>`, `<img src>`, `url(http...)`, `@import`) and zero `\r\n` bytes across all Stage 3 and Stage 7 source and audit files.

---

## 2. Reader Clarity & Pre-Publication Reader Gate (`INVESTIGATION_CHECKLIST.md`)

- **Layer A (Universal Reader Gate) — PASS:**
  1. *Headline first:* Both `index.html` and `report.md` lead immediately with the dual outcome (all `33/33` released histogram bars match under `dropped`, whereas C4 direct `TT` is `4.63%` vs printed `3.04%`, reconciling the Step 0 `2,905,134.2386`-document shortfall against Table 13's `364.87M -> 350.48M`).
  2. *Adjacent qualifiers:* Every headline figure, card, and ledger row carries its scope/arm/convention/unit-granularity qualifier immediately beside the number.
  3. *Self-contained visual encodings:* SVG histograms plot `log10(groups + 1)` with exact printed/derived counts labeled on every bar, `<title>`/`<desc>` accessibility tags, and collapsible full numeric tables covering `dropped`, `low`, `high`, and omitted exact edges (`10`, `20`, `50`, `500`, `5000`).
  4. *Terminology & navigation:* Project codes (`TT`, `EE`, `ET`, Arms `A`/`B`/`S`, `dropped`/`low`/`high`, `U = N_multi - K_multi`) are defined in plain language at first use; all links and collapsible `<details>` work without external assets.
- **Layer B (Genre Supplement — Claim Verification & Methodological Comparison) — PASS:**
  - Every target row states printed value, derived value, difference, verdict, and evidence basis side by side.
  - The dedicated C4 percentage disambiguation table cleanly separates `1.68%` (external Google Research abstract), `3.04%` (printed Table 2 `TT`), `3.9%` (`1 - 350.48 / 364.87` Table 13 ratio), `[2.193%, 3.950%]` (Step 0 Figure 1 interval), `4.63%` (Stage 2 direct released `TT`), and `4.60%` (direct validation-with-train).
  - Non-evaluated original-idea Stages 4–6 (`47` out-of-scope rows) and blocked split inputs (`17` `NOT_EXECUTABLE_INPUT` rows) are explicitly accounted for without overclaiming.

---

## 3. Evaluation of Deferred Minor Items (`results/stage7/run-002/progress.md`)

1. **`realnews-zero-eligibility-ranking` Status Label (`MISMATCH` vs `NOT_EXECUTABLE_INPUT`):**
   - **Assessment:** Scientifically benign as shipped. Both `report.md` and the adjacent `qualification` field in `ledger.csv` / `index.html` state explicitly that `0` eligible IDs under `total >= 10` is an expected consequence of unique full-article URLs in `realnews.tar.gz` and does not establish a host-level contradiction against printed Table 11. Reclassifying to `NOT_EXECUTABLE_INPUT` in a future reader pass is optional polish, not a scientific defect.
2. **Exact H1/Lede Wording Not Regression-Pinned in `src/verify_stage7.py`:**
   - **Assessment:** Low risk. `test_html_is_offline_accessible_and_links_resolve` and `test_integrated_report_preserves_headlines_and_alternative_bases` already pin the key claims, numbers, and qualifiers, and `verify_run` verifies deterministic regeneration of the entire HTML and Markdown bytes against `run-manifest.json`.
3. **Historical Workstation Path in `results/stage1/run-004/audit/report.md` Line 15:**
   - **Assessment:** Correctly left unedited on disk to preserve the immutable Stage 1 run receipt and SHA-256 manifest. See Observation 1 below for the complete inventory of workstation paths across Stage 1–3 receipts before any external publication.

---

## 4. Non-Blocking Publication-Safety & Cross-Family Observations

1. **Complete Inventory of Workstation Paths in Stage 1–3 Audit Receipts (Publication Safety):**
   - `results/stage7/run-002/audit/*`, top-level documentation (`README.md`, `SCOPE.md`, `PREREGISTRATION.md`, `CLAIM_INVENTORY.md`), and Stage 2–3 `report.md` contain **zero** private workstation paths.
   - However, in addition to `results/stage1/run-004/audit/report.md` (line 15), a workstation-user path prefix is recorded in **five Stage 1–3 JSON receipt files**:
     - `results/stage1/run-004/audit/input-manifest.json` (`command`, `inputs[*].local_path`, `split_files[*].path`)
     - `results/stage2/run-004/audit/input-manifest.json` (`command`, `inputs[*].local_path`)
     - `results/stage2/run-004/audit/full-input-manifest.json` (`command`, `inputs[*].local_path`, `acquisition_manifest`, `public_split_store.path`, `train_source_metadata`, `work_db`)
     - `results/stage2/run-004/audit/custody-verification.json` (`public_split_store.path`, `validation_files[*].local_path`) — linked directly from top-level `README.md` (line 57) and `results/README.md` (line 9).
     - `results/stage3/run-002/audit/input-manifest.json` (`command`, `inputs[*].local_path`, `acquisition_manifest`)
   - **Recommendation:** Keep the immutable Stage 1–3 run directories untouched in the local Atelier workspace, but if preparing a public release or static-site bundle, either redact/relativize those path fields in the exported copy or exclude those five JSON manifest receipts (and Stage 1 `report.md` line 15) from the public bundle.

2. **Relative Link Root Assumption in `results/stage7/run-002/audit/index.html` (Deployment Geometry):**
   - All 302 relative file links in `index.html` traverse four directories up (`../../../../paper/targets/...`, `../../../../results/stage2/run-004/audit/...`, `../../../../README.md`).
   - **Recommendation:** Serve or publish from the member project root (with `results/stage7/run-002/audit/index.html` as the entry path), not by uploading `results/stage7/run-002/audit/` alone as a standalone web root.

3. **Future Relocation to the Alternate Project Drive (Cross-Root Verifier Portability):**
   - Per `.paper-claims/AGENTS.md`, completed heavy members may later move to the alternate project drive. `src/verify_stage7.py --run-dir results/stage7/run-002/audit` uses `ROOT`-relative paths and will continue to pass after a move, whereas `src/verify_stage1.py`, `src/verify_stage2.py`, and `src/verify_stage3.py` resolve raw input paths from `input-manifest.json` unless updated or run where the original workstation paths remain accessible.
