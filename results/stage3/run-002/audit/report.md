# Stage 3 — RealNews released-cluster audit (run-002)

**Contract:** FROZEN v1. **Population:** released archive, all splits. The historical seed's exposed values were regeneration targets, not blind predictions.

## Input identity and row diagnostics

Cluster archive `data/raw/clusters/realnews.tar.gz`: 1,428,191,066 bytes; SHA-256 `27b14ae911e3bb2632f2a087e84f24c0f5163786d77ff92e1bbfa9d47473046c`. Streamed member `realnews.csv` (3,432,651,696 decompressed bytes) without extracting the full CSV. Header: `id,keep,cluster`.

| Check | Result |
|---|---|
| Physical released rows | 32,797,763 |
| Unique released IDs | 32,797,763 |
| Unique clusters | 30,014,995 |
| Malformed / empty-field rows | 0 / 0 |
| Duplicate released IDs / extra rows | 0 / 0 |
| Singleton documents | 27,917,044 |
| Multi-document clusters / documents | 2,097,951 / 4,880,719 |
| keep=0 multi / singleton | 4,880,719 / 0 |
| keep=1 multi / singleton | 0 / 27,917,044 |
| Keep-membership discrepancy rows | 0 |
| Keep-membership status | KEEP_MEMBERSHIP_AGREE |
| URL divergence rows | 0 |

IDs are compared as exact UTF-8 strings without host, scheme, path or URL normalization. Duplicate physical IDs remain in the estimand. Raw inputs and the disk-backed row store remain local.

## Split-free removal ceiling

Multi-document rows **4,880,719** minus multi-document clusters **2,097,951** give **U = 2,782,768**. The frozen keep-one formula is `U=D_multi-C_multi=sum_{c:n_all(c)>=2}(n_all(c)-1)`.

The independently rounded printed difference implies removals in **(2,760,000, 2,780,000)**. Because the smallest compatible integer is 2,760,001, the verdict for this U is **CEILING_COMPATIBLE**. `CEILING_COMPATIBLE` is only a ceiling result, not a train-size match.

## Table 2 — split-dependent cells

| Metric | Printed % | Derived | Verdict |
|---|---|---|---|
| TT | 13.63 |  | NOT_EXECUTABLE_INPUT |
| EE | 1.25 |  | NOT_EXECUTABLE_INPUT |
| ET | 14.35 |  | NOT_EXECUTABLE_INPUT |

All three cells are `NOT_EXECUTABLE_INPUT`: no exact public original size or RealNews split mapping is pinned. No train/validation/test assignments are inferred from the released archive.

## Table 13 — conditional release-population comparison

Basis: **CONDITIONAL_RELEASE_POPULATION** — measured released archive rows, not a verified exact public original train size. This is not a verified public train population and not a verified public train-size reproduction.

| Basis | Original M | Original verdict | Removals | Retained | Retained M | NEARDUP verdict | Direct train removal |
|---|---|---|---|---|---|---|---|
| CONDITIONAL_RELEASE_POPULATION | 32.80 | MISMATCH | 2782768 | 30014995 | 30.01 | MISMATCH | NOT_EXECUTABLE_INPUT |

### Companion dispositions

- §5.3 printed rounding: **14.35% → 14.4%**, **MATCH** as printed ROUND_HALF_UP consistency, not reproduction of the unavailable split cell.
- Table 13 ORIGINAL and NEARDUP token cells: **NOT_EXECUTABLE_INPUT** and **NOT_EXECUTABLE_INPUT**; cluster IDs and assignments cannot reproduce the paper's 50k BPE token counts.

## Table 11 — exact released-ID audit

Faithful `Frac Dups` is physical `keep=0 / # Total`; multi-document membership is sensitivity only. Direct lookups include every released ID, including IDs occurring only with `keep=1`. Exact-ID mismatches do not by themselves reconstruct or contradict a source-native host-level aggregation; no normalization was introduced.

| Row | Printed URL | Printed total | Derived total | Total verdict | Printed frac | Derived frac | Frac verdict |
|---|---|---|---|---|---|---|---|
| 1 | medicalnewstoday.com. | 12 | 0 | MISMATCH | 1.00 |  | NOT_EXECUTABLE_INPUT |
| 2 | dodbuzz.com | 301 | 0 | MISMATCH | 0.99 |  | NOT_EXECUTABLE_INPUT |
| 3 | undertheradar.military.com | 187 | 0 | MISMATCH | 0.97 |  | NOT_EXECUTABLE_INPUT |
| 4 | q.usatoday.com | 33 | 0 | MISMATCH | 0.94 |  | NOT_EXECUTABLE_INPUT |
| 5 | ad-test.thirdage.com | 354 | 0 | MISMATCH | 0.94 |  | NOT_EXECUTABLE_INPUT |
| 6 | amp.nymag.com | 15 | 0 | MISMATCH | 0.93 |  | NOT_EXECUTABLE_INPUT |
| 7 | citizenwire.com | 1022 | 0 | MISMATCH | 0.93 |  | NOT_EXECUTABLE_INPUT |
| 8 | paycheck-chronicles.military.com | 363 | 0 | MISMATCH | 0.92 |  | NOT_EXECUTABLE_INPUT |
| 9 | product-reviews.net | 73403 | 0 | MISMATCH | 0.92 |  | NOT_EXECUTABLE_INPUT |
| 10 | kitup.military.com | 196 | 0 | MISMATCH | 0.92 |  | NOT_EXECUTABLE_INPUT |
| 11 | gcaptain.com | 33903 | 0 | MISMATCH | 0.92 |  | NOT_EXECUTABLE_INPUT |
| 12 | dev.screenrant.com | 70 | 0 | MISMATCH | 0.91 |  | NOT_EXECUTABLE_INPUT |
| 13 | live.swissinfo.ch | 66 | 0 | MISMATCH | 0.91 |  | NOT_EXECUTABLE_INPUT |
| 14 | news.theepochtimes.com | 82 | 0 | MISMATCH | 0.87 |  | NOT_EXECUTABLE_INPUT |
| 15 | opinion.toledoblade.com | 986 | 0 | MISMATCH | 0.87 |  | NOT_EXECUTABLE_INPUT |
| 16 | cdn.moneytalksnews.com | 121 | 0 | MISMATCH | 0.86 |  | NOT_EXECUTABLE_INPUT |
| 17 | amp.fox23.com | 14 | 0 | MISMATCH | 0.86 |  | NOT_EXECUTABLE_INPUT |
| 18 | sales.rollingstone.com | 20 | 0 | MISMATCH | 0.85 |  | NOT_EXECUTABLE_INPUT |
| 19 | ftp.screenrant.com | 20 | 0 | MISMATCH | 0.85 |  | NOT_EXECUTABLE_INPUT |

### Derived ranking — first five of up to 20

The separate derived ranking includes every ID with `total >= 10`, then sorts by faithful unrounded fraction descending, total descending and URL bytewise ascending. It does not apply C4's all-duplicate-only filter.

| Rank | URL | Total | keep0 | Frac Dups | Membership fraction |
|---|---|---|---|---|---|

## Figure 8(b) — all predeclared conventions

Match counts: dropped 11/11, low 8/11, high 8/11. The Stage 1 primary remains `dropped`; RealNews agreement does not select a new convention.

| Convention | Bin | Printed | Derived | Verdict |
|---|---|---|---|---|
| dropped | 1 | 27917044 | 27917044 | MATCH |
| dropped | 2 | 1715379 | 1715379 | MATCH |
| dropped | 3 | 231913 | 231913 | MATCH |
| dropped | 4 | 89017 | 89017 | MATCH |
| dropped | 5 | 34487 | 34487 | MATCH |
| dropped | [6, 10) | 24889 | 24889 | MATCH |
| dropped | [11, 20) | 1150 | 1150 | MATCH |
| dropped | [21, 50) | 243 | 243 | MATCH |
| dropped | [51, 500) | 129 | 129 | MATCH |
| dropped | [501, 5000) | 11 | 11 | MATCH |
| dropped | [5001, ∞) | 0 | 0 | MATCH |
| low | 1 | 27917044 | 27917044 | MATCH |
| low | 2 | 1715379 | 1715379 | MATCH |
| low | 3 | 231913 | 231913 | MATCH |
| low | 4 | 89017 | 89017 | MATCH |
| low | 5 | 34487 | 34487 | MATCH |
| low | [6, 10) | 24889 | 25592 | MISMATCH |
| low | [11, 20) | 1150 | 1174 | MISMATCH |
| low | [21, 50) | 243 | 249 | MISMATCH |
| low | [51, 500) | 129 | 129 | MATCH |
| low | [501, 5000) | 11 | 11 | MATCH |
| low | [5001, ∞) | 0 | 0 | MATCH |
| high | 1 | 27917044 | 27917044 | MATCH |
| high | 2 | 1715379 | 1715379 | MATCH |
| high | 3 | 231913 | 231913 | MATCH |
| high | 4 | 89017 | 89017 | MATCH |
| high | 5 | 34487 | 34487 | MATCH |
| high | [6, 10) | 24889 | 24889 | MATCH |
| high | [11, 20) | 1150 | 1853 | MISMATCH |
| high | [21, 50) | 243 | 267 | MISMATCH |
| high | [51, 500) | 129 | 135 | MISMATCH |
| high | [501, 5000) | 11 | 11 | MATCH |
| high | [5001, ∞) | 0 | 0 | MATCH |

### Exact omitted edge sizes

| Cluster size | Clusters | Documents |
|---|---|---|
| 10 | 703 | 7030 |
| 20 | 24 | 480 |
| 50 | 6 | 300 |
| 500 | 0 | 0 |
| 5000 | 0 | 0 |

## Verification and reproduction

- Audit runtime: 240.421 seconds; local work-store bytes at receipt: 3,942,658,048.
- `verify_stage3.py`: hand-derived fixtures, archive identity, histogram, cluster/URL diagnostics, figures, ceiling, ranking, conditional arithmetic and comparison checks.
- `verify_stage3_report.py`: read-only reader-claim, output-hash and code-receipt checks.
- Method provenance: shared receipt, rounding, figure and table helpers are imported from Stages 1–2; the RealNews streaming audit and comparisons are new for Stage 3.
- Reports and aggregate outputs contain no full document text. Publication remains a separate rights and user decision.

The original commands are recorded below. To reproduce, replace `run-002` with an unused run name throughout; existing named runs are immutable:

```bash
.venv/Scripts/python -B src/verify_stage3.py
.venv/Scripts/python -B src/stage3_audit.py --out-dir results/stage3/run-002/audit
.venv/Scripts/python -B src/verify_stage3.py --full --run-dir results/stage3/run-002/audit
.venv/Scripts/python -B src/stage3_compare.py --out-dir results/stage3/run-002/audit
.venv/Scripts/python -B src/stage3_report.py --out-dir results/stage3/run-002/audit
.venv/Scripts/python -B src/verify_stage3.py --full --run-dir results/stage3/run-002/audit
.venv/Scripts/python -B src/verify_stage3_report.py --run-dir results/stage3/run-002/audit
```
