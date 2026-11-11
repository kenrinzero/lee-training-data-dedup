# Stage 1 — Wiki-40B released-cluster audit (run-004)

**Contract:** FROZEN v1. **Population:** released archive, all splits. C4 content was not opened. The historical seed's exposed values were regeneration targets, not blind predictions.

## Findings

- Train-with-train is **20,465 / 2,926,536 = 0.699290…%**, rounding to **0.70%** versus the printed **0.39%**: `MISMATCH`.
- Validation-with-validation and test-with-validation-arm EE both round to **0.26%** and match the printed cell at displayed precision.
- Validation-with-train is **0.70%** (`MISMATCH`); test-with-train is **0.72%** (`MATCH`). This retains both evaluation arms and **does not rename or relabel** the paper's printed `valid` column.
- All evaluated rule-derived retained sizes round to **2.91M**. The all-train rows are sensitivity analyses only; their rounded agreement is not evidence that the authors used that rule.
- Figure convention lock: **PRIMARY_LOCKED**; primary **dropped**; candidates **dropped**. Match counts: dropped 11/11, low 9/11, high 9/11.

## Input identity and reproducibility

- Cluster archive: `.\data\raw\clusters\wiki40b.tar.gz`; 26,773,963 bytes; SHA-256 `db1df97ef3268e0bdf36c15b66c4f71e4b465c42864f7c009104bb96bf8f8a32`.
- Archive member `wiki40b.csv`; 61,018,605 decompressed bytes; header `id,keep,cluster`.
- Public split revision: `06bfe584d8193cf58f79c6354ecc2a2b94a7deea`; 23 pinned Parquet shards; PyArrow 26.0.1.
- Run identity: Stage 1 / run-004; command `python -B src/stage1_audit.py --out-dir results/stage1/run-004/audit`.
- Raw inputs remain local. No raw cluster or dataset redistribution is authorized by this report.

## Row, schema, keep and join diagnostics

| Check | Result |
|---|---|
| Physical released rows | 3,252,407 |
| Unique released IDs | 3,252,407 |
| Unique clusters | 3,234,610 |
| Malformed / empty-field rows | 0 / 0 |
| Duplicate released IDs / extra rows | 0 / 0 |
| keep=0 multi / singleton | 23,519 / 0 |
| keep=1 multi / singleton | 0 / 3,228,888 |
| Keep-membership discrepancy rows | 0 |
| Join status | COMPLETE |
| Public unique keys | 3,252,407 |
| Duplicate public keys / rows | 0 / 0 |
| Cross-split public keys / released rows | 0 / 0 |
| Unmatched released / missing public rows | 0 / 0 |
| Population balance train / validation / test | 2,926,536 / 163,597 / 162,274 |

The join is exact-key, released-physical-row weighted. No normalization, trimming, deduplication, or arbitrary split assignment was applied.

## Table 2 — printed versus derived

| Printed target | Arm | Metric | Printed % | Numerator | Denominator | Rounded % | Verdict |
|---|---|---|---|---|---|---|---|
| train | validation | TT | 0.39 | 20465 | 2926536 | 0.70 | MISMATCH |
| validation | validation | EE | 0.26 | 432 | 163597 | 0.26 | MATCH |
| validation | validation | ET | 0.72 | 1138 | 163597 | 0.70 | MISMATCH |
| train | test | TT | 0.39 | 20465 | 2926536 | 0.70 | MISMATCH |
| validation | test | EE | 0.26 | 418 | 162274 | 0.26 | MATCH |
| validation | test | ET | 0.72 | 1163 | 162274 | 0.72 | MATCH |

Exact unrounded percentages and ratios are preserved in `derived-duplication.csv` and `table2-verdicts.csv`. TT is repeated for each evaluation arm because the frozen ledger grades the complete three-column target against both arms; its value is arm-invariant.

## Table 13 — original, retained sizes and removal intervals

| Arm | Rule | Original | Removals | Retained | Rounded M | NEARDUP verdict | Interval verdict |
|---|---|---|---|---|---|---|---|
| validation | A | 2.93 | 16304 | 2910232 | 2.91 | MATCH | CONSISTENT_INTERVAL |
| validation | B | 2.93 | 15461 | 2911075 | 2.91 | MATCH | CONSISTENT_INTERVAL |
| validation | S | 2.93 | 21148 | 2905388 | 2.91 | MATCH | CONSISTENT_INTERVAL |
| test | A | 2.93 | 16340 | 2910196 | 2.91 | MATCH | CONSISTENT_INTERVAL |
| test | B | 2.93 | 15461 | 2911075 | 2.91 | MATCH | CONSISTENT_INTERVAL |
| test | S | 2.93 | 21148 | 2905388 | 2.91 | MATCH | CONSISTENT_INTERVAL |
| validation+test | A | 2.93 | 16996 | 2909540 | 2.91 | MATCH | CONSISTENT_INTERVAL |
| validation+test | B | 2.93 | 15461 | 2911075 | 2.91 | MATCH | CONSISTENT_INTERVAL |
| validation+test | S | 2.93 | 21148 | 2905388 | 2.91 | MATCH | CONSISTENT_INTERVAL |

Rule A is evaluation-preferred keep-one; Rule B is uniform train keep-one; Rule S is the all-train sensitivity. The exact-original compatible removal interval is **(11,536, 21,536]**. Every printed original cell rounds to 2.93M and matches. Full columns, including printed values and interval endpoints, are in `table13-verdicts.csv`.

## Figure 8 bottom panel — all conventions

| Convention | Bin | Printed | Derived | Verdict |
|---|---|---|---|---|
| dropped | 1 | 3228888 | 3228888 | MATCH |
| dropped | 2 | 3557 | 3557 | MATCH |
| dropped | 3 | 833 | 833 | MATCH |
| dropped | 4 | 399 | 399 | MATCH |
| dropped | 5 | 245 | 245 | MATCH |
| dropped | [6, 10) | 391 | 391 | MATCH |
| dropped | [11, 20) | 163 | 163 | MATCH |
| dropped | [21, 50) | 60 | 60 | MATCH |
| dropped | [51, 500) | 24 | 24 | MATCH |
| dropped | [501, 5000) | 1 | 1 | MATCH |
| dropped | [5001, ∞) | 0 | 0 | MATCH |
| low | 1 | 3228888 | 3228888 | MATCH |
| low | 2 | 3557 | 3557 | MATCH |
| low | 3 | 833 | 833 | MATCH |
| low | 4 | 399 | 399 | MATCH |
| low | 5 | 245 | 245 | MATCH |
| low | [6, 10) | 391 | 430 | MISMATCH |
| low | [11, 20) | 163 | 173 | MISMATCH |
| low | [21, 50) | 60 | 60 | MATCH |
| low | [51, 500) | 24 | 24 | MATCH |
| low | [501, 5000) | 1 | 1 | MATCH |
| low | [5001, ∞) | 0 | 0 | MATCH |
| high | 1 | 3228888 | 3228888 | MATCH |
| high | 2 | 3557 | 3557 | MATCH |
| high | 3 | 833 | 833 | MATCH |
| high | 4 | 399 | 399 | MATCH |
| high | 5 | 245 | 245 | MATCH |
| high | [6, 10) | 391 | 391 | MATCH |
| high | [11, 20) | 163 | 202 | MISMATCH |
| high | [21, 50) | 60 | 70 | MISMATCH |
| high | [51, 500) | 24 | 24 | MATCH |
| high | [501, 5000) | 1 | 1 | MATCH |
| high | [5001, ∞) | 0 | 0 | MATCH |

### Exact edge sizes omitted by `dropped`

| Cluster size | Clusters | Documents |
|---|---|---|
| 10 | 39 | 390 |
| 20 | 10 | 200 |
| 50 | 0 | 0 |
| 500 | 0 | 0 |
| 5000 | 0 | 0 |

The locked candidate set was selected solely by Wiki-40B printed fidelity: **dropped**. C4 cannot break or shrink this lock. C4 content was not opened.

## Outputs and verification

- `input-manifest.json`: URLs, revisions, byte counts, SHA-256 receipts, parser and runtime identity.
- `cluster-composition.csv`, `cluster-histogram.csv`, `edge-sizes.csv`: exact cluster aggregates.
- `derived-duplication.csv`, `derived-removals.csv`, `figure-counts.csv`: complete derived values and sensitivities.
- `table2-verdicts.csv`, `table13-verdicts.csv`, `figure-verdicts.csv`: every printed comparison.
- Diagnostic CSVs preserve empty as well as nonempty discrepancy sets.
- `verify_stage1.py` checks hand-derived fixtures, all input hashes, every composition-derived metric, every figure convention, and UTF-8/LF outputs.
- `verify_stage1_report.py` checks that this report carries every verdict and the frozen lock.

The original run commands are recorded below. To reproduce them, replace `run-004` with an unused run name throughout; existing named runs are immutable:

```bash
python -B src/stage1_audit.py --out-dir results/stage1/run-004/audit
python -B src/stage1_compare.py --out-dir results/stage1/run-004/audit
python -B src/verify_stage1.py --run-dir results/stage1/run-004/audit
python -B src/stage1_report.py --out-dir results/stage1/run-004/audit
python -B src/verify_stage1_report.py --run-dir results/stage1/run-004/audit
```

The audit command refuses to overwrite an existing output directory; corrections require a new named run.
