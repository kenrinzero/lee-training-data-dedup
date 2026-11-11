# Step 0 Task 2 report — independent printed arithmetic

## Outcome

Completed all five required derivation areas in `arithmetic.md` and recorded
seven named derivations with premises, formulas, outputs, assumptions, and
verdicts in `arithmetic.json`.

Headline results:

- **C4 removal ceiling: contradiction.** The nominal ceiling is
  11,456,622.3168 removals. Allowing Table 2's full rounding interval raises
  its strict upper boundary only to 11,474,865.7614, still below Table 13's
  rounding-compatible minimum of 14.38M by 2,905,134.2386 examples.
- **Figure 1: consistent interval.** The bars give 348,320,475 singletons,
  2,502,048 plotted multi-document clusters, a 10,868,122 lower-edge
  multi-document count, and a whole-population keep-one lower count of
  8,366,074. Subtracting all 364,608 validation examples gives conditional
  train-removal bounds 8,001,466–14,410,977. Table 13's interval fits. Exact
  shares remain indeterminate because of omitted edges and within-bin sizes.
- **Random splits: formulas exact, C4 numerical expectation indeterminate.**
  Independent and finite-population ET/EE/TT identities are recorded. Exact
  validation-with-validation expectation requires the full cluster-size
  histogram, which the printed bars do not provide.
- **LM1B floor: contradiction.** Figure 8(a) gives 687,845 plotted
  multi-document clusters, 1,505,410 lower-edge multi-cluster documents,
  30,602,237 lower-edge documents overall, and at most 547 omitted edge-size
  clusters. After charging all 306,688 held-out sentences against the plotted
  keep-one bound, the train-removal floor is 510,877, exceeding Table 13's
  largest rounding-compatible value by 70,877.
- **Supporting arithmetic.** Both repeated-sentence percentages round to
  0.02%. C4 NEARDUP agrees with the appendix's 3.9% and step/size anchors. C4
  EXACTSUBSTR is internally inconsistent with Appendix C and the
  no-outright-removal method text; no copy error is asserted.

## Public metadata pinned independently

Access date for all public records: **2026-11-08**. Access was metadata/API
only; no dataset content or cluster archive was downloaded.

- C4 `en`: **364,868,892 train**, **364,608 validation**, from Hugging Face
  `legacy-datasets/c4` revision
  `21e98d7063e4037e836a0299d7fbb7efd484e6c3`:
  - https://huggingface.co/datasets/legacy-datasets/c4/raw/21e98d7063e4037e836a0299d7fbb7efd484e6c3/README.md
  - https://huggingface.co/api/datasets/legacy-datasets/c4
- LM1B `plain_text`: **30,301,028 train**, **306,688 test**, from Hugging Face
  `billion-word-benchmark/lm1b` revision
  `35161838ea9e05371a25a8db037f94fcae4c2064`:
  - https://huggingface.co/datasets/billion-word-benchmark/lm1b/raw/35161838ea9e05371a25a8db037f94fcae4c2064/README.md
  - https://huggingface.co/api/datasets/billion-word-benchmark/lm1b
  - https://huggingface.co/datasets/billion-word-benchmark/lm1b/raw/35161838ea9e05371a25a8db037f94fcae4c2064/lm1b.py

LM1B has a public held-out `test` split, not a public `validation` split. The
arithmetic explicitly maps the paper's evaluation terminology to `test`; without
that convention, the validation-adjusted numerical verdict is indeterminate.
The historical seed was not read and no remembered count was used as an
unsupported premise.

## Command and verification summary

Source inspection used `pdftotext -layout` on PDF pages 1, 5, 15, 17–18, and
21–22. Public split metadata was retrieved with read-only URL fetches from the
exact records above. All computation used Python 3 standard library with
`python -B`; no analysis package or persistent verification script was created.

The final numerical/source validation recomputed the derivations from the CSVs
and JSON rather than checking only imports or JSON syntax. It asserted:

- exactly 193 unique scalar targets and 44 figure bars;
- all 25 printed scalar premises used in JSON against `printed-targets.csv` by
  exact decimal value;
- every Figure 1 and Figure 8(a) label/count against both CSVs, including all
  11 LM1B scalar-ledger rows;
- exact `Fraction` values for the C4 ceiling and robust gap;
- every Figure 1 and LM1B count, bound, omitted-edge allowance, and percentage;
- both repeated-sentence percentages and the appendix arithmetic; and
- all seven derivation IDs and their allowed verdict values.

Final numerical/source output:

```text
PASS: 193-row/44-bar oracle; 25 JSON scalar premises and all 22 used bars match source CSVs.
PASS: C4 ceiling exact fractions and strict rounded-interval contradiction.
PASS: Figure 1 lower/upper bounds and percentages independently recomputed.
PASS: every LM1B numerical output and strict Table 13 floor contradiction.
PASS: repeated-sentence percentages, NEARDUP anchors, and EXACTSUBSTR implied removal arithmetic.
```

A separate exact enumeration checked every ET/EE/TT case for `N=2..8`, every
nonempty proper evaluation split, every cluster size `s=1..N`, and all 504
resulting cases:

```text
PASS: 504 finite-population ET/EE/TT cases verified exactly by exhaustive split enumeration.
PASS UTF-8/LF: planning/step0/arithmetic.md
PASS UTF-8/LF: planning/step0/arithmetic.json
PASS: arithmetic.json parses after final wording edit.
```

Two overlong inline verification commands were truncated by the command
transport before completing. A shortened run then reached an enumeration
assertion; diagnosis showed that its train-target test branch had used the
evaluation subset rather than its complement. The corrected independent
enumeration used exact rational comparisons and passed all 504 cases. These
were temporary harness errors; no deliverable number was changed in response.

## Self-review against the brief

| Requirement | Result |
|---|---|
| C4 removal ceiling and assumption/internal-versus-release distinction | Done, with nominal and rounding-aware bounds and a conditional contradiction verdict. |
| Figure 1 singletons, multi-documents, clusters, keep-one bound/percentage, omitted edges, lower-edge share | Done, with the whole-population lower count distinguished from the validation-adjusted train-removal floor and upper bound. |
| Independent and finite-population random-split identities | Done; train-side identity also included, with document-weighted expectations. |
| Precise multi-cluster-share approximation and exact VV information need | Done; no unobserved distribution substituted; numerical VV verdict indeterminate. |
| LM1B multi-document/lower-edge counts, maximum omitted clusters, validation-adjusted floor, Table 13 comparison | Done; every bar and scalar premise checked against Task 1's CSVs. |
| 61,036/61 percentages | Done; both round to 0.02%. |
| C4 NEARDUP/EXACTSUBSTR versus Appendix C and §5.1 | Done; NEARDUP consistent, EXACTSUBSTR contradictory without declaring a copy error. |
| JSON premises, formulas, numerical outputs, and verdicts | Done for seven named derivations. |
| Exact public metadata, URLs, and access dates | Done in both arithmetic outputs and this report. |
| Protect Task 1 files, inventory, and preregistration | None edited. |
| No historical seed, cluster archive/full dataset, or cluster-derived estimate | Confirmed. Metadata/API and PDF text inspection only. |
| UTF-8/LF and non-Git workspace | Arithmetic outputs verified; report checked in the final integrity pass. No repository initialized or commit made. |
| No subagent | None dispatched. Scientific/reader Type-B review remains independent future work. |

## Remaining qualifications

1. Figure split coverage is not printed. Figure 1 and LM1B total-based bounds
   explicitly assume the pinned public train-plus-evaluation population.
2. LM1B's public `test` split is used as the evaluation split by explicit
   convention, not renamed in the source record.
3. The exact C4 validation-with-validation expectation remains indeterminate
   without the cluster-size histogram.
4. This is a self-reviewed Type-A arithmetic/source check, not independent
   Type-B scientific or reader approval.


---

## Review fix report — Figure 1 train-removal lower bound (2026-11-08)

The independent review correctly identified that `D_multi - C_multi` over the
combined train-plus-validation population is a whole-population keep-one count,
not directly a train-removal lower bound. The Figure 1 formulas, narrative,
JSON output names/values, headline result, and self-review wording now distinguish:

```text
whole-population keep-one lower count = 8,366,074,
conservative train-removal floor      = 8,366,074 - 364,608
                                      = 8,001,466,
train-removal upper bound             = 14,410,977 (unchanged).
```

The corrected lower percentage is 2.192970180642311...% of train. Table 13
remains inside the corrected train-removal interval, so the `consistent`
verdict is unchanged.

### Targeted exact recomputation

Command run from the member root:

```bash
python -B - <<'PY'
from fractions import Fraction
whole = 10868122 - 2502048
validation = 364608
train = 364868892
train_floor = whole - validation
pct = 100 * Fraction(train_floor, train)
print('whole_population_keep_one_lower =', whole)
print('train_removal_lower =', train_floor)
print('train_removal_lower_percent_fraction =', pct)
print('train_removal_lower_percent_decimal =', format(float(pct), '.15f'))
assert whole == 8366074
assert train_floor == 8001466
assert pct == Fraction(200036650, 91217223)
assert format(float(pct), '.15f') == '2.192970180642311'
assert 8001466 < 14380000 < 14400000 < 14410977
print('PASS: corrected Figure 1 train floor and Table 13 interval membership.')
PY
```

Output:

```text
whole_population_keep_one_lower = 8366074
train_removal_lower = 8001466
train_removal_lower_percent_fraction = 200036650/91217223
train_removal_lower_percent_decimal = 2.192970180642311
PASS: corrected Figure 1 train floor and Table 13 interval membership.
```

### Covering numerical regression

Two `python -B` standard-library commands were then run from the member root.
The first loaded `arithmetic.json` and both Task 1 CSVs; checked all 193 scalar
rows, 44 bars, 25 JSON scalar premises, and all 22 used figure bars; recomputed
the C4 ceiling, every Figure 1 bound and percentage, every LM1B output, and the
supporting arithmetic; and asserted that the stale train-floor percentage and
JSON key were absent. The second repeated the exact finite-population
enumeration. Outputs:

```text
PASS: 193 scalars, 44 bars, 25 JSON scalar premises, and all 22 used bars match Task 1 CSVs.
PASS: C4 ceiling and rounding-aware contradiction recomputed exactly.
PASS: Figure 1 whole=8366074, train floor=8001466, percent=2.192970180642311, upper=14410977; Table 13 remains inside.
PASS: every LM1B count, omitted-edge allowance, and removal-floor comparison recomputed.
PASS: repeated-sentence percentages and C4 appendix arithmetic recomputed.
PASS: stale Figure 1 train-floor values and JSON keys absent.
PASS: 504 finite-population ET/EE/TT cases verified exactly.
```

No Task 1 target file, `PREREGISTRATION.md`, or `CLAIM_INVENTORY.md` was edited,
and no subagent was dispatched.
