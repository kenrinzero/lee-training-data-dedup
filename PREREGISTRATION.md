# Analysis contract — FROZEN v1

**Frozen date:** 2026-11-08  
**Status:** Step 0 is complete and v1 is frozen after independent review
(Spec PASS / Quality APPROVED / Ready to freeze YES; agent-5 fresh context).
Stage results may be graded under this version. Future changes require dated
appended amendments only.

Scope is original idea **Stages 1, 2, 3 and 7**, preceded by Step 0. Substring
recounts, standalone EXACTSUBSTR reproduction and memorization experiments are
deferred. This contract audits duplication statistics and their internal
consistency, not model quality, perplexity, memorization or author intent.

## 1. Evidence hierarchy and prior exposure

The ACL Anthology PDF is the printed source of record. The approved Task 1
oracle (`paper/targets/README.md`, `printed-targets.csv` and `figure-bars.csv`)
contains 193 scalar rows and 44 figure bars with source-native locators. The
approved Task 2 artifacts (`planning/step0/arithmetic.md` and `arithmetic.json`)
are the numerical authority for printed arithmetic and public C4/LM1B metadata.
The historical seed is an exposure ledger and source of hypotheses, never a
numerical oracle. `STEP0_DERIVATIONS.md` summarizes, but does not supersede,
those artifacts.

The seed and its Wiki-40B full-file pilot, C4 head inspection, printed
contradictions, infini-gram probes and prior-work review were visible before
this contract. Consequently:

| ID | Exposed statement | Contract treatment |
|---|---|---|
| E1 | C4 Table 2 and Table 13 are incompatible under a removal ceiling | Exposed printed-arithmetic target; independently re-derived in Task 2 |
| E2 | Wiki-40B `keep=1` marks singletons and `keep=0` marks members of multi-document clusters | Exposed pilot lead; Stage 1 must test it before any C4 use |
| E3 | Wiki-40B printed `valid` may align with public `test`; exposed pilot values are train 0.699%, validation 0.264%/0.696%, test 0.258%/0.717% | Reproduction targets, not novel predictions; grade validation and test separately |
| E4 | Dropping exact edge sizes reproduces the Wiki-40B figure | Exposed convention lead; evaluate low, high and dropped without selecting by C4 outcome |
| E5 | C4 has 365,233,500 physical rows and reproduces Figure 1 | Exposed release-identity lead and kill gate |
| E6 | C4 train duplication lies in [4.4,4.8]% and rule-derived removals in [14.38,14.42]M | Exposed pilot bands, not new predictions or tolerance exceptions |
| E7 | LM1B's figure implies more removals than Table 13 | Exposed printed-only lead; Task 2 independently derived the conditional 510,877 floor |
| E8 | The old Wiki removal band 17–18k missed the exposed pilot | Retain as an exposed failed band; do not revise it into a prediction |
| P1 | Exact C4 validation-with-validation random-split expectation requires the full cluster-size histogram | Prospective computation plan; no numerical expectation is predeclared |

No genuinely novel numerical prediction is added. Exposed bands do not replace
the cell-by-cell verdict rules below.

## 2. Pinned sources and acquisition gates

All web records in this section were accessed on **2026-11-08**. Full URLs,
HEAD metadata and rights qualifications are preserved in `data/raw/MANIFEST.md`.
No archive, full dataset or dataset row content was acquired for this contract.

- **Paper:** https://aclanthology.org/2022.acl-long.577.pdf; local SHA-256
  `dcfa46d7aced43a97b9cf2ebd705919b65d4dd8a44d0914b1e646fe2d59ea8d3`.
- **Authors' repository:** `google-research/deduplicate-text-datasets`, commit
  `4e9888ac3f95dc4f6169867a04c4c19df02dafe3`. The pinned `LICENSE` is
  Apache-2.0. The README describes CSV columns and asks users of the repository
  or deduplicated datasets to cite the paper. It does not state a separate
  cluster-CSV licence; cluster redistribution remains gated.
- **Wiki-40B:** Hugging Face `google/wiki40b`, configuration `en`, revision
  `06bfe584d8193cf58f79c6354ecc2a2b94a7deea`; exact public splits are
  **2,926,536 train**, **163,597 validation**, **162,274 test** pages. The join
  field is `wikidata_id`.
- **C4:** Hugging Face `legacy-datasets/c4`, configuration `en`, revision
  `21e98d7063e4037e836a0299d7fbb7efd484e6c3`; **364,868,892 train** and
  **364,608 validation** examples. The join field is `url`.
- **LM1B:** Hugging Face `billion-word-benchmark/lm1b`, `plain_text`, revision
  `35161838ea9e05371a25a8db037f94fcae4c2064`; **30,301,028 train** and
  **306,688 test** sentences. Printed-only arithmetic maps evaluation language
  to public `test` explicitly; it does not rename the source split.
- **Cluster endpoints:** HEAD returned 200 for `wiki40b.tar.gz`, `c4.tar.gz` and
  `realnews.tar.gz`, with exact byte counts in the manifest. `lm1b.tar.gz`
  returned 404. HEAD availability is not archive integrity, schema or release
  identity.

Before any run, acquire only the authorized input, record actual bytes and
SHA-256, and verify them against the run receipt. Any split-file content needed
for joins is a future gated acquisition; this contract pins metadata only.
RealNews has no pinned public split mapping or exact public original size. Its
Table 2 split cells and direct train-removal reproduction are therefore not
executable released-cluster checks.

## 3. Row, cluster and join semantics

### 3.1 Physical rows and cluster membership

Parse the released CSV as physical rows without deduplicating IDs. Record
header, member name, parser/version, row order, malformed rows, empty fields,
duplicate cluster IDs and duplicate document IDs. A malformed row or unexpected
schema stops the affected analysis until explained.

For cluster `c`, let `n_all(c)` be its physical released rows and let
`n_train(c)`, `n_validation(c)` and `n_test(c)` be the rows assigned to each
public split. A singleton has `n_all(c)=1`; a multi-document cluster has
`n_all(c)>=2`. Table 2 duplication metrics use these memberships, not merely the
CSV `keep` flag.

Stage 1 first tabulates the exposed Wiki-40B lead: agreement of `keep=1` with
singletons and `keep=0` with multi-document membership. Report both directions
and every discrepancy. Only if that test is completed may `keep` be used on C4;
Table 2 primary indicators remain cluster-membership based. The README's word
"deleted" is not treated as proof that a retained copy is identified.

Table 11 implements a different, source-native estimand. Its caption says
examples "marked as near-duplicates by NEARDUP"; faithful `Frac Dups` is therefore
**physical rows with `keep=0` divided by physical `# Total`**. The fraction of
physical rows in multi-document clusters is diagnostic/sensitivity only. If the
two disagree, emit `KEEP_MEMBERSHIP_DIVERGENCE` with row-, cluster- and URL-level
counts. Grade printed Table 11 cells only against the `keep=0` estimand, retain
both tables, and never manufacture a `MISMATCH` by substituting the membership
estimand. Missing or invalid `keep` makes the faithful cell
`NOT_EXECUTABLE_INPUT`; it does not authorize substitution.

### 3.2 Exact-key joins

Wiki-40B joins the parsed CSV `id` to `wikidata_id`; C4 joins it to `url`. Keys
are compared exactly as parsed UTF-8 strings: no case folding, scheme removal,
host normalization, trailing-slash removal or whitespace trimming. Any
whitespace or encoding anomaly is reported, not silently repaired.

For each released row, compute a split mask from all public rows carrying its
key. Repeated keys within one split assign that split to every released row with
the key; physical released rows remain distinct. A key occurring in multiple
splits is **cross-split ambiguous**: report its multiplicity and mark every
split-dependent cell it touches `INDETERMINATE_JOIN`; never choose an occurrence
arbitrarily. Released rows unmatched to the public keys, and public keys absent
from the release, are counted and stop exact split-dependent verdicts until
explained. There is no duplicate-URL exemption from the C4 physical-row kill
test.

A complete Wiki split join must account for exactly 2,926,536/163,597/162,274
public pages and all released rows. A complete C4 join must account for exactly
364,868,892/364,608 public examples and all released rows. Percentage
denominators are the exact public split counts, not unique-key counts.

For **every split** `S`, the population-balance gate is
`sum_c n_S(c) = N_S`, where `N_S` is that exact public split size. If this fails,
the affected split-dependent cells are `INDETERMINATE_JOIN` even when no
unmatched, missing or cross-split key was reported. Unequal same-split key
multiplicities may be accepted only when every total balances and no cross-split
ambiguity exists; label the resulting estimand **released-physical-row weighted**,
not unique-public-document weighted, and preserve the multiplicity table.

### 3.3 Evaluation populations and figure populations

Wiki-40B `validation` and `test` are separate evaluation arms. For arm `E`, the
other evaluation split is not relabelled as train and is not used as an
evaluation duplicate. The printed word `valid` remains in source labels and
output column names until results are reported.

C4 uses public `validation` as its only evaluation arm. LM1B's public `test` is
used only in the explicitly mapped printed-only derivation. RealNews split masks
are unavailable.

Figure histograms use **all physical released rows**, with the population named
as `released archive, all splits`. If the relevant complete join succeeds, also
state the verified public composition: Wiki train+validation+test or C4
train+validation. Do not infer a train-only figure from Table 13.

## 4. Duplication metrics and removal rules

For a selected evaluation arm `E`, define document-level indicators:

- **train-with-train (TT):** a train document is duplicated when
  `n_train(c)>=2`; numerator `sum_c n_train(c) * 1[n_train(c)>=2]`, denominator
  exact public train size.
- **evaluation-with-evaluation (EE):** an evaluation document is duplicated when
  `n_E(c)>=2`; numerator `sum_c n_E(c) * 1[n_E(c)>=2]`, denominator exact public
  size of `E`.
- **evaluation-with-train (ET):** an evaluation document is duplicated when
  `n_E(c)>=1` and `n_train(c)>=1`; numerator `sum_c n_E(c) *
  1[n_train(c)>=1]`, denominator exact public size of `E`.

A singleton cannot contribute to any indicator. Other-split members neither
create nor remove an indicator unless they belong to the named target or train
population. Report numerator, denominator, unrounded ratio and rounded printed
comparison for every cell.

For each cluster and selected evaluation arm `E`, compute three separate train
removal counts:

1. **Rule A — evaluation-preferred keep-one.** If `n_E(c)>0`, retain one
   evaluation copy and remove all `n_train(c)` train members. Otherwise, if
   `n_train(c)>0`, retain one train copy and remove `max(0,n_train(c)-1)`.
   Thus `R_A(c)=n_train(c)` when `n_E(c)>0`, else `max(0,n_train(c)-1)`.
2. **Rule B — uniform train keep-one.** Always retain one train copy when one
   exists: `R_B(c)=max(0,n_train(c)-1)`, regardless of evaluation membership.
3. **All-train sensitivity.** In every multi-document cluster (`n_all(c)>=2`),
   remove every train member: `R_S(c)=n_train(c)`; singleton clusters contribute
   zero.

Evaluation-only clusters have zero train removals. Train-plus-evaluation
clusters differ between Rules A and B exactly as the formulas state.
Validation-only and test-only Wiki clusters are evaluated under their own arm;
under the other arm they have `n_E=0`, so Rule A falls back to train keep-one.
Also run a clearly labelled Wiki `validation+test` evaluation-union sensitivity
for Rule A, never as the default interpretation of printed `valid`.

The retained train size is exact public train size minus train removals. Rules
A and B are alternative interpretations, not observed author deletions; the
all-train rule is a sensitivity, never the faithful default.

## 5. Figure bins and convention lock

The printed bins are `1`, `2`, `3`, `4`, `5`, `[6,10)`, `[11,20)`, `[21,50)`,
`[51,500)`, `[501,5000)`, `[5001,∞)`. Each bar counts clusters, not documents.
Evaluate exactly three predeclared assignments of edge sizes 10, 20, 50, 500 and
5000:

| Convention | Assignment to adjacent printed bins |
|---|---|
| `dropped` | Omit all five edge sizes from the 11 plotted bars; report their cluster and document counts separately |
| `low` | Assign each edge size to the lower/larger-left-endpoint printed bin: 10→`[6,10)`, 20→`[11,20)`, 50→`[21,50)`, 500→`[51,500)`, 5000→`[501,5000)` |
| `high` | Assign each edge size to the higher/smaller-right-endpoint printed bin: 10→`[11,20)`, 20→`[21,50)`, 50→`[51,500)`, 500→`[501,5000)`, 5000→`[5001,∞)` |

These arrows name the destination printed bin only; they do not alter the
printed labels. Preserve all three complete 11-bar tables and all dropped-edge
counts in every stage.

Stage 1 locks conventions solely by printed fidelity. If exactly one convention
reproduces all 11 Wiki-40B Figure 8 bottom-panel labels, that convention is the
primary and the locked candidate set is its singleton. If **zero** match, the
locked candidate set is **all three**; if **multiple** match, the locked set is
exactly the matching subset. Both ambiguous branches have **no primary**. C4
results cannot break the tie, shrink the locked set or create a primary.

Stage 2's release-identity test separately requires at least one predeclared
convention to reproduce all 11 C4 labels. Under a unique Wiki primary, a C4 match
only by a non-primary convention is release/convention forensics, not a silent
promotion; downstream faithful convention-dependent outputs use the Stage-1
primary and alternatives remain sensitivities. Under a locked ambiguous candidate
set, every convention-dependent C4 output is labelled sensitivity/
`AMBIGUOUS_CONVENTION` (or the convention-dependent branch stops), even if only a
subset matches C4. Non-convention outputs—including direct Table 2 cells, exact
cluster counts, removal rules and Table 11—may proceed when row count, join and
other release-identity requirements hold. No ambiguous branch is required to
select an impossible primary.

## 6. Rounding, printed sizes and verdict rules

Use decimal **ROUND_HALF_UP** at each cell's printed precision. For a percentage
printed with `p` digits after the decimal in percent units, compute
`100*numerator/denominator`, round half up to `p` digits and require exact
formatted equality. Apply the same rule to ratios at their displayed precision.
Counts, row totals, figure bars, cluster counts and largest-cluster size match
exactly. No exposed pilot band is a tolerance exception.

For Table 13 example sizes, let `N` be the exact public original train size and
let printed values in million examples have two decimal places. Check:

1. `ROUND_HALF_UP(N/1,000,000, 2)` against ORIGINAL;
2. `ROUND_HALF_UP((N-R)/1,000,000, 2)` against NEARDUP for each rule-derived
   removal `R`; and
3. the implied removal interval obtained from exact `N` and the printed NEARDUP
   rounding interval. For printed `m` million, the compatible final counts are
   `[mM-5,000, mM+5,000)`, so removals lie in
   `(N-mM-5,000, N-mM+5,000]`, with `M=1,000,000`.

For C4 this exact-original interval is **(14,383,892, 14,393,892]**; for
Wiki-40B it is **(11,536, 21,536]**; for LM1B printed-only arithmetic it is
**(426,028, 436,028]**. Keep these distinct from Task 2's difference between two
independently rounded printed cells, e.g. C4 `(14.38M,14.40M)`. RealNews lacks
an exact public `N`; a released-archive total may support only a conditional
release-population comparison after it is measured.

The approximate §5.1 **1.8M pair-cluster** statement passes its quantitative
check when the exact number of size-2 clusters rounds half up to 1.8 at one
decimal million; separately test the printed "majority" as
`n_2 > C_multi/2`. Report the exact `n_2`. The 280 clusters over 5,000 and
250,933 largest size require exact equality. Count size 5,000 separately from
the prose's "over 5,000" and Figure 1's `[5001,∞)` bin.

Verdict labels are:

- `MATCH` / `MISMATCH`: executable printed comparison under the frozen rule;
- `CONSISTENT_INTERVAL` / `CONTRADICTION`: printed-only or interval arithmetic,
  with premises adjacent;
- `AMBIGUOUS_CONVENTION`: no unique convention is locked (zero or multiple Wiki
  11/11 matches); convention-dependent outputs remain sensitivity or stop;
- `INDETERMINATE_JOIN`: required split membership is not uniquely determined or
  exact per-split population balance fails;
- `NOT_EXECUTABLE_INPUT`: necessary clusters, split metadata or other inputs
  are unavailable;
- `SOURCE_MISSING`: the printed source omits the target, notably Table 11's
  twentieth row;
- `KILL_RELEASE_IDENTITY`: the Stage-2 release-identity branch stopped faithful
  C4 cluster reproduction.

A miss triggers only predeclared source, split, duplicate-key and convention
forensics. A new convention discovered after results cannot become faithful
without a dated amendment and explicit exposure label.

## 7. Stage 1 — Wiki-40B and convention lock

From an immutable, hash-checked run, regenerate:

1. physical rows, unique IDs, cluster histogram, split-join coverage and
   duplicate/cross-split diagnostics;
2. the `keep` singleton lead test;
3. TT; EE and ET separately for validation and test, with exact numerators and
   denominators;
4. Rules A, B and all-train sensitivity for validation, test and the labelled
   evaluation-union sensitivity;
5. all 11 bars under all three edge conventions and exact edge-size counts over
   all released rows;
6. Table 13 original and retained sizes using exact public train size and the
   printed rounding intervals.

The exposed values 0.699%, 0.264%, 0.258%, 0.696% and 0.717%, plus exposed
Rule A/B retained sizes, are regeneration targets only. Grade both evaluation
arms and retain every result even if only test resembles the printed third
cell. Do not rename printed `valid` before results.

Stage 1 is complete when the outputs and discrepancies are written and the locked
candidate set is recorded before opening C4 content: a singleton primary after a
unique 11/11 match, all three after zero matches, or the matching subset after
multiple matches. A Wiki mismatch does not authorize selecting a new rule for C4,
and an ambiguous lock has no primary to select.

## 8. Stage 2 — C4 cluster audit

### 8.1 Release-identity kill branch

Stream `c4.csv` from `c4.tar.gz` without extracting the full CSV. Before any
faithful printed-cell verdict, require both:

- physical CSV rows equal **365,233,500**, including all duplicate URLs; and
- at least one of `dropped`, `low`, `high` reproduces **all 11 Figure 1 labels
  exactly** over all released rows.

Duplicate URLs are measured and reported, never an unspecified row-count
exemption. If either condition fails, emit `KILL_RELEASE_IDENTITY`, stop the
faithful C4 cluster branch, and ship release forensics plus the independent
printed arithmetic. Do not tune bins, delete duplicate rows or change the join
until the test passes. Already completed Wiki and printed-only audits remain
valid independent outputs.

### 8.2 Required computations if identity holds

- Recompute C4 TT, validation-with-validation and validation-with-train directly
  from cluster membership and the complete split join.
- Compute the exact finite-population random-split EE expectation from the full
  cluster-size histogram before the comparison routine reads printed 1.59%:
  `E[P_EE]=(1/N)*sum_s s*n_s*[1-C(T,s-1)/C(N-1,s-1)]`, with
  `N=365,233,500`, `V=364,608`, `T=N-V`. Serialize the expectation first, then
  compare it as a secondary random-split check. Printed aggregates alone leave
  it indeterminate; the direct observed EE cell remains a separate target.
- Recompute Table 13 under Rules A and B, report the all-train sensitivity, and
  grade original/retained sizes and exact-original removal intervals as in §6.
- Emit all Figure 1 conventions, exact edge sizes, full cluster-size histogram,
  singleton documents, multi-document clusters and document counts. Apply the
  unique-primary or ambiguous-candidate branch locked in Stage 1.
- Recompute size-2 clusters, clusters over 5,000 and largest cluster size for
  the §5.1 verdicts.
- Recompute Table 11's 19 printed C4 rows. For each printed URL, `# Total` is
  its physical released row count and faithful `Frac Dups` is physical `keep=0`
  rows divided by `# Total`. Compare counts exactly and ratios by ROUND_HALF_UP
  at displayed precision. For the derived top-20 ranking, first filter to URLs
  whose **unrounded `keep=0` share equals 1**, then rank by `# Total` descending
  and URL bytewise ascending. Directly transcribed oracle rows remain unchanged.
  The absent twentieth printed URL/total/fraction is `SOURCE_MISSING`; a released-
  ranking candidate is not a recovery of the omitted printed cell.
- Report duplicate URLs, unmatched keys, cross-split keys, per-split population
  balance and `keep` versus cluster-membership diagnostics. On disagreement,
  apply `KEEP_MEMBERSHIP_DIVERGENCE`: membership remains faithful for Table 2,
  `keep=0` remains faithful for Table 11, and neither estimand is substituted for
  the other to create a verdict.

If the release identity fails, required cells that cannot be computed from
another authorized source receive the kill-branch verdict rather than forced
cluster agreement.

## 9. Stage 3 — RealNews cluster audit

Use all released rows to regenerate Figure 8 middle-panel bars under all three
conventions, exact edge sizes, total rows, full cluster histogram and Table 11's
19 printed RealNews rows. Faithful Table 11 `Frac Dups` is physical `keep=0`
rows divided by physical `# Total`, as for C4; cluster-membership fractions are
sensitivity only and disagreements invoke `KEEP_MEMBERSHIP_DIVERGENCE`. Report
the eligible `# Total>=10` list ordered by faithful unrounded fraction descending,
total descending, then URL bytewise ascending.

Compute the split-free keep-one ceiling
`U=D_multi-C_multi=sum_{c:n_all(c)>=2}(n_all(c)-1)`. Independently rounded
ORIGINAL 31.16M and NEARDUP 28.39M give printed-difference removals in
**(2,760,000,2,780,000)**, whose smallest compatible integer is **2,760,001**.
Thus **`U <= 2,760,000`** is `CONTRADICTION` under keep-one semantics; otherwise
(`U >= 2,760,001`) the verdict is only `CEILING_COMPATIBLE`, not a train-size
match. Separately record that printed Table 2 **14.35% rounds half up to §5.3's
14.4%**; this is printed-rounding consistency, not reproduction of the
unavailable split cell.

Without a pinned exact public original size and split mapping, the three
RealNews Table 2 cells and direct train removals are `NOT_EXECUTABLE_INPUT`.
Compare Table 13 ORIGINAL/NEARDUP directly only if an exact public original is
later pinned by amendment, or conditionally using the measured release total
with that assumption named. Never invent train/validation/test assignments for
access-gated source data.

## 10. Stage 7 — visualizer and integrated report

Generate Figure 1 and Figure 8 panels solely from immutable Stage 1–3 outputs.
Show all released bars and annotate dropped exact edge sizes; do not hide failed
or ambiguous conventions. Include an offline ledger distinguishing printed,
directly recomputed, rule-derived and printed-only values, including C4 1.68%
from the external publication abstract, 3.04%, Table 13's implied removal,
Appendix D's 3.9%, and Figure 1 bounds. The 1.68% source is
https://research.google/pubs/deduplicating-training-data-makes-language-models-better/
(accessed 2026-11-08); it is not a PDF Table 2 substitute.

Every included printed cell links to its output and verdict. Where no necessary
input exists, show the explicit non-executable reason rather than a blank or a
surrogate value.

## 11. Coverage and grading ledger

| Claim group | Included targets and verdict basis |
|---|---|
| C1 | All three C4 Table 2 cells by direct cluster recount; 1.59% additionally by the exact histogram expectation; §5.3's 4.6% only as printed rounding of 4.60%, not a separate split |
| C2 | C4 Table 13 ORIGINAL and NEARDUP examples under both rules plus sensitivity; printed-difference and exact-original intervals; Appendix C/D and Table 6 anchors by printed arithmetic. Token counts require tokenization unavailable from clusters and are `NOT_EXECUTABLE_INPUT`; EXACTSUBSTR reproduction is deferred |
| C3 | All 11 C4 bars; approximate 1.8M size-2 clusters plus majority; exact 280 and 250,933; 19 printed C4 URL rows (38 cells) using faithful `keep=0 / # Total`, the unrounded fraction-1 top-20 filter, and the missing twentieth row as `SOURCE_MISSING` |
| C4 | Wiki Table 2 three printed columns against validation and test separately; Table 13 ORIGINAL/NEARDUP under both rules; all 11 bottom-panel bars and edge sizes. Token/EXACTSUBSTR cells are not derivable under this scope |
| C5 | All 11 RealNews bars, 19 URL rows (38 cells) using faithful `keep=0 / # Total`, total rows and split-free ceiling (`CONTRADICTION` iff `U <= 2,760,000`). All three Table 2 split cells and direct split-dependent Table 13 train removal are `NOT_EXECUTABLE_INPUT` until inputs are pinned; 14.35%→14.4% is printed-rounding consistency only |
| C6 | C4 repeated-sentence percentages, NEARDUP supporting anchors and EXACTSUBSTR internal consistency by Task 2 arithmetic; all 11 LM1B bars and Table 13 by printed-only bounds. All three LM1B Table 2 cells and any LM1B cluster recount are `NOT_EXECUTABLE_INPUT` because no cluster archive is pinned; LM1B validation means public `test` only by explicit mapping |
| C7 | Figures and alternative-percentage ledger regenerate from frozen outputs; visual agreement does not override cell verdicts |

The approved Step-0 arithmetic verdicts remain visible alongside, never replaced
by, future cluster tests: C4 removal-ceiling contradiction with robust gap
**2,905,134.2386**; Figure 1 conditional interval consistency with corrected
train floor **8,001,466** and upper bound **14,410,977**; C4 printed-only VV
indeterminacy; conditional LM1B floor **510,877** contradiction; repeated-
sentence consistency; C4 NEARDUP supporting-anchor consistency; and C4
EXACTSUBSTR size inconsistency without an established copy error.

## 12. Immutable outputs, stopping and review

Each named stage writes a new immutable run directory containing input receipts,
URL/revision/access date, actual bytes and SHA-256, code/environment identity,
schema and join diagnostics, complete convention/sensitivity tables, printed-
versus-derived cells, verdicts and a report. Source hashes are verified before
each run. Named outputs are never overwritten; corrections create a new run and
link the superseded receipt. C4 remains unextracted as a full CSV. Raw inputs
remain local and unchanged; only code and aggregates are publishable unless a
later rights review permits more.

Hash, schema or row-identity failure stops the affected analysis. Follow the
three-attempt cap for repeated acquisition/execution failures and continue only
independent work. A clean negative, partial reproduction, ambiguity or kill-test
exit is complete. Do not extend into deferred experiments to make the audit
appear more conclusive.

Type-A checks cover source identity, counts, execution, rounding, regeneration,
links and UTF-8/LF. Scientific adequacy and reader clarity require independent
Type-B review. Independent candidate review is complete and v1 is frozen;
Stage 1 is next. Publication remains a separate user decision.

## Amendments and freeze history

- **2026-11-08 — FROZEN v1.** Independent candidate review completed with Spec
  PASS / Quality APPROVED / Ready to freeze YES (agent-5 fresh context). Step 0
  is complete; Stage 1 is next. No amendments have been applied.
- Future changes are dated appended amendments only. Every amendment must state
  date, reason, affected analyses, prior exposure and required reruns; never
  silently change a population, convention, tolerance, target or verdict rule.
- **2026-11-09 — Amendment A1: streamed C4 train custody.** Reason: the maintained Parquet train conversion contains only 2,207,027 rows, while the full pinned original train has 1,024 JSON shards totaling 326,778,635,540 bytes and exceeds available local storage. Affected analyses: Stage 2 train split acquisition and custody only; every estimand, join diagnostic, target, tolerance and verdict rule is unchanged. Prior exposure: release identity has passed, but no train join or split-cell result has been opened. Stage 2 may stream each original shard from `allenai/c4` root revision `1588ec454efa1a09f29cd18ddd04fe05fc8653a2` once per acquisition attempt, record actual compressed bytes and SHA-256, and retain an exact URL/split table plus receipts instead of the compressed document bodies. The 2,207,027-row partial Parquet train is excluded and preserved unchanged; full validation Parquet remains usable. Before any split-dependent verdict, the derived public table must prove 364,868,892 train and 364,608 validation physical rows and pass every existing duplicate, cross-split, unmatched, missing-key and population-balance gate. Later runs must hash the preserved derived table and its acquisition manifest; no remote reacquisition may silently replace them. Any failure to establish these identities yields `INDETERMINATE_JOIN` or a new corrected run, never inferred train membership.
