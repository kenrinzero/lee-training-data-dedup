# Step 0 derivations and source contract — FROZEN v1

**Frozen date:** 2026-11-08  
**Status:** Step 0 is complete and v1 is frozen after independent review
(Spec PASS / Quality APPROVED / Ready to freeze YES; agent-5 fresh context).
This is the frozen synthesis of approved Task 1/2 artifacts plus Task 3 source
metadata, not a cluster-analysis result. Future changes require dated appended
amendments only.

No cluster archive or full dataset was downloaded or opened, and no cluster-
derived estimate was computed. The historical seed was read only to label prior
exposure. Numerical authority remains the approved Task 1 oracle and Task 2
arithmetic, including the reviewed Figure 1 train-floor correction.

## 1. Approved printed oracle

The source of record is the 22-page ACL PDF at
https://aclanthology.org/2022.acl-long.577.pdf, preserved locally with 720,473
bytes and SHA-256
`dcfa46d7aced43a97b9cf2ebd705919b65d4dd8a44d0914b1e646fe2d59ea8d3`.

- `paper/targets/printed-targets.csv` contains 193 unique scalar rows:
  C1 3, C2 23, C3 55, C4 21, C5 59 and C6 32.
- `paper/targets/figure-bars.csv` contains 44 bars: 11 each for Figure 1 and
  Figure 8's top/middle/bottom panels.
- `paper/targets/README.md` supplies final page/table/figure locators, units,
  source discrepancies and the Table 11 transcription.
- Four exact public split sizes absent from the PDF and two absent Table 11
  twentieth-row cells remain `UNRESOLVED` **in the printed oracle**. Public
  metadata below supplies the split inputs separately; it does not alter the PDF
  transcription. The missing twentieth printed row remains missing.

The printed bins are `1,2,3,4,5,[6,10),[11,20),[21,50),[51,500),[501,5000),
[5001,∞)`. Bars count groups, not documents. Exact sizes 10, 20, 50, 500 and
5000 are absent from the printed half-open ranges. Figure 8 has three unlettered
panels; `(a)/(b)/(c)` are reading-order names only.

## 2. Independently pinned public metadata

All records were accessed on **2026-11-08** using metadata/API/documentation or
HEAD requests only.

### 2.1 Split populations

| Dataset | Revision and exact counts | Exact source URLs |
|---|---|---|
| Wiki-40B `en` | Hugging Face `google/wiki40b`, revision `06bfe584d8193cf58f79c6354ecc2a2b94a7deea`; **2,926,536 train**, **163,597 validation**, **162,274 test** pages; join key `wikidata_id` | https://huggingface.co/datasets/google/wiki40b/raw/06bfe584d8193cf58f79c6354ecc2a2b94a7deea/README.md ; https://huggingface.co/api/datasets/wiki40b (resolves to `google/wiki40b`) |
| C4 `en` | Hugging Face `legacy-datasets/c4`, revision `21e98d7063e4037e836a0299d7fbb7efd484e6c3`; **364,868,892 train**, **364,608 validation** examples; join key `url` | https://huggingface.co/datasets/legacy-datasets/c4/raw/21e98d7063e4037e836a0299d7fbb7efd484e6c3/README.md ; https://huggingface.co/api/datasets/legacy-datasets/c4 |
| LM1B `plain_text` | Hugging Face `billion-word-benchmark/lm1b`, revision `35161838ea9e05371a25a8db037f94fcae4c2064`; **30,301,028 train**, **306,688 test** sentences | https://huggingface.co/datasets/billion-word-benchmark/lm1b/raw/35161838ea9e05371a25a8db037f94fcae4c2064/README.md ; https://huggingface.co/api/datasets/billion-word-benchmark/lm1b ; loader: https://huggingface.co/datasets/billion-word-benchmark/lm1b/raw/35161838ea9e05371a25a8db037f94fcae4c2064/lm1b.py |

Wiki-40B validation and test are distinct arms throughout Stage 1. LM1B has a
public held-out `test`, not a separate public validation split. The LM1B
arithmetic maps the paper's evaluation terminology to `test` explicitly; without
that assumption the held-out-adjusted numerical verdict is indeterminate.

RealNews split metadata and exact public original train size are not pinned.
Consequently its Table 2 split cells and direct train removals are not executable
from the released cluster CSV.

### 2.2 Authors' repository and rights statements

Repository: `google-research/deduplicate-text-datasets`, pinned commit
**`4e9888ac3f95dc4f6169867a04c4c19df02dafe3`** (commit date
2024-05-21T17:47:37Z).

- Commit record: https://api.github.com/repos/google-research/deduplicate-text-datasets/commits/4e9888ac3f95dc4f6169867a04c4c19df02dafe3
- Commit page: https://github.com/google-research/deduplicate-text-datasets/commit/4e9888ac3f95dc4f6169867a04c4c19df02dafe3
- Pinned README: https://raw.githubusercontent.com/google-research/deduplicate-text-datasets/4e9888ac3f95dc4f6169867a04c4c19df02dafe3/README.md
- Pinned licence: https://raw.githubusercontent.com/google-research/deduplicate-text-datasets/4e9888ac3f95dc4f6169867a04c4c19df02dafe3/LICENSE

The licence file is **Apache License 2.0**. The README says the CSV columns are
document ID, a boolean described as whether the document was deleted, and
cluster ID; C4/RealNews IDs are URLs and Wiki-40B IDs are `wikidata_id`. It asks
users of the repository or deduplicated datasets to cite the paper and says the
project is not an officially supported Google product. It lists LM1B as
"coming soon" in the Approx Deduplication Results section. Neither statement
proves the operational meaning of `keep` for every row; Stage 1 must test the
exposed singleton lead.

Apache-2.0 is the repository/code licence. No separate cluster-CSV licence was
found in these pinned statements. Cluster redistribution rights therefore remain
unresolved and gated. The pinned Wiki-40B card says "More Information Needed"
for licensing; no unrestricted Wiki redistribution right is inferred. Raw
clusters and source rows stay local; publish code and aggregates only absent a
later rights review.

### 2.3 Cluster availability and external context

HEAD metadata on 2026-11-08 returned 200 for Wiki-40B, C4 and RealNews and 404
for LM1B. Exact response headers and acquisition gates are in
`data/raw/MANIFEST.md`. HEAD success does not establish member name, decompressed
size, SHA-256, schema, row count or release identity.

The external Google Research abstract at
https://research.google/pubs/deduplicating-training-data-makes-language-models-better/
states "1.68% of the C4 are near-duplicates." This is a separate publication-
page claim with unresolved denominator/basis, not a substitute for any PDF cell.

## 3. Deterministic cluster formulas for future stages

For cluster `c`, `n_all` is physical released rows and `n_train`, `n_E` are rows
joined to train and selected evaluation split `E`. Multi-document membership is
`n_all>=2`; singleton is `n_all=1`.

```text
TT numerator = sum_c n_train(c) * 1[n_train(c) >= 2]
EE numerator = sum_c n_E(c)     * 1[n_E(c) >= 2]
ET numerator = sum_c n_E(c)     * 1[n_train(c) >= 1]

Rule A(c) = n_train(c)                 if n_E(c) > 0
          = max(0, n_train(c) - 1)     otherwise
Rule B(c) = max(0, n_train(c) - 1)
All-train sensitivity(c) = n_train(c)  if n_all(c) >= 2, else 0
```

Each percentage uses the exact public target-split denominator. These Table 2
indicators do not use `keep`. For every split `S`, exact population balance is
also required: `sum_c n_S(c)=N_S`, alongside unmatched, missing and cross-split
checks. Failure makes the affected cells `INDETERMINATE_JOIN`. Unequal same-
split key multiplicities may be accepted only when totals balance and no cross-
split ambiguity exists; the estimand is then explicitly released-physical-row
weighted, not unique-public-document weighted.

Validation-only/test-only clusters have zero train removals; spanning clusters
follow the formulas. Wiki validation and test are evaluated separately, with a
labelled union sensitivity only.

Table 11 instead uses the caption's source-native "marked as near-duplicates by
NEARDUP" estimand: faithful `Frac Dups=keep=0 physical rows/# Total`. Multi-
document-cluster fractions are sensitivity only. `KEEP_MEMBERSHIP_DIVERGENCE`
preserves both results and prohibits grading the printed cell against the wrong
estimand. C4's derived top 20 first filters to URLs whose unrounded `keep=0`
share is exactly 1, then ranks by total descending and URL bytewise ascending.

Figures use all released rows. Edge sizes are evaluated low, high or dropped. A
unique 11/11 Wiki match locks a primary. Zero matches lock all three candidates;
multiple matches lock the matching subset. No primary exists in either ambiguous
branch, and C4 cannot break the tie. Convention-dependent C4 outputs remain
sensitivity/`AMBIGUOUS_CONVENTION` (or stop), while non-convention outputs may
proceed if release identity otherwise holds. These are future tests, not Step-0
results.

## 4. Approved printed arithmetic

### 4.1 C4 Table 2 removal ceiling — conditional contradiction

Task 2 uses exact public `N_t=364,868,892`, `N_v=364,608`, printed TT 3.04% and
Table 13 ORIGINAL/NEARDUP 364.87M/350.48M. Under common-population,
evaluation-preferred keep-one semantics, every removed train document has a
train or validation duplicate. Generously allowing all TT documents plus at most
one additional removal per validation document gives:

```text
D_tt nominal = 0.0304 * 364,868,892 = 11,092,014.3168
U nominal    = D_tt + 364,608       = 11,456,622.3168
U rounded    < 0.03045 * 364,868,892 + 364,608
             = 11,474,865.7614
```

The difference between the two printed rounded Table 13 sizes is 14.39M, with
rounding-compatible interval `(14.38M,14.40M)`. Thus:

```text
nominal shortfall = 14,390,000 - 11,456,622.3168
                  = 2,933,377.6832
robust gap        = 14,380,000 - 11,474,865.7614
                  = 2,905,134.2386
```

**Step-0 verdict: contradiction**, conditional on the tables sharing the NEARDUP
population and the stated removal semantics. It does not identify whether the
cause is a printed cell, release, split basis or convention. Stage 2 remains
necessary.

### 4.2 Figure 1 bounds — corrected train floor and interval consistency

From the 11 approved bar counts:

```text
C_all                         = 350,822,523 plotted clusters
C_multi                       =   2,502,048 plotted multi-document clusters
D_singleton                   = 348,320,475 singleton documents
D_multi lower edge            =  10,868,122 documents
D_all lower edge              = 359,188,597 documents
N = train + validation        = 365,233,500
unaccounted above lower edges =   6,044,903 documents
D_multi upper under full N    =  16,913,025 documents
```

The lower-edge multi-document share is 2.975664061483955...% of train plus
validation. It is a bound, not an exact share.

For one retained copy per multi-document cluster, the **whole-population**
keep-one lower count is:

```text
R_whole >= 10,868,122 - 2,502,048 = 8,366,074.
```

This is not directly a train-removal floor because a retained copy can be in
validation. Subtracting the entire validation split gives the corrected,
deliberately conservative train floor; the whole-document budget gives the
upper bound:

```text
R_train >= 8,366,074 - 364,608 = 8,001,466
R_train <= 365,233,500 - 348,320,475 - 2,502,048
                              = 14,410,977
```

The corrected floor is 2.192970180642311...% of train; the upper bound is
3.949631584377437...% of train. Table 13's printed-difference interval lies
inside `[8,001,466,14,410,977]`.

**Step-0 verdict: consistent interval**, conditional on Figure 1 covering public
train+validation and keep-one semantics. Exact shares/removals remain
indeterminate from printed bars because of omitted edges and within-bin sizes.
The stale use of 8,366,074 as a train floor is not revived.

### 4.3 Random-split identities — exact formulas, printed-only VV indeterminate

For cluster size `s` and independent evaluation assignment probability `q`:

```text
P_ET(s) = 1 - q^(s-1)              conditional on evaluation target
P_EE(s) = 1 - (1-q)^(s-1)          conditional on evaluation target
P_TT(s) = 1 - q^(s-1)              conditional on train target
```

For an exact finite population of `N` documents, `V` evaluation and `T=N-V`
train:

```text
P_ET(s) = 1 - C(V-1,s-1)/C(N-1,s-1)
P_EE(s) = 1 - C(T,s-1)/C(N-1,s-1)
P_TT(s) = 1 - C(V,s-1)/C(N-1,s-1)
```

With `n_s` clusters of size `s`, expectations are document-weighted:

```text
E[P_ET] = (1/N) sum_s s*n_s * [1-C(V-1,s-1)/C(N-1,s-1)]
E[P_EE] = (1/N) sum_s s*n_s * [1-C(T,s-1)/C(N-1,s-1)]
```

Under independent splitting, the all-document multi-cluster share `A` satisfies
`A-E[P_ET]=sum_{s>=2}(s*n_s/N)*q^(s-1)`. Thus ET equals A only when every
materially weighted multi-document cluster retains a train member; small-
evaluation random splitting can make it an approximation, not an identity.

**Step-0 verdict: indeterminate** for a numerical reconstruction of C4's 1.59%
from printed aggregates. Stage 2 must compute `E[P_EE]` from the full histogram
before comparing it with 1.59%; direct observed EE is a separate check.

### 4.4 LM1B printed-only floor — conditional contradiction

Using public `N=30,301,028+306,688=30,607,716` and Figure 8(a):

```text
C_all                              = 29,784,672
C_multi                            =    687,845
D_multi lower edge                 =  1,505,410
D_all lower edge                   = 30,602,237
unaccounted documents              =      5,479
maximum omitted edge-size clusters =        547 (remainder 9 documents)
plotted keep-one lower             =    817,565
held-out-adjusted train floor      = 817,565 - 306,688 = 510,877
```

Table 13's printed difference is 430,000, with rounding-compatible interval
`(420,000,440,000)`. The floor exceeds the nominal difference by 80,877 and the
largest printed-difference-compatible value by **70,877**. Omitted edge clusters
can only increase the floor.

**Step-0 verdict: contradiction**, conditional on Figure 8(a) covering public
train+held-out, evaluation mapping to public `test`, and keep-one semantics. No
LM1B cluster test is authorized or currently executable.

### 4.5 Supporting arithmetic

- `100*61,036/364,868,892 = 0.016728200550459642...%` and
  `100*61/364,608 = 0.016730296647358260...%`; both round to printed **0.02%**.
  Reverse-treating 0.02% as exact is not a valid objection.
- Table 13 C4 NEARDUP implies 3.9438704196015019...% reduction, rounding to
  Appendix D's **3.9%**. Appendix C's 152K/146K steps at batch 4,800 over two
  epochs imply 364.8M/350.4M examples, consistent with approximate 365M/350M
  and Table 13's rounded values. TT 3.04% is not a removal percentage.
- Table 13 C4 EXACTSUBSTR repeats NEARDUP at 350.48M, while Appendix C groups
  ORIGINAL/EXACTSUBSTR at approximately 365M and 152K steps, and §5.1/Appendix E
  says EXACTSUBSTR does not remove examples outright for the stated context.
  **Verdict: contradiction; copy/transcription explanation not established.**

## 5. Exact-original Table 13 comparisons versus printed differences

Future stage comparisons use exact public original `N`, not only subtraction of
two rounded printed cells. With two-decimal million values and ROUND_HALF_UP, a
printed NEARDUP `mM` admits final counts `[mM-5,000,mM+5,000)`. Therefore:

| Population | Exact public `N` | Printed NEARDUP | Exact-original removal interval |
|---|---:|---:|---:|
| C4 train | 364,868,892 | 350.48M | **(14,383,892,14,393,892]** |
| Wiki-40B train | 2,926,536 | 2.91M | **(11,536,21,536]** |
| LM1B train, printed-only | 30,301,028 | 29.87M | **(426,028,436,028]** |

These intervals supplement, and do not rewrite, Task 2's approved rounded-
printed-cell derivations. RealNews has no exact public `N`; its split-free
ceiling is `U=sum_{n_all>=2}(n_all-1)`. Independently rounded ORIGINAL 31.16M and
NEARDUP 28.39M imply printed-difference removals in **(2,760,000,2,780,000)**, so
the smallest compatible integer removal is **2,760,001**. Therefore
**`U <= 2,760,000` is `CONTRADICTION`** under keep-one semantics; otherwise
(`U >= 2,760,001`) the verdict is only **`CEILING_COMPATIBLE`**, not a train-size
reproduction.

RealNews §5.3's **14.4%** has a separate printed-rounding disposition: Table 2's
**14.35% rounds half up to 14.4%**. This establishes printed consistency only and
does not reproduce the unavailable split cell.

## 6. Step-0 findings versus future cluster tests

Step 0 establishes the printed oracle, metadata, formulas, conditional internal
consistency findings and deterministic contract. It does **not** establish:

- actual Wiki/C4/RealNews cluster counts or the operational `keep` semantics;
- which Wiki public split the paper called `valid`;
- a unique figure-edge convention;
- C4 archive identity, exact Table 2 cells, removals or Table 11 ranking;
- the exact C4 random-split EE expectation;
- RealNews split cells or direct train removals;
- any LM1B cluster result, token count, EXACTSUBSTR result or model behavior.

Stage 1 must regenerate Wiki targets and lock the convention before C4 content.
Stage 2 must pass exact physical rows 365,233,500 and an 11/11 predeclared C4
figure match before faithful C4 cell grading. Under an ambiguous Wiki lock, non-
convention C4 outputs may still proceed when identity otherwise holds, while all
convention-dependent outputs remain sensitivity/`AMBIGUOUS_CONVENTION` or stop.
Failure invokes the release-identity branch rather than post-result tuning.

## 7. Assumptions, unresolved inputs and acquisition gates

1. Figure 1 and LM1B total-based bounds assume full public train+evaluation
   coverage because the figures do not state a split.
2. LM1B evaluation maps to public `test` only by explicit convention.
3. C4/Wiki exact split percentages require complete, exact-key, non-cross-split-
   ambiguous joins and `sum_c n_S(c)=N_S` for every split. Duplicate keys are
   measured, never silently exempted. Balanced unequal same-split multiplicities
   are explicitly released-physical-row weighted.
4. RealNews exact public original size and split mapping remain unresolved;
   acquiring them is a separate gate before direct split/table train verdicts.
5. LM1B cluster source remains unresolved after HEAD 404; do not substitute a
   NEARDUP reimplementation.
6. Archive SHA-256, member identity, decompressed sizes and schemas remain
   unknown until authorized acquisition; HEAD sizes are only acquisition checks.
7. Cluster-CSV and Wiki redistribution rights remain unresolved. Apache-2.0 for
   repository code does not settle those separate rights.
8. Table 11's twentieth printed C4 URL/total/fraction is absent from the PDF;
   released ranking cannot turn it into a recovered printed cell.
9. Exposed seed values and bands are reproduction targets, not prospective
   predictions or tolerance exceptions.

## 8. Checklist lenses carried into review

- **Number/aggregation basis:** groups versus documents, TT/EE/ET versus removals,
  ratios versus percentages, exact split sizes versus rounded table values.
- **Delta arithmetic:** independent recomputation of ceilings, bounds and both
  Table 13 interval bases; preserve the corrected Figure 1 train floor.
- **Configuration/caption mismatch:** pinned revisions, separate Wiki arms,
  dropped figure edges, 19-versus-20 Table 11 rows, unlettered Figure 8 panels.
- **Phantom inputs and pilot overclaim:** no invented RealNews splits, LM1B
  archive, missing URL, token counts or novel predictions from exposed pilots.
- **Scope overclaim:** printed contradictions do not replace reproduction, and
  cluster counts do not adjudicate memorization or model quality.
- **Reader precision:** every conditional finding carries its population,
  rounding, mapping and computability qualifier next to the claim.

These lenses screen the contract; they are not independent scientific approval.

## Amendments and freeze history

- **2026-11-08 — FROZEN v1.** Independent candidate review completed with Spec
  PASS / Quality APPROVED / Ready to freeze YES (agent-5 fresh context). Step 0
  is complete; Stage 1 is next. No amendments have been applied.
- Future changes are dated appended amendments only. Each amendment must state
  its reason, affected derivations or contract rules, prior exposure and required
  reruns; approved arithmetic and reviewed findings must not be silently rewritten.
