# Integrated report — Lee et al. released-cluster duplication audit

**Contract:** FROZEN v1 with custody Amendment A1. **Stage 7 candidate:** run-002. **Reader:** [offline visualizer and complete ledger](index.html).

## Principal result

The released C4, RealNews and Wiki-40B archives reproduce all **33/33 printed bars** under the predeclared `dropped` edge convention. They do not reproduce the printed C4 train-with-train rate: direct membership gives **16,892,539 / 364,868,892 = 4.63%**, versus **3.04%** (`MISMATCH`). This is a bounded duplication-statistics audit, not a test of model quality, perplexity or memorization.

## C4 findings

- Direct Table 2: TT **4.63%** (`MISMATCH`), observed validation-with-validation **1.58%** (`MISMATCH`), validation-with-train **4.60%** (`MATCH`).
- Secondary random-split EE: **1.60%** (`MISMATCH`) under a uniform fixed-size validation split. The whole-population weighted numerator **N × E[P_EE]** is 5859223.55260572805972103758998352383330684415405889919380667; the expected validation-split count **V × E[P_EE]** is **5,849.19**. These bases are distinct from each other and from direct observed EE.
- Table 13: Rule A removes **14,393,547**, retains **350,475,345 → 350.48M** (`MATCH`); Rule B retains **350.49M** (`MISMATCH`); all-train Rule S retains **347.97M** (`MISMATCH`). Rules A/B are interpretations, not observed author deletions; Rule S is sensitivity only.
- §5.1: size-2 clusters **1,861,744 → 1.9M**, not printed 1.8M; pair majority `MATCH`; 280 clusters over 5,000 and largest 250,933 both `MATCH`.
- Table 11: exact full-ID totals are zero for all 19 printed strings, but this does not reproduce or contradict the host-like estimand. The promised twentieth row remains `SOURCE_MISSING`.

### Alternative C4 percentages and bounds

| Value | Basis | Disposition |
|---|---|---|
| 1.68% | External Google Research abstract; unresolved denominator | External context; not a PDF Table 2 substitute |
| 3.04% | Printed Table 2 TT | Direct recount 4.63%, `MISMATCH` |
| 3.943870419601502% → 3.9% | Independently rounded Table 13 sizes and Appendix D | `CONSISTENT_INTERVAL` |
| 14.39M nominal removal | Difference of rounded Table 13 sizes | Exact-original and printed-difference intervals remain separate |
| [8,001,466, 14,410,977] | Conditional Figure 1 train-removal bounds | `CONSISTENT_INTERVAL`; upper is 3.949631584377437% of train |
| 4.63% | Direct TT; separately, all-release multi-document membership share | Different estimands; neither is interchangeable with removals |

The Step-0 common-population keep-one ceiling remains `CONTRADICTION`, with robust minimum shortfall **2,905,134.2386**. Figure 1's conditional printed-only bounds remain `CONSISTENT_INTERVAL` with Table 13.

## Wiki-40B findings

TT is **20,465 / 2,926,536 = 0.70%** versus printed 0.39% (`MISMATCH`). Validation EE/ET are **0.26% / 0.70%** (`MATCH` / `MISMATCH`); test EE/ET are **0.26% / 0.72%** (`MATCH` / `MATCH`). The paper's `valid` label is not renamed. All evaluated retained sizes round to 2.91M, without identifying an author deletion rule.

## RealNews findings

The split-free keep-one ceiling is **U = 4,880,719 − 2,097,951 = 2,782,768**, so `CEILING_COMPATIBLE`. This is **not a train-size match**. Conditional release-population Table 13 sizes are 32.80M and 30.01M (`MISMATCH` each), not verified public train sizes. All three Table 2 cells and direct train removals remain `NOT_EXECUTABLE_INPUT`.

All 19 exact full-ID URL totals are zero; fractions are non-executable. Zero IDs meet the derived ranking's exact-ID `total >= 10` filter, so the empty ranking is expected under that rule and is not a host-level contradiction.

## LM1B and printed-only checks

No LM1B cluster archive is pinned; all Table 2 cells and cluster recounts remain `NOT_EXECUTABLE_INPUT`. The conditional printed-only train-removal floor is **510,877**, exceeding Table 13's largest printed-difference-compatible value by **70,877** (`CONTRADICTION`). The conclusion depends on full-population figure coverage, public-test evaluation mapping and keep-one semantics.

Repeated-sentence percentages round to 0.02%; NEARDUP Table 13 and Appendix C/D anchors are consistent; C4 EXACTSUBSTR's 350.48M conflicts with Appendix C and method context (`CONTRADICTION`) without establishing a copy error.

## Figures and complete ledger

- **Figure 1 — C4:** dropped 11/11, low 7/11, high 7/11. Exact omitted edges — 10: 9,974 clusters / 99,740 documents, 20: 2,400 clusters / 48,000 documents, 50: 788 clusters / 39,400 documents, 500: 4 clusters / 2,000 documents, 5000: 0 clusters / 0 documents.
- **Figure 8 middle — RealNews:** dropped 11/11, low 8/11, high 8/11. Exact omitted edges — 10: 703 clusters / 7,030 documents, 20: 24 clusters / 480 documents, 50: 6 clusters / 300 documents, 500: 0 clusters / 0 documents, 5000: 0 clusters / 0 documents.
- **Figure 8 bottom — Wiki-40B:** dropped 11/11, low 9/11, high 9/11. Exact omitted edges — 10: 39 clusters / 390 documents, 20: 10 clusters / 200 documents, 50: 0 clusters / 0 documents, 500: 0 clusters / 0 documents, 5000: 0 clusters / 0 documents.
- **Figure 8 top — LM1B:** all 11 bars are printed-only; no archive or edge convention is inferred.

The [complete ledger](ledger.csv) contains 286 entries covering all 193 printed-oracle rows, expanded evaluation arms, removal rules and figure conventions, plus secondary and external context. Every entry links its source output and verdict. Non-executable entries carry explicit reasons.

## Verification and reproduction

Stage 7 verifies every accepted Stage 1–3 output against its immutable run manifest before writing outputs. The build is standard-library Python; the reader is dependency-free HTML/CSS/JavaScript/SVG with semantic chart tables and no runtime network requirement.

```bash
python -B src/verify_stage7.py
python -B src/stage7_build.py --out-dir results/stage7/run-002/audit
python -B src/verify_stage7.py --run-dir results/stage7/run-002/audit
```

To regenerate, replace `run-002` with an unused run name. Named runs are immutable. Raw clusters, source rows and the PDF remain local; only aggregates enter the reader. This package redistributes code and aggregate results only; raw inputs and the source PDF are not included.
