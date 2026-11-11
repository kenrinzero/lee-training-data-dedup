# Step 0 Task 2 — independent printed arithmetic

## Scope and inputs

This derivation uses the 193-row printed oracle in
`paper/targets/printed-targets.csv`, the 44 bars in
`paper/targets/figure-bars.csv`, and the preserved ACL PDF. The historical seed
was not read. No cluster archive or full dataset was downloaded or opened, and
no cluster-derived estimate was computed.

Two public metadata records supply the split sizes left `UNRESOLVED` by the
paper. Both were accessed on **2026-11-08**, using metadata/API requests only.

| Input | Exact value | Public record |
|---|---:|---|
| C4 `en` train | 364,868,892 examples | Hugging Face `legacy-datasets/c4`, revision `21e98d7063e4037e836a0299d7fbb7efd484e6c3`, [pinned dataset card](https://huggingface.co/datasets/legacy-datasets/c4/raw/21e98d7063e4037e836a0299d7fbb7efd484e6c3/README.md), `dataset_info` and Data Splits table. The [repository API record](https://huggingface.co/api/datasets/legacy-datasets/c4) independently returns the same revision and counts. |
| C4 `en` validation | 364,608 examples | Same pinned C4 card and API record. |
| LM1B `plain_text` train | 30,301,028 sentences | Hugging Face `billion-word-benchmark/lm1b`, revision `35161838ea9e05371a25a8db037f94fcae4c2064`, [pinned dataset card](https://huggingface.co/datasets/billion-word-benchmark/lm1b/raw/35161838ea9e05371a25a8db037f94fcae4c2064/README.md), `dataset_info` and Data Splits table. The [repository API record](https://huggingface.co/api/datasets/billion-word-benchmark/lm1b) returns the same revision and counts. |
| LM1B held-out evaluation | 306,688 sentences | Same pinned LM1B card and API record. The public split is named **`test`**, not validation. The [pinned loader](https://huggingface.co/datasets/billion-word-benchmark/lm1b/raw/35161838ea9e05371a25a8db037f94fcae4c2064/lm1b.py) maps the held-out files to `datasets.Split.TEST`. |

For LM1B arithmetic below, the paper's validation/evaluation language is mapped
to the public held-out `test` split as an explicit convention. The source does
not publish a separate validation split. Without that mapping, the
validation-adjusted numerical comparison would be indeterminate.

For rounded Table 13 values in units of 0.01M, ordinary nearest rounding gives
an open rounding interval; using closed endpoints would not change any verdict.
Thus C4 NEARDUP removals lie in `(14.38M, 14.40M)` and LM1B NEARDUP removals in
`(0.42M, 0.44M)`. Table 2's 3.04% is likewise allowed to lie in
`[3.035%, 3.045%)` for the robustness check.

## 1. C4 removal ceiling — contradiction

**Printed and public premises.** Table 2 gives C4 train-with-train duplication
as 3.04%. Table 13 gives ORIGINAL 364.87M and NEARDUP 350.48M train examples.
The public split sizes are `N_t = 364,868,892` and `N_v = 364,608`.

Under keep-one semantics, every removed train document must belong to a
non-singleton cluster and therefore must have a duplicate in train or
validation. Documents with a train duplicate number at most the Table 2
train-with-train count. Any additional removable train document has no train
duplicate but does have a validation duplicate; there can be at most one such
document per validation example. This deliberately generous bound does not
subtract the retained copy from the train-with-train count.

The nominal train-with-train count and ceiling are

```text
D_tt = 0.0304 * 364,868,892
     = 11,092,014.3168 examples,

U = D_tt + N_v
  = 11,092,014.3168 + 364,608
  = 11,456,622.3168 examples.
```

The fractional values are expected values from a printed percentage, not claims
that a document count is fractional. An integer ceiling can only be smaller.
Even allowing Table 2's full rounding interval gives

```text
U_rounded < 0.03045 * 364,868,892 + 364,608
          = 11,474,865.7614 examples.
```

Table 13 directly implies

```text
R_table13 = 364.87M - 350.48M = 14.39M examples,
R_table13 in (14.38M, 14.40M) after rounding allowances.
```

Hence the nominal shortfall is
`14,390,000 - 11,456,622.3168 = 2,933,377.6832` examples. More strongly, the
smallest Table 13-compatible removal count exceeds the largest rounding-aware
ceiling by

```text
14,380,000 - 11,474,865.7614 = 2,905,134.2386 examples.
```

**Verdict: contradiction**, conditional on Table 2 and Table 13 describing the
same NEARDUP population and on keep-one removal with evaluation copies
preferred. This is an internal printed-arithmetic incompatibility under those
stated semantics. A different cluster release, split basis, duplicate flag
convention, or table population could instead produce a release/convention
mismatch; the arithmetic alone does not identify which printed cell or release
is wrong.

## 2. Figure 1 bounds — consistent interval, exact values indeterminate

The 11 bars are group counts, not document counts. Use lower edges
`l = (1,2,3,4,5,6,11,21,51,501,5001)` and the transcribed bar vector `b`.
Direct summation gives

```text
C_all       = sum(b)                    = 350,822,523 plotted clusters,
C_multi     = sum(b[2:])                =   2,502,048 plotted multi-document clusters,
D_singleton = b[1]                      = 348,320,475 singleton documents.
```

For multi-document clusters, exact sizes 2–5 contribute 5,315,545 documents;
the ranged bins contribute another 5,552,577 at their lower edges. Therefore

```text
D_multi^- = sum(l[i] * b[i], i=2..11)  = 10,868,122 documents,
D_all^-   = D_singleton + D_multi^-     = 359,188,597 documents.
```

Assuming the figure covers the pinned public train plus validation population,
`N = 364,868,892 + 364,608 = 365,233,500`, the lower-edge calculation leaves
`365,233,500 - 359,188,597 = 6,044,903` documents unaccounted for. The exact
printed half-open bins omit sizes 10, 20, 50, 500, and 5000, so neither the
exact multi-document count nor the exact removal count follows from the bars.
Under the full-population assumption,

```text
10,868,122 <= D_multi <= 365,233,500 - 348,320,475 = 16,913,025.
```

The lower-bin-edge multi-document share of all documents is

```text
100 * 10,868,122 / 365,233,500
  = 2.975664061483955...%.
```

This is a **lower bound**, not an exact observed share. Using train alone as
the denominator would give 2.978637597858027...%, but train plus validation is
the appropriate base for the full-population assumption above.

For one retained document per multi-document cluster over the combined train
and validation population, `R_whole = D_multi - C_multi`. The bars consequently
give the **whole-population** keep-one lower count

```text
R_whole >= 10,868,122 - 2,502,048 = 8,366,074.
```

This is not by itself a train-removal bound: a cluster's retained copy may be
in validation. Subtracting the entire validation split gives the conservative
train-removal lower bound

```text
R_train >= R_whole - N_v
        >= 8,366,074 - 364,608
        = 8,001,466.
```

A valid train-removal upper bound uses the whole public document budget:

```text
R_train <= N - D_singleton - C_multi
        = 365,233,500 - 348,320,475 - 2,502,048
        = 14,410,977.
```

The upper bound is 3.949631584377437...% of public train examples, or
3.945688716944092...% of all train-plus-validation examples. The corrected
train-removal lower bound is 2.192970180642311...% of train. Omitted edge-size
clusters only make the exact removal total uncertain; the whole-population
lower-edge count 8,366,074 must not be mislabelled as either an upper bound or
a train-removal lower bound.

**Verdict: consistent.** Table 13's rounded removal interval
`(14.38M, 14.40M)` lies inside the corrected Figure 1 train-removal interval
`[8.001466M, 14.410977M]`. This interval test does not determine the exact
figure share or validate a particular treatment of omitted edges. Because the
figure itself does not state its split, the total-based bounds and shares are
conditional on the full-public-split coverage assumption.

## 3. Random-split identities — numerical comparison indeterminate

Let a cluster have size `s`. First suppose each document independently enters
evaluation with probability `q`, so train probability is `1-q`. Conditional on
the target document being in evaluation, duplication with train and with
evaluation have probabilities

```text
P_ET(s) = 1 - q^(s-1),
P_EE(s) = 1 - (1-q)^(s-1).
```

The first expression is one minus the probability that all other members join
the target in evaluation; the second is one minus the probability that all
other members are in train. Conditional on a train target, the analogous
train-with-train identity is `P_TT(s) = 1 - q^(s-1)`.

For an exact finite-population split of `N` documents into `V` evaluation and
`T = N-V` train documents, conditional on an evaluation target there are `V-1`
remaining evaluation documents and `T` train documents among `N-1`. Thus

```text
P_ET(s) = 1 - C(V-1, s-1) / C(N-1, s-1)
        = 1 - (V-1)_(s-1) / (N-1)_(s-1),

P_EE(s) = 1 - C(T, s-1) / C(N-1, s-1)
        = 1 - (T)_(s-1) / (N-1)_(s-1),
```

where `x_(k) = x(x-1)...(x-k+1)` is the falling factorial and a binomial
coefficient with an impossible lower index is zero. For a train target,

```text
P_TT(s) = 1 - C(V, s-1) / C(N-1, s-1).
```

Now let `n_s` be the number of clusters of size `s`, with `N = sum_s s*n_s`.
Averaging over a randomly selected evaluation document gives the exact
finite-population expectations

```text
E[P_ET] = (1/N) * sum_s s*n_s *
          [1 - C(V-1,s-1)/C(N-1,s-1)],

E[P_EE] = (1/N) * sum_s s*n_s *
          [1 - C(T,s-1)/C(N-1,s-1)].
```

The weights `s*n_s/N` are document-weighted, not cluster-weighted. The
all-document multi-cluster share is `A = sum_(s>=2) s*n_s/N`. Under independent
splitting,

```text
A - E[P_ET] = sum_(s>=2) (s*n_s/N) * q^(s-1).
```

Therefore `E[P_ET] = A` only when every materially weighted multi-document
cluster is guaranteed to retain a train member. It is an approximation when
evaluation is small enough that all-evaluation clusters have negligible
probability; random splitting by itself does not make the identity exact.
Large clusters and non-negligible evaluation fractions can make the difference
material.

The exact evaluation-with-evaluation expectation needs the complete
cluster-size histogram `n_s` (or equivalent factorial moments), together with
`N` and `V`. The printed bars do not supply within-bin sizes and omit exact
edge sizes; singleton, multi-document, and cluster totals are insufficient.
No unobserved cluster-size distribution is substituted here.

**Verdict: indeterminate** for a numerical reconstruction or comparison of C4
Table 2's 1.59% validation-with-validation cell. The formulas are exact, but
the printed aggregates do not determine their numerical value.

## 4. LM1B printed-only floor — contradiction

Every Figure 8(a) premise below was checked against the target CSV. The public
train plus held-out population is
`N = 30,301,028 + 306,688 = 30,607,716` sentences.

The plotted cluster counts are

```text
C_all   = 29,784,672,
C_multi = 595,632 + 68,775 + 15,825 + 4,432 + 2,762 + 340 + 66 + 13
        = 687,845.
```

Exact sizes 2–5 account for 1,483,049 multi-cluster documents. Lower edges for
the ranged bins add 22,361, yielding

```text
D_multi^- = 1,505,410 multi-cluster documents,
D_all^-   = 29,096,827 + 1,505,410 = 30,602,237 plotted lower-edge documents.
```

The exact multi-document count is not printed; 1,505,410 is its lower bound.
The full public population leaves `30,607,716 - 30,602,237 = 5,479` documents
outside that lower-edge accounting. Since the smallest omitted exact edge size
is 10, at most

```text
floor(5,479 / 10) = 547 omitted edge-size clusters
```

can fit, with nine documents remaining. This is a maximum cluster count, not a
claim that 547 such clusters exist.

For the plotted multi-document clusters, keep-one removals at lower edges are

```text
R_plotted^- = D_multi^- - C_multi
            = 1,505,410 - 687,845
            = 817,565.
```

At most one retained evaluation copy per cluster can reduce train removals.
Charging **all** 306,688 held-out documents against this bound is deliberately
conservative:

```text
R_train >= 817,565 - 306,688 = 510,877.
```

Omitted edge-size clusters can only increase this floor; subtracting the whole
held-out split already allows them to contain evaluation documents.

Table 13 instead implies `30.30M - 29.87M = 0.43M = 430,000` removals, or
`(420,000, 440,000)` after rounding. The floor exceeds the nominal value by
80,877 and even the largest rounding-compatible value by
`510,877 - 440,000 = 70,877` sentences.

**Verdict: contradiction**, conditional on Figure 8(a) covering the public
train plus held-out population, keep-one semantics, and mapping the paper's
evaluation terminology to LM1B `test`. Without the split mapping, the numerical
verdict is indeterminate; no exact public `validation` split is invented.

## 5. Supporting arithmetic

### 5.1 The 61,036/61 sentence percentages — consistent

Using the exact public C4 split sizes,

```text
100 * 61,036 / 364,868,892 = 0.016728200550459642...%,
100 * 61     / 364,608     = 0.016730296647358260...%.
```

Both round to **0.02%** at two decimal places. The paper's wording that the
counts represent 0.02% of samples in each dataset is therefore consistent with
ordinary printed rounding. Conversely, treating 0.02% as exact would imply
72,973.7784 train and 72.9216 validation samples, but that reverse calculation
is not a valid objection to a rounded printed percentage.

### 5.2 C4 NEARDUP anchors — consistent

Table 13's implied fractional reduction is

```text
100 * (364.87 - 350.48) / 364.87
  = 3.9438704196015019...%,
```

which rounds to Appendix D's **3.9% smaller**. Appendix C's 152K and 146K
steps at batch size 4,800 over two epochs correspond to
`152,000*4,800/2 = 364,800,000` and `146,000*4,800/2 = 350,400,000` examples,
consistent with its approximate 365M/350M descriptions and Table 13's rounded
364.87M/350.48M. Section 5.1's 3.04% is a train-with-train duplication
statistic, not a removal percentage; those bases must not be equated. The
separate ceiling contradiction in §1 remains.

**Verdict: consistent** for the NEARDUP size, step, and 3.9% supporting anchors.

### 5.3 C4 EXACTSUBSTR anchors — contradiction, cause not established

Table 13 prints C4 EXACTSUBSTR at **350.48M**, identical to NEARDUP, implying
`364.87M - 350.48M = 14.39M` fewer examples than ORIGINAL. Appendix C instead
groups C4-ORIGINAL and C4-EXACTSUBSTR at approximately **365M examples**, with
the same **152K steps** and batch size 4,800. Section 5.1 explicitly says
EXACTSUBSTR does not remove examples outright, while removing substrings and
reporting 77% overlap with NEARDUP-removed C4 train examples. Appendix E
reiterates that, for datasets already exactly deduplicated at creation,
EXACTSUBSTR does not remove examples outright.

The repeated 350.48M cell is compatible with a transcription/copy hypothesis,
but the printed evidence does not establish that explanation or identify the
correct replacement value.

**Verdict: contradiction** between Table 13's C4 EXACTSUBSTR example count and
the appendix description. No established copy error is asserted.
