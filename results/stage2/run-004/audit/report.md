# Stage 2 — C4 released-cluster audit (run-004)

**Contract:** FROZEN v1. **Population:** released archive, all splits. Stage 1 locked `dropped` as the sole primary before any C4 content was opened.

## Release identity

**IDENTITY_HOLD**. Physical rows **365,233,500** versus required **365,233,500**. Figure matches: dropped 11/11, low 7/11, high 7/11.

Cluster archive `data/raw/clusters/c4.tar.gz`: 13,872,073,006 bytes; SHA-256 `5b73b507b3aa08c7dca5d5da55afe27babe6a4ddde40f4107ad1e88e82986723`. Streamed member `c4.csv` (30,219,354,495 decompressed bytes) without extracting the full CSV.

The historical seed's exposed values were regeneration targets, not blind predictions. The kill test precedes every faithful printed-cell verdict.

## Split provenance and join diagnostics

Split source: `1,024 original allenai/c4 train JSON shards streamed under Amendment A1 plus full validation Parquet`, root revision `1588ec454efa1a09f29cd18ddd04fe05fc8653a2`. The 1024 train shards total 326,778,635,540 compressed bytes and were streamed once per acquisition attempt under Amendment A1; exact URLs and per-shard SHA-256 receipts are retained without compressed document bodies. Validation uses two full Parquet files totaling 509,275,778 bytes. The 2,207,027-row partial Parquet train was excluded. The preserved public URL store was hash-checked before processing.

| Check | Result |
|---|---|
| Join status | COMPLETE |
| Public train / validation rows | 364,868,892 / 364,608 |
| Population balance train / validation | 364,868,892 / 364,608 |
| Public unique keys | 365,233,500 |
| Duplicate public keys / rows | 0 / 0 |
| Duplicate released URLs / extra rows | 0 / 0 |
| Cross-split public keys / released rows | 0 / 0 |
| Unmatched released / missing public rows | 0 / 0 |
| Keep-membership status | KEEP_MEMBERSHIP_AGREE |
| URL divergence rows | 0 |

Joins compare exact UTF-8 URL strings without normalization. Repeated public keys map through one URL mask, so they never multiply released rows. Cross-split and unmatched keys are not arbitrarily assigned. The estimand is released-physical-row weighted.

## Table 2 — direct observed cluster membership

| Metric | Printed % | Numerator | Denominator | Rounded % | Verdict |
|---|---|---|---|---|---|
| TT | 3.04 | 16892539 | 364868892 | 4.63 | MISMATCH |
| EE | 1.59 | 5754 | 364608 | 1.58 | MISMATCH |
| ET | 4.60 | 16756 | 364608 | 4.60 | MATCH |

TT means train-with-train; EE means validation-with-validation; ET means validation-with-train. Exact unrounded values are in `table2-verdicts.csv`.

### Secondary random-split EE check

Expected numerator **5859223.55260572805972103758998352383330684415405889919380667**; unrounded percent **1.60424045236971089993689998041897137948924295116929284794704**; rounded **1.60%** versus printed **1.59%**: **MISMATCH**. This assumes a uniform fixed-size validation split and is separate from the direct observed EE cell. The expectation was serialized before the comparison routine read the printed 1.59%.

## Table 13 — original, removals and retained train size

| Rule | Original M | Removals | Retained | Retained M | NEARDUP | Interval |
|---|---|---|---|---|---|---|
| A | 364.87 | 14393547 | 350475345 | 350.48 | MATCH | CONSISTENT_INTERVAL |
| B | 364.87 | 14381052 | 350487840 | 350.49 | MISMATCH | CONTRADICTION |
| S | 364.87 | 16896263 | 347972629 | 347.97 | MISMATCH | CONTRADICTION |

Rule A is evaluation-preferred keep-one; Rule B is uniform train keep-one; Rule S is the all-train sensitivity. Rules A and B are alternative interpretations, not observed author deletions; rounded agreement does not identify the authors' rule. The exact-original removal interval is **(14,383,892, 14,393,892]**.

### Companion dispositions required by the coverage ledger

- §5.3 printed rounding: **4.60% → 4.6%**, **MATCH** as printed rounding consistency, not a separate split result.
- Independently rounded printed-difference interval **(14,380,000, 14,400,000)**: A **CONSISTENT_INTERVAL**, B **CONSISTENT_INTERVAL**, S **CONTRADICTION**. This is distinct from the exact-original interval above.
- Table 13 ORIGINAL and NEARDUP token cells: **NOT_EXECUTABLE_INPUT** and **NOT_EXECUTABLE_INPUT**; cluster IDs and assignments cannot reproduce the paper's 50k BPE token counts.
- Step-0 removal-ceiling companion: **CONTRADICTION**, robust minimum shortfall **2905134.2386**, preserved in `planning/step0/arithmetic.json` under `c4_removal_ceiling`.
- Step-0 Figure 1 companion: **CONSISTENT_INTERVAL**, conditional train-removal interval **[8,001,466, 14,410,977]**, preserved under `fig1_bounds`.

## §5.1 cluster facts

| Claim | Printed | Derived | Verdict |
|---|---|---|---|
| approximately 1.8M pair clusters | 1.8 | 1861744 | MISMATCH |
| majority are pair clusters | majority | True | MATCH |
| clusters over 5000 | 280 | 280 | MATCH |
| largest cluster size | 250933 | 250933 | MATCH |

Size 5,000 is reported separately from the prose's 'over 5,000'. Figure bars count clusters, not documents.

## Table 11 — printed URL rows

Faithful `Frac Dups` is physical `keep=0 / # Total`; the multi-document-cluster fraction is diagnostic only. The twentieth printed URL is absent and remains `SOURCE_MISSING`; a derived ranking candidate is not a recovered printed value.

These zero exact-ID counts test only exact full-URL identity. They do **not** reproduce the source-native host-level estimand or establish 19 substantive numerical contradictions in the paper's host-like aggregation. Host extraction, scheme/path removal or other normalization would require a dated amendment with prior-exposure disclosure and a new run; none was introduced.

| Row | Printed URL | Printed total | Derived total | Total verdict | Printed frac | Derived frac | Frac verdict |
|---|---|---|---|---|---|---|---|
| 1 | hairtechkearney.com | 4883 | 0 | MISMATCH | 1 |  | NOT_EXECUTABLE_INPUT |
| 2 | keywordsking.com | 1786 | 0 | MISMATCH | 1 |  | NOT_EXECUTABLE_INPUT |
| 3 | sydneysitalianfruitshops.online | 1178 | 0 | MISMATCH | 1 |  | NOT_EXECUTABLE_INPUT |
| 4 | moewiki.usamimi.info | 1001 | 0 | MISMATCH | 1 |  | NOT_EXECUTABLE_INPUT |
| 5 | swarovskijewelryoutlet.org | 984 | 0 | MISMATCH | 1 |  | NOT_EXECUTABLE_INPUT |
| 6 | forzadurto.org | 980 | 0 | MISMATCH | 1 |  | NOT_EXECUTABLE_INPUT |
| 7 | producerati.com | 971 | 0 | MISMATCH | 1 |  | NOT_EXECUTABLE_INPUT |
| 8 | sourceryforge.org | 908 | 0 | MISMATCH | 1 |  | NOT_EXECUTABLE_INPUT |
| 9 | heavenz-kitchen.com | 876 | 0 | MISMATCH | 1 |  | NOT_EXECUTABLE_INPUT |
| 10 | little-eclipse.com | 822 | 0 | MISMATCH | 1 |  | NOT_EXECUTABLE_INPUT |
| 11 | walops.com | 819 | 0 | MISMATCH | 1 |  | NOT_EXECUTABLE_INPUT |
| 12 | 16thstlaunderland.com | 713 | 0 | MISMATCH | 1 |  | NOT_EXECUTABLE_INPUT |
| 13 | theroyalstarinfo.com | 696 | 0 | MISMATCH | 1 |  | NOT_EXECUTABLE_INPUT |
| 14 | code4kt.com | 684 | 0 | MISMATCH | 1 |  | NOT_EXECUTABLE_INPUT |
| 15 | nflfalconsjerseys.us | 682 | 0 | MISMATCH | 1 |  | NOT_EXECUTABLE_INPUT |
| 16 | quiltingbeeshop.com | 676 | 0 | MISMATCH | 1 |  | NOT_EXECUTABLE_INPUT |
| 17 | ulifeinsurancemiami.com | 675 | 0 | MISMATCH | 1 |  | NOT_EXECUTABLE_INPUT |
| 18 | wowkeyword.com | 673 | 0 | MISMATCH | 1 |  | NOT_EXECUTABLE_INPUT |
| 19 | taspetro.com | 671 | 0 | MISMATCH | 1 |  | NOT_EXECUTABLE_INPUT |
| 20 | SOURCE_MISSING | UNRESOLVED |  | SOURCE_MISSING | UNRESOLVED |  | SOURCE_MISSING |

### Derived full-URL diagnostic — first five of 20

Candidates were first restricted to URLs whose unrounded `keep=0` share equals 1, then sorted by total descending and URL bytewise ascending. Because every released full URL is unique, every eligible total is 1. This is a full-URL diagnostic, **not** a reconstruction of the printed host-like frequency ranking. The remaining 15 rows are preserved in `table11-top20.csv`.

| Rank | URL | Total | keep0 | Membership fraction |
|---|---|---|---|---|
| 1 | http://%e2%80%8bwiping-rags-absorbents-spill-kits.americantex.com/item/cylinder-products/universal-cylinder-bracket/7216-ye | 1 | 1 | 1 |
| 2 | http://%e2%80%8bwiping-rags-absorbents-spill-kits.americantex.com/viewitems/accessories-3/ground-pads | 1 | 1 | 1 |
| 3 | http://%e2%80%8bwiping-rags-absorbents-spill-kits.americantex.com/viewitems/berms-1/stinger-snap-foam-berms | 1 | 1 | 1 |
| 4 | http://--.kr/ | 1 | 1 | 1 |
| 5 | http://-./11294-product-121.php | 1 | 1 | 1 |

## Figure 1 — all predeclared conventions

| Convention | Bin | Printed | Derived | Verdict |
|---|---|---|---|---|
| dropped | 1 | 348320475 | 348320475 | MATCH |
| dropped | 2 | 1861744 | 1861744 | MATCH |
| dropped | 3 | 292575 | 292575 | MATCH |
| dropped | 4 | 109853 | 109853 | MATCH |
| dropped | 5 | 54984 | 54984 | MATCH |
| dropped | [6, 10) | 85567 | 85567 | MATCH |
| dropped | [11, 20) | 42723 | 42723 | MATCH |
| dropped | [21, 50) | 28446 | 28446 | MATCH |
| dropped | [51, 500) | 23094 | 23094 | MATCH |
| dropped | [501, 5000) | 2782 | 2782 | MATCH |
| dropped | [5001, ∞) | 280 | 280 | MATCH |
| low | 1 | 348320475 | 348320475 | MATCH |
| low | 2 | 1861744 | 1861744 | MATCH |
| low | 3 | 292575 | 292575 | MATCH |
| low | 4 | 109853 | 109853 | MATCH |
| low | 5 | 54984 | 54984 | MATCH |
| low | [6, 10) | 85567 | 95541 | MISMATCH |
| low | [11, 20) | 42723 | 45123 | MISMATCH |
| low | [21, 50) | 28446 | 29234 | MISMATCH |
| low | [51, 500) | 23094 | 23098 | MISMATCH |
| low | [501, 5000) | 2782 | 2782 | MATCH |
| low | [5001, ∞) | 280 | 280 | MATCH |
| high | 1 | 348320475 | 348320475 | MATCH |
| high | 2 | 1861744 | 1861744 | MATCH |
| high | 3 | 292575 | 292575 | MATCH |
| high | 4 | 109853 | 109853 | MATCH |
| high | 5 | 54984 | 54984 | MATCH |
| high | [6, 10) | 85567 | 85567 | MATCH |
| high | [11, 20) | 42723 | 52697 | MISMATCH |
| high | [21, 50) | 28446 | 30846 | MISMATCH |
| high | [51, 500) | 23094 | 23882 | MISMATCH |
| high | [501, 5000) | 2782 | 2786 | MISMATCH |
| high | [5001, ∞) | 280 | 280 | MATCH |

The faithful convention-dependent output uses `dropped`; `low` and `high` remain sensitivities and cannot displace the Stage 1 lock.

## Verification and reproduction

- `verify_stage2.py`: hand-derived identity, random-split and ranking fixtures; source hashes; histogram-derived identity; full split receipts; direct metrics, removals, cluster facts, random expectation and Table 11 ranking.
- `verify_stage2_report.py`: read-only reader-claim, output-hash and code-receipt checks.
- Method provenance: shared `figure_counts`, receipt and output helpers are imported from Stage 1; the streamed DuckDB audit and comparisons are new for Stage 2.
- Raw inputs and the disk-backed row store remain local. Reports and aggregate CSV/JSON outputs contain no full document text.

The original commands are recorded below. To reproduce, replace `run-004` with an unused run name throughout; existing named runs are immutable:

```bash
python -B src/stage2_identity.py --out-dir results/stage2/run-004/audit
python -B src/verify_stage2.py --run-dir results/stage2/run-004/audit
.venv/Scripts/python -B src/stage2_acquire.py --out-dir results/stage2/run-004
.venv/Scripts/python -B src/stage2_audit.py --out-dir results/stage2/run-004/audit
.venv/Scripts/python -B src/stage2_compare.py --out-dir results/stage2/run-004/audit
python -B src/stage2_finalize.py --out-dir results/stage2/run-004/audit
.venv/Scripts/python -B src/verify_stage2.py --full --run-dir results/stage2/run-004/audit
python -B src/stage2_report.py --out-dir results/stage2/run-004/audit
python -B src/verify_stage2_report.py --run-dir results/stage2/run-004/audit
```
