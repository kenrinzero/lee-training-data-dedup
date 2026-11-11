# Claim inventory — FROZEN v1

**Frozen date:** 2026-11-08  
**Status:** Step 0 is complete and v1 is frozen after independent review
(Spec PASS / Quality APPROVED / Ready to freeze YES; agent-5 fresh context).
Future changes require dated appended amendments only.

This inventory maps the authorized Stages 1–3 and 7 to the preserved ACL PDF.
PDF page numbers equal printed page numbers. Exact scalar values, units and
precision are in `paper/targets/printed-targets.csv`; all 44 figure scalars are
also in `paper/targets/figure-bars.csv`. Those approved Task 1 artifacts are the
printed oracle. Task 2's arithmetic and the new public metadata pins are separate
from PDF transcription.

## 1. Source-native claim map

| ID | Final source-native locator and printed target | Planned released-cluster or arithmetic check | Computability / tier |
|---|---|---|---|
| C1 | **PDF p. 5, Table 2, C4 row:** TT **3.04%**, valid-valid **1.59%**, valid-train **4.60%**; **p. 5 §5.1** repeats 3.04%; **p. 6 §5.3** prints 4.6% | Join all released C4 rows to pinned train/validation splits; count TT/EE/ET by cluster membership; compute exact finite-population EE expectation from the full cluster histogram before comparing with 1.59% | Direct recount is executable only after complete unambiguous split join and release-identity gate; random-split expectation additionally assumes a uniform fixed-size split / T3 |
| C2 | **PDF p. 21, Table 13, C4 row:** ORIGINAL/NEARDUP **364.87M/350.48M examples**, **177.3B/173.7B tokens**; **p. 15 Appendices C/D** approximate sizes, steps, hours and **3.9%**; **p. 16 Table 6** training-time anchors | Compare exact public original size and rule-derived retained sizes at printed precision under Rules A/B; report all-train sensitivity and both exact-original and printed-difference removal intervals; preserve Task 2 supporting arithmetic | Example counts executable after Stage-2 gate; token counts are not recoverable from cluster CSVs; model timing is printed-only consistency context, not a cluster reproduction / T3 |
| C3 | **PDF p. 5, Figure 1 and §5.1:** 11 group-count bars; approximately **1.8M** size-2 clusters, **280** clusters over 5,000, largest **250,933**; **p. 21 Table 11 C4 column:** 19 printed URL rows | Stream all C4 rows; compute three edge conventions and dropped edges; exact size-2/over-5000/largest counts; physical URL totals and faithful `keep=0 / # Total` fractions; derive the top 20 only from URLs whose unrounded `keep=0` share equals 1 | Executable after release identity, except the absent twentieth printed row remains `SOURCE_MISSING`; no duplicate-URL exemption / T3 |
| C4 | **PDF p. 5, Table 2, Wiki40B row:** **0.39% / 0.26% / 0.72%**; **p. 21 Table 13 Wiki40B row:** ORIGINAL/NEARDUP **2.93M/2.91M examples**, **2.25B/2.24B tokens**; **p. 22 Figure 8 bottom panel:** 11 bars | Join `wikidata_id`; report validation and test separately for EE/ET and removal arms; test `keep` lead; evaluate all edge conventions and both removal rules over all released rows | Executable with pinned Wiki-40B `en` metadata and complete join; do not relabel printed `valid` before results; token/EXACTSUBSTR cells are outside cluster-only computability / T3 |
| C5 | **PDF p. 5, Table 2, RealNews row:** **13.63% / 1.25% / 14.35%**; **p. 21 Table 13 Real News row:** ORIGINAL/NEARDUP **31.16M/28.39M examples**, **24.7B/22.4B tokens**; **p. 21 Table 11 RealNews column:** 19 rows; **p. 22 Figure 8 middle panel:** 11 bars; **p. 6 §5.3:** 14.4% | Recompute all-row figure, total rows, URL cells and split-free keep-one ceiling; compare Table 13 only at the population level supported by measured release rows; check separately that printed 14.35% rounds half up to 14.4% | **All three Table 2 split cells and direct train removals are not executable** without pinned RealNews split metadata and exact public original size. The 14.4% check is printed-rounding consistency, not reproduction of the unavailable split cell / T3 |
| C6 | **PDF p. 1 §1:** 61,036/61 and 0.02%; **p. 5 Table 2 LM1B row:** **4.86% / 0.07% / 4.92%**; **p. 21 Table 13:** LM1B **30.30M/29.87M**, C4 EXACTSUBSTR **350.48M**; **p. 22 Figure 8 top panel:** 11 LM1B bars; **pp. 15–18 Appendices C–E** method/size context | Preserve Task 2's printed-plus-public-metadata derivations: C4 ceiling, Figure 1 corrected bounds, random-split identities, LM1B floor, repeated percentages, NEARDUP anchors and EXACTSUBSTR consistency | Printed arithmetic executable now with stated assumptions. **All LM1B Table 2 cells and LM1B cluster recounts are not executable**: `lm1b.tar.gz` HEAD is 404 and no alternative cluster source is pinned. EXACTSUBSTR reproduction remains deferred / T3 |
| C7 | **PDF p. 5 Figure 1; p. 22 Figure 8** (three unlettered panels, top-to-bottom LM1B/Real News/Wiki40B); C4 alternative-percentage sources under C1/C2/C6 | Regenerate figures and printed/direct/rule-derived/printed-only ledger from immutable stage outputs; annotate dropped edges and non-executable cells | Numerical/visual reproduction after Stages 1–3; no visual smoothing or convention substitution / T3 |

`T3` denotes deterministic execution and numerical checks. Interpretation and
reader adequacy still require independent Type-B review.

## 2. Cell-level computability and verdict coverage

### 2.1 Table 2

- **C4:** three direct cells are included. TT requires train membership; EE and
  ET require validation membership. Duplicate URLs occurring across splits make
  affected split cells `INDETERMINATE_JOIN`, not silently unique-key estimates.
  The 1.59% random-split expectation is a secondary model-based comparison and
  requires the full `n_s` histogram; printed Figure 1 aggregates are insufficient.
- **Wiki-40B:** the three printed columns are graded against validation and test
  as separate arms. Validation-only, test-only and spanning clusters follow the
  contract formulas. A test match does not rewrite the PDF's `valid` label.
- **RealNews:** 13.63%, 1.25% and 14.35% remain printed targets but are
  `NOT_EXECUTABLE_INPUT` from the released cluster file alone.
- **LM1B:** 4.86%, 0.07% and 4.92% remain printed targets but are
  `NOT_EXECUTABLE_INPUT`; no LM1B cluster archive is pinned. Public `test` is not
  renamed validation.

Every Table 2 numerator and denominator is based on cluster membership. For each
split `S`, `sum_c n_S(c)=N_S` is required in addition to unmatched/missing/cross-
split checks; otherwise the cell is `INDETERMINATE_JOIN`. If unequal same-split
key multiplicities are accepted because totals balance, the estimand is explicitly
released-physical-row weighted. `keep` is first tested as an exposed Wiki lead
and is never the sole basis of a primary **Table 2** duplication cell. Table 11's
separate source-native `keep=0` estimand is specified below.

### 2.2 Table 13 and supporting printed cells

C4, Wiki-40B and LM1B have exact public original train sizes pinned in Step 0.
ORIGINAL and NEARDUP example cells use ROUND_HALF_UP at two decimals in million
examples. Rule-derived removal intervals use exact original size and the printed
NEARDUP interval. Task 2's difference between independently rounded printed
cells remains a separate internal-consistency calculation.

RealNews has no pinned exact public original size. Its released physical row
count may be used as a clearly conditional release-population candidate, not as
an independently verified public train count. Its independently rounded ORIGINAL
31.16M and NEARDUP 28.39M imply printed-difference removals in
**(2,760,000,2,780,000)**; the smallest compatible integer is **2,760,001**. For
split-free ceiling `U`, `U <= 2,760,000` is `CONTRADICTION` under keep-one
semantics and `U >= 2,760,001` is only `CEILING_COMPATIBLE`, never a train-size
reproduction. Separately, **14.35% rounds half up to §5.3's 14.4%**; that printed-
rounding consistency check does not reproduce the unavailable 14.35% split cell.

Token cells cannot be recomputed from document IDs and cluster assignments.
Appendix C/D and Table 6 timing/size cells support printed arithmetic only.
C4 EXACTSUBSTR's repeated 350.48M is checked for internal consistency, not
reproduced by a deferred EXACTSUBSTR run. RealNews/Wiki/LM1B EXACTSUBSTR cells
remain visible in the oracle but are not executable targets in this scope.

### 2.3 Figures and §5.1 cluster statements

All 11 bars in each included panel are individual exact-count targets. Figures
use all released rows and name the split population. Exact edge sizes 10, 20,
50, 500 and 5000 are assigned low, high or dropped under all three predeclared
conventions. A unique 11/11 Wiki match locks a primary. Zero matches lock all
three candidates and multiple matches lock the matching subset; neither ambiguous
branch has a primary, and C4 cannot break the tie. Convention-dependent C4
outputs then remain sensitivity/`AMBIGUOUS_CONVENTION` (or stop), while non-
convention outputs may proceed if release identity otherwise holds. C4 release
identity requires physical rows 365,233,500 and at least one convention matching
all 11 C4 bars.

The §5.1 1.8M statement is explicitly approximate: grade by ROUND_HALF_UP to
0.1M and separately test "majority". The 280 count and 250,933 largest size are
exact. The prose "over 5,000" excludes size 5,000; report that size separately.

### 2.4 Table 11

The caption's examples "marked as near-duplicates by NEARDUP" define the faithful
estimand. For each of the 19 printed C4 and 19 printed RealNews rows, `# Total`
is the exact physical-row count and faithful `Frac Dups` is **physical `keep=0`
rows divided by physical `# Total`**, rounded half up at displayed precision.
Duplicate URLs stay in both numerator and denominator. Multi-document-cluster
fractions are diagnostic/sensitivity only. On disagreement, emit
`KEEP_MEMBERSHIP_DIVERGENCE`, preserve both tables and grade the printed cell only
against `keep=0`; never substitute membership to manufacture a `MISMATCH`.

The C4 derived top-20 candidate set first filters URLs to those whose **unrounded
`keep=0` share equals 1**, then ranks by `# Total` descending and URL bytewise
ascending. Directly transcribed rows remain unchanged. The C4 caption promises
20 URLs but only 19 rows are printed. The missing URL, total and fraction are
`SOURCE_MISSING`; structured sentinels already exist for the latter two. A
recomputed released-ranking twentieth candidate is labelled new derived evidence,
not a recovered printed value. RealNews ranking/filter conventions are fixed in
the preregistration.

## 3. Step-0 internal-consistency findings included in scope

These are approved printed-plus-public-metadata findings, not cluster results:

| Finding | Current Step-0 verdict | Future cluster relationship |
|---|---|---|
| C4 Table 2 removal ceiling 11,456,622.3168 nominal; robust strict upper 11,474,865.7614; robust gap 2,905,134.2386 | `CONTRADICTION`, conditional on common population and evaluation-preferred keep-one | Stage 2 tests actual cells and release/convention explanations independently |
| Figure 1 whole-population keep-one lower count 8,366,074; corrected train floor **8,001,466**, upper **14,410,977** | `CONSISTENT_INTERVAL` with Table 13 under full train+validation coverage | Stage 2 obtains exact counts; Step-0 bounds do not choose an edge convention |
| C4 random-split EE from printed aggregates | Indeterminate without full histogram | Stage 2 computes exact expectation before comparing to 1.59% |
| LM1B conditional train-removal floor **510,877**, exceeding largest printed-difference-compatible 440,000 by 70,877 | `CONTRADICTION`, conditional on full-population figure coverage and public-test evaluation mapping | No future released-cluster test is currently executable |
| 61,036/61 repeated-sentence percentages | Both round to 0.02%; consistent | No deferred substring recount is authorized |
| C4 NEARDUP Table 13/appendix anchors | Consistent at printed precision | Does not erase the separate Table 2 ceiling contradiction |
| C4 EXACTSUBSTR 350.48M versus appendix/method context | Contradiction; copy error not established | No standalone EXACTSUBSTR reproduction in this scope |

## 4. External context, not a PDF substitute

The Google Research publication abstract at
https://research.google/pubs/deduplicating-training-data-makes-language-models-better/
(accessed 2026-11-08) states **1.68%** of C4 is near-duplicates. Stage 7 carries
it as an external publication-page statement with its own basis unresolved; it
does not replace 3.04%, 4.60%, Table 13 or Figure 1.

## 5. Interpretation and checklist lenses

A successful count reproduction supports only the named cell under the frozen
population and rule. A mismatch is a numerical, source, release or convention
incompatibility, never evidence of intent. No included check validates unseen
model training, memorization, perplexity or model-quality claims.

The container investigation checklist was applied as a screening lens:

- **Aggregation/basis mismatch:** distinguish groups from documents, TT/EE/ET,
  removals, percentages and ratios, exact public splits from rounded table sizes.
- **Caption/table mismatch:** retain Table 11's 19-versus-20 discrepancy and
  Figure 8's unlettered three-panel structure.
- **Configuration mismatch:** pin revisions, split joins, edge conventions and
  evaluation arms; treat Wiki `valid` as unresolved until results.
- **Delta arithmetic:** preserve both exact-original and printed-difference
  intervals and the corrected Figure 1 train floor.
- **Scope overclaim / pilot-as-comprehensive:** label all seed values exposed and
  all Step-0 findings conditional; do not turn printed arithmetic into a cluster
  reproduction.
- **Phantom or missing inputs:** mark RealNews splits, LM1B clusters, token
  counts and Table 11's twentieth row explicitly non-executable or missing.

These are lenses, not additional verdicts. Every final claim still needs its
source, deterministic derivation and independent review chain.

## Amendments and freeze history

- **2026-11-08 — FROZEN v1.** Independent candidate review completed with Spec
  PASS / Quality APPROVED / Ready to freeze YES (agent-5 fresh context). Step 0
  is complete; Stage 1 is next. No amendments have been applied.
- Future changes are dated appended amendments only. Each amendment must state
  its reason, affected claims, prior exposure and required reruns; reviewed
  conventions, findings and numbers must not be silently rewritten.
