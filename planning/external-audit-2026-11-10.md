# External Audit Report: Step 0, Stage 1 (`Wiki-40B`), and Stage 2 (`C4`)

- **Date:** 2026-11-10
- **Auditor:** Gemini 4 Argon (High) — Katflow session `#2838` (`Review [review]`)
- **Project:** `paper-claims/lee-training-data-dedup` (`2107.06499-deduplicating-training-data-makes-language-models-better`)
- **Scope:** Cross-family Type-B independent review + lightweight Type-A verification of Step 0 (`FROZEN v1` + Amendment A1), Stage 1 (`results/stage1/run-004/audit/`), and Stage 2 (`results/stage2/run-004/audit/`).
- **Overall Verdict:** **PASS** (Zero blocking defects; 4 non-blocking findings / Stage 3–7 recommendations).

---

## 1. Independent Verification Executed

1. **Step 0 Freeze & Oracle Verification:**
   - Verified `planning/FREEZE-v1.json`: 12/14 listed files match their `2026-11-08T20:19:22Z` SHA-256 digests byte-for-byte, including all three immutable snapshots (`planning/preregistration-v1.md`, `planning/claim-inventory-v1.md`, `planning/step0-derivations-v1.md`) and both oracle tables (`paper/targets/printed-targets.csv` [193 rows], `paper/targets/figure-bars.csv` [44 rows]).
   - Verified `PREREGISTRATION.md` is an exact append-only extension of `planning/preregistration-v1.md` (`prereg_current.startswith(prereg_v1)` holds) containing only dated **Amendment A1** (`2026-11-09`), and `data/raw/MANIFEST.md` reflects post-freeze Stage 1–2 acquisitions.
   - Independently re-derived all Step 0 printed-only checks in `planning/step0/arithmetic.json`:
     - C4 Table 2 (`3.04%`) vs Table 13 (`364.87M -> 350.48M`): nominal ceiling `11,456,622.3168`, rounding-aware strict ceiling `< 11,474,865.7614` vs Table 13 minimum `14,380,000` -> robust minimum shortfall `2,905,134.2386` documents (`CONTRADICTION`).
     - Figure 1 bounds: `348,320,475` singletons, `2,502,048` plotted multi-document clusters, lower-edge multi-document count `10,868,122`, whole-population keep-one floor `8,366,074`, validation-adjusted train-removal floor `8,001,466` (`2.193%`), upper bound `14,410,977` (`3.950%`) -> `CONSISTENT_INTERVAL` with Table 13.
     - LM1B printed-only removal floor: `1,505,410 - 687,845 - 306,688 = 510,877` vs Table 13 `(420,000, 440,000)` -> minimum excess `70,877` (`CONTRADICTION`).

2. **Stage 1 (`Wiki-40B`) Verification (`results/stage1/run-004/audit/`):**
   - Executed `python -B src/verify_stage1.py` (10/10 unit tests PASS) and `python -B src/verify_stage1_report.py --run-dir results/stage1/run-004/audit` (all 19 output SHA-256 digests, 3 script digests, verdicts, and LF endings PASS).
   - Verified `stat()` byte sizes of all 24 Stage 1 raw inputs (`wiki40b.tar.gz` + 23 Parquet shards = `6,210,605,868` bytes).
   - Independently streamed `results/stage1/run-004/audit/cluster-composition.csv` (`3,234,610` clusters, `63,582,029` bytes) and `cluster-histogram.csv` row-by-row, reproducing:
     - `3,252,407` physical rows (`2,926,536` train, `163,597` validation, `162,274` test), `3,228,888` singletons (`keep=1`), `5,722` multi-document clusters (`23,519` rows, all `keep=0`), `0` discrepancies.
     - Figure 8(c) convention lock: `dropped` matches `11/11` bars (omitting `39` size-10 and `10` size-20 clusters), `low` `9/11`, `high` `9/11` -> `dropped` uniquely locked as `PRIMARY_LOCKED`.
     - Table 2 numerators: `TT = 20,465` (`0.6993%` -> `0.70%` vs printed `0.39%`, `MISMATCH`); validation `EE = 432` (`0.2641%` -> `0.26%`, `MATCH`), `ET = 1,138` (`0.6956%` -> `0.70%` vs `0.72%`, `MISMATCH`); test `EE = 418` (`0.2576%` -> `0.26%`, `MATCH`), `ET = 1,163` (`0.7167%` -> `0.72%`, `MATCH`).
     - Table 13 removals across all 3 arms (`validation`: `A=16,304, B=15,461, S=21,148`; `test`: `A=16,340, B=15,461, S=21,148`; `validation+test`: `A=16,996, B=15,461, S=21,148`), all within `(11,536, 21,536]` (`2.91M`, `MATCH` / `CONSISTENT_INTERVAL`).

3. **Stage 2 (`C4`) Verification (`results/stage2/run-004/audit/`):**
   - Executed `python -B src/verify_stage2.py` (13/13 unit tests PASS) and `python -B src/verify_stage2_report.py --run-dir results/stage2/run-004/audit` (all 30 output SHA-256 digests, 8 script digests, verdicts, and LF endings PASS).
   - Verified `stat()` byte sizes of all local Stage 2 archives and DuckDB stores (`c4.tar.gz` `13,872,073,006` B, 2 validation Parquets `509,275,778` B, `public.duckdb` `14,786,244,608` B, `c4.duckdb` `36,895,207,424` B) and verified all `1,024/1,024` streamed train shard receipts in `results/stage2/run-002/split-acquisition-manifest.json` against `train-source-metadata.json` (`326,778,635,540` bytes, `364,868,892` rows, `1,024/1,024` LFS SHA-256 matches).
   - Independently recomputed from `results/stage2/run-004/audit/cluster-histogram.csv`:
     - `365,233,500` physical rows, `350,835,689` unique clusters (`348,320,475` singletons + `2,515,214` multi-document clusters = `16,913,025` multi-document rows; whole-release keep-one removals `14,397,811`).
     - Figure 1 convention check: `dropped` matches `11/11` bars (`low` `7/11`, `high` `7/11`), with omitted exact edge sizes `10: 9,974`, `20: 2,400`, `50: 788`, `500: 4`, `5000: 0` (`13,166` total omitted clusters; `2,515,214 - 13,166 = 2,502,048` plotted multi-document clusters).
     - Exact finite-population random-split EE expectation: `E[P_EE] = 0.0160424045...` (`1.604240%` -> `1.60%` vs printed `1.59%`, `MISMATCH`).

---

## 2. Non-Blocking Findings & Stage 3–7 Guardrails

1. **Random-Split EE `expected_numerator` Basis Labeling (`src/stage2_audit.py` & `src/stage2_report.py`):**
   - `random_split_ee_from_histogram` accumulates `sum_{s>=2} s * n_s * [1 - C(T, s-1)/C(N-1, s-1)] = 5,859,223.5526...` and divides by `N = 365,233,500` to obtain `E[P_EE] = 1.604240%` (`1.60%`).
   - The probability, percentage, and `MISMATCH` verdict are mathematically exact, but `5,859,223.55` is the *whole-population* weighted numerator (`N * E[P_EE]`), whereas the expected count of validation documents with a validation partner over `V = 364,608` is `V * E[P_EE] = 5,849.19` (directly comparable to the observed EE numerator `5,754`).
   - **Action for Stage 3 (`RealNews`) & Stage 7:** Report both `V * E[P_EE]` (expected validation-split count) and `N * E[P_EE]` (whole-population weighted numerator) with explicit basis labels.

2. **`url_stats` Pre-Filtering by `keep0_urls` (`src/stage2_audit.py` lines 298–308):**
   - `url_stats` joins `released` against `keep0_urls` (`SELECT DISTINCT id FROM released WHERE keep = 0`), excluding URLs that appear only with `keep = 1`.
   - In C4 (`run-004`), this is harmless because `duplicate_released_urls = 0` and none of the 19 printed Table 11 strings (`hairtechkearney.com`, etc.) appear in `released`.
   - **Action for Stage 3 (`RealNews`):** Do not copy the `keep0_urls` pre-filter into any lookup where a queried URL could exist in `released` with only `keep = 1` rows.

3. **Freeze Verification Protocol for Post-Freeze Amendments (`planning/FREEZE-v1.json`):**
   - `planning/preregistration-v1.md`, `planning/claim-inventory-v1.md`, and `planning/step0-derivations-v1.md` preserve the exact frozen v1 bytes, while `PREREGISTRATION.md` has Amendment A1 appended and `data/raw/MANIFEST.md` has Stage 1–2 acquisition updates.
   - **Action for Stage 7:** Ensure any final freeze-verification script checks `planning/*-v1.md` against `FREEZE-v1.json` for exact SHA-256 equality and checks `PREREGISTRATION.md` for prefix equality (`prereg_current.startswith(prereg_v1)`).

4. **Cold-Disk Full SHA-256 Re-Hash Deferred to Stage 7:**
   - Per operator guidance while the workstation was in active use, multi-GB raw archive re-hashing (`verify_stage1.py --run-dir ...` and `verify_stage2.py --full --run-dir ...`) was replaced in this review session by `stat()` byte-size verification, output-manifest SHA-256 verification, Stage 1 `cluster-composition.csv` re-summation, Stage 2 `cluster-histogram.csv` recomputation, and 1,024-shard LFS receipt verification.
