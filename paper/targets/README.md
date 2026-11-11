# Printed target oracle — Lee et al. (2022)

This directory maps the current C1–C7 claim inventory to the preserved 22-page
PDF at `paper/paper.pdf`. The ACL PDF is the numerical source of record. The
historical seed was used only as a checklist of targets, never as a numerical
oracle. No cluster archive was opened and no cluster-derived estimate was
computed.

PDF page numbers and the page numbers printed at the bottom of this article are
identical (1–22). `printed-targets.csv` contains the scalar ledger;
`figure-bars.csv` contains the specialized figure transcription. Figure scalars
are repeated in both CSV files so the main ledger is complete. Values are not
silently converted to exact counts: for example, Table 13's `364.87M` remains
`364.87` in unit `million examples`.

`UNRESOLVED` is a sentinel, not a printed value. It is used for exact public
split sizes required by later arithmetic but absent from the PDF, and for Table
11's absent twentieth-row total and fraction. `NA` in the page field accompanies
the split-size sentinels; the absent Table 11 cells retain page 21 as their
source locator. No figure bar was unreadable.

## Claim-to-source locator map

| Claim | Source-native locator(s) | Printed targets and scope |
|---|---|---|
| C1 | PDF p. 5, Table 2, C4 row; p. 5, §5.1; p. 6, §5.3 | C4 train-with-train **3.04%**, validation-with-validation **1.59%**, validation-with-train **4.60%**. Section 5.1 repeats the train range endpoint 3.04%; §5.3 rounds validation-with-train to **4.6%**. |
| C2 | PDF p. 21, Table 13, C4 row; p. 15, Appendices C and D; p. 16, Table 6 | C4 original/NEARDUP examples **364.87M/350.48M**; tokens **177.3B/173.7B**. Appendix C gives approximately **365M/350M examples**, **152K/146K steps**, **131/126 hours**, and **5.5 days** for original. Appendix D gives **3.9% smaller**, **63 hours/epoch**, and around **5 hours** saved over two epochs. Table 6 gives **5.47/5.26 days** and **16804.70/16149.31 TPU hours** for XL-ORIGINAL/XL-NEARDUP. |
| C3 | PDF p. 5, Figure 1 and §5.1; p. 21, Table 11, C4 column | All 11 C4 group-count bars; **1.8M** pair clusters, **280** clusters over **5,000** examples, largest cluster **250,933** examples; all 19 printed C4 URL rows and their `# Total`/`Frac Dups` cells. The promised twentieth C4 URL is absent; its total and fraction have structured `UNRESOLVED` rows. |
| C4 | PDF p. 5, Table 2, Wiki40B row; p. 21, Table 13, Wiki40B row; p. 22, Figure 8 bottom panel | Wiki-40B Table 2 cells **0.39% / 0.26% / 0.72%**; Table 13 original/NEARDUP examples **2.93M/2.91M**, tokens **2.25B/2.24B**; all 11 bottom-panel bars. The PDF labels the split `valid`, not `test`; no split-substitution conclusion is made here. |
| C5 | PDF p. 5, Table 2, RealNews row; p. 21, Table 13, Real News row and Table 11 RealNews column; p. 22, Figure 8 middle panel | RealNews Table 2 cells **13.63% / 1.25% / 14.35%**; original/NEARDUP examples **31.16M/28.39M**, tokens **24.7B/22.4B**; all 19 URL rows and all 11 middle-panel bars. Section 5.3 rounds validation-with-train to **14.4%**. |
| C6 | PDF p. 1, §1; p. 3, §3; p. 5, Table 2 and §5.1; p. 15, Appendices C/D; p. 16, Table 6; p. 18, Appendix E continuation; p. 21, Table 13; p. 22, Figure 8 top panel | Printed-only C4/LM1B arithmetic premises, including all LM1B Table 2 and Table 13 cells and all 11 top-panel bars. The §1 consistency inputs are **61,036** train occurrences, **61** validation occurrences, and **0.02%** wording. Exact public C4 train/validation and LM1B train/validation sizes are **not printed** and are marked `UNRESOLVED`; §3's LM1B **30M** and Table 13's rounded **30.30M** are not exact public train-split counts. |
| C7 | PDF p. 5, Figure 1; p. 22, Figure 8; the C4 percentage sources listed under C1/C2/C6 | Visual transcription target: exact bin labels, bar labels, omitted edge sizes, corpus order, and units. The alternative-percentage ledger must preserve the bases of **3.04%**, Table 13's rounded example sizes, **3.9%**, and Figure 1 bars. The external publication-page value **1.68%** is not printed in this PDF and is not added as a PDF target. |

No deferred memorization or standalone EXACTSUBSTR reproduction targets are
added. EXACTSUBSTR cells retained in the ledger are only printed context for
C2/C4/C5/C6's existing internal-consistency checks.

## Table 2 — exact printed cells

Unit is **percent of examples**, not tokens. Columns follow the printed headers.

| Corpus (printed row) | `% train examples with dup in train` | `% valid with dup in valid` | `% valid with dup in train` |
|---|---:|---:|---:|
| C4 | 3.04% | 1.59% | 4.60% |
| RealNews | 13.63% | 1.25% | 14.35% |
| LM1B | 4.86% | 0.07% | 4.92% |
| Wiki40B | 0.39% | 0.26% | 0.72% |

Locator: PDF p. 5, Table 2. The caption calls these fractions while the cells
are printed with percent signs. The CSV therefore stores numeric values with
unit `%`.

## Table 13 — exact printed cells

Locator: PDF p. 21, Table 13. Token values use the paper's **50k BPE
vocabulary** and unit **billion BPE tokens**. Example values use unit **million
examples**. All are train-set sizes and retain printed rounding.

| Corpus (printed row) | ORIGINAL tokens | NEARDUP tokens | EXACTSUBSTR tokens | ORIGINAL examples | NEARDUP examples | EXACTSUBSTR examples |
|---|---:|---:|---:|---:|---:|---:|
| C4 | 177.3B | 173.7B | 165.4B | 364.87M | 350.48M | 350.48M |
| Real News | 24.7B | 22.4B | 20.1B | 31.16M | 28.39M | 28.39M |
| LM1B | 1.0B | 0.94B | 0.90B | 30.30M | 29.87M | 30.16M |
| Wiki40B | 2.25B | 2.24B | 2.19B | 2.93M | 2.91M | 2.93M |

Section 3 on PDF p. 3 instead gives coarse full-dataset descriptions: C4
**360M web documents**, RealNews **31M documents**, LM1B **30M sentences**, and
English Wiki-40B **2.9M Wikipedia pages**. These are separate printed
approximations, not interchangeable exact split sizes.

## Figure transcription and omitted sizes

The 11 bins in each panel, indexed bottom-to-top in the CSV, are:

`1`, `2`, `3`, `4`, `5`, `[6, 10)`, `[11, 20)`, `[21, 50)`, `[51, 500)`,
`[501, 5000)`, `[5001, ∞)`.

Every bar value is a **number of groups**, as labelled on the horizontal axis;
it is not a document count. The figures do not state a split in their captions
or axes, so `split_or_arm` is `not stated` in the scalar ledger.

| Figure/panel | Corpus legend | Printed bar labels in bin-index order 1 through 11 |
|---|---|---|
| Figure 1, p. 5 | C4 | 348,320,475 / 1,861,744 / 292,575 / 109,853 / 54,984 / 85,567 / 42,723 / 28,446 / 23,094 / 2,782 / 280 |
| Figure 8 top, p. 22 | LM1B | 29,096,827 / 595,632 / 68,775 / 15,825 / 4,432 / 2,762 / 340 / 66 / 13 / 0 / 0 |
| Figure 8 middle, p. 22 | Real News | 27,917,044 / 1,715,379 / 231,913 / 89,017 / 34,487 / 24,889 / 1,150 / 243 / 129 / 11 / 0 |
| Figure 8 bottom, p. 22 | Wiki40B | 3,228,888 / 3,557 / 833 / 399 / 245 / 391 / 163 / 60 / 24 / 1 / 0 |

The printed half-open ranges **omit exact cluster sizes 10, 20, 50, 500, and
5000** in both Figure 1 and every Figure 8 panel. This conclusion follows from
the labels alone; it is not a cluster-derived estimate. Zero is a printed bar
label where shown, not an unresolved value.

Figure 8 actually contains **three unlettered panels**, in top-to-bottom order
LM1B, Real News, Wiki40B. The names Figure 8(a), 8(b), and 8(c) in the CSV are
reading-order conventions for the existing claim inventory; they are not
printed panel letters. There is no fourth Figure 8 panel and no Figure 8(d)
target. C4 is separately shown in Figure 1.

## Table 11 — URL rows

Locator: PDF p. 21, Table 11. `# Total` is a count of examples. `Frac Dups` is
a **ratio**, not a percentage. The table filters the left side to URLs that
occur at least 10 times. The following transcription corrects the column
misalignment produced by `pdftotext -layout`; rendered-page inspection was used
for these values.

| RealNews URL | # Total | Frac Dups | C4 URL | # Total | Frac Dups |
|---|---:|---:|---|---:|---:|
| medicalnewstoday.com. | 12 | 1.00 | hairtechkearney.com | 4883 | 1 |
| dodbuzz.com | 301 | 0.99 | keywordsking.com | 1786 | 1 |
| undertheradar.military.com | 187 | 0.97 | sydneysitalianfruitshops.online | 1178 | 1 |
| q.usatoday.com | 33 | 0.94 | moewiki.usamimi.info | 1001 | 1 |
| ad-test.thirdage.com | 354 | 0.94 | swarovskijewelryoutlet.org | 984 | 1 |
| amp.nymag.com | 15 | 0.93 | forzadurto.org | 980 | 1 |
| citizenwire.com | 1022 | 0.93 | producerati.com | 971 | 1 |
| paycheck-chronicles.military.com | 363 | 0.92 | sourceryforge.org | 908 | 1 |
| product-reviews.net | 73403 | 0.92 | heavenz-kitchen.com | 876 | 1 |
| kitup.military.com | 196 | 0.92 | little-eclipse.com | 822 | 1 |
| gcaptain.com | 33903 | 0.92 | walops.com | 819 | 1 |
| dev.screenrant.com | 70 | 0.91 | 16thstlaunderland.com | 713 | 1 |
| live.swissinfo.ch | 66 | 0.91 | theroyalstarinfo.com | 696 | 1 |
| news.theepochtimes.com | 82 | 0.87 | code4kt.com | 684 | 1 |
| opinion.toledoblade.com | 986 | 0.87 | nflfalconsjerseys.us | 682 | 1 |
| cdn.moneytalksnews.com | 121 | 0.86 | quiltingbeeshop.com | 676 | 1 |
| amp.fox23.com | 14 | 0.86 | ulifeinsurancemiami.com | 675 | 1 |
| sales.rollingstone.com | 20 | 0.85 | wowkeyword.com | 673 | 1 |
| ftp.screenrant.com | 20 | 0.85 | taspetro.com | 671 | 1 |

The caption says the right side shows the **20 most frequent URLs** in C4, but
only **19 C4 rows** are printed. The twentieth URL and its values are
unresolved; none has been inferred. The scalar ledger contains explicit
`table11-c4-r20-total` and `table11-c4-r20-frac` rows with `UNRESOLVED` values
and units `examples` and `ratio`, respectively.

## Appendix timing and size anchors

All locators and printed units are represented independently in
`printed-targets.csv`:

- **Appendix C, PDF p. 15:** C4-ORIGINAL and C4-EXACTSUBSTR each approximately
  **365M examples**, **152K steps**, batch size **4800 examples**, and
  approximately **131 hours (5.5 days)**; C4-NEARDUP approximately **350M
  examples**, **146K steps**, and approximately **126 hours**. Each model was
  trained for **2 epochs**.
- **Appendix D, PDF p. 15:** approximately **131 hours or 5.5 days** on a
  128-core TPU v3; deduplicated dataset **3.9% smaller**; **63 hours/epoch**;
  around **5 hours** saved for two epochs.
- **Table 6, PDF p. 16:** XL-ORIGINAL **5.47 days** and **16804.70 TPU hrs**;
  XL-NEARDUP **5.26 days** and **16149.31 TPU hrs**.
- **Section 5.1, PDF p. 5:** majority **1.8M clusters** consisting of a single
  pair, **280 clusters** with over **5,000 examples**, one cluster of size
  **250,933 examples**, and **77%** of NEARDUP-removed C4 training examples
  having a verbatim length-50 match. The seed's shorthand “1.8M pairs” is thus
  less precise than the printed unit, which is clusters.

## Source discrepancies and limits

1. **Exact split sizes absent.** The PDF does not print exact public C4 train,
   C4 validation, LM1B train, or LM1B validation counts. The corresponding four
   ledger rows are `UNRESOLVED`. In particular, LM1B §3's coarse **30M** and
   Table 13's rounded **30.30M** are not the exact public train-split count
   needed for arithmetic. Later arithmetic must pin a separate public split
   source rather than treating the seed's `364,868,892`, `364,608`, `30,301,028`,
   or `306,688` as PDF facts.
2. **Table 11 row-count mismatch.** Nineteen C4 URL rows are visible although
   the caption promises 20. The missing row remains unresolved; its total and
   fraction are explicit `UNRESOLVED` entries in the scalar ledger.
3. **Figure panel naming.** Figure 8 has three unlettered panels, not four
   lettered panels. CSV panel letters are explicit reading-order conventions.
4. **Corpus spelling varies.** `RealNews` appears in Table 2 and Table 11,
   while `Real News` appears in Table 13 and Figure 8. The source prints
   `Wiki40B`; `Wiki-40B` is the normalized CSV corpus name.
5. **Size precision varies.** Section 3's 360M/31M/30M/2.9M descriptions,
   Appendix C's approximately 365M/350M, and Table 13's two-decimal M values
   have different bases or rounding and must not be silently equated with exact
   public split sizes.
6. **Prose rounding varies.** Section 5.3 on p. 6 prints C4 **4.6%** and
   RealNews **14.4%**, whereas Table 2 prints **4.60%** and **14.35%**.
7. **C4 EXACTSUBSTR size tension.** Table 13 repeats **350.48M** for C4
   NEARDUP and EXACTSUBSTR, but Appendix C groups C4-ORIGINAL and
   C4-EXACTSUBSTR at approximately **365M examples**. Appendix E's dataset-size
   prose concludes on p. 18 that EXACTSUBSTR does not actually remove examples
   for already exactly deduplicated datasets. This is recorded as a source
   consistency issue, not declared a copy error. LM1B's distinct **30.16M**
   EXACTSUBSTR cell remains visible.
8. **Table extraction is not authoritative for layout.** Layout text
   misassigns several Table 11 totals and interleaves Table 13 rows. The CSV
   follows rendered-page inspection, not extraction order.
9. **Rights notice absent.** No paper licence, copyright notice, or Creative
   Commons statement is printed in the preserved 22-page PDF. See
   `paper/PROVENANCE.md`; absence of a notice is not a determination that the
   work is unrestricted.

## CSV conventions

- `printed-targets.csv` header:
  `target_id,claim_id,page,locator,corpus,quantity,split_or_arm,printed_value,unit,notes`.
- `figure-bars.csv` header:
  `figure,page,corpus,bin_index,bin_label,printed_count,notes`.
- Printed counts are integer strings without thousands separators in CSV;
  README tables retain the printed comma formatting for readability.
- Ratios and percentages are distinct units. Days, hours, hours/epoch, steps,
  examples, groups, tokens, and TPU hours are not merged into a common unit.
- No derived removals, totals, ratios, or cluster estimates are included as
  printed values. Step 0 Task 2 must derive those separately from this oracle.
