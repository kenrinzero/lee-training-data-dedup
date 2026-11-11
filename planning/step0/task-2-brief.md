# Task 2 — independent printed arithmetic

Project: Lee et al. (2022) duplication-statistics audit, Step 0. This task derives internal-consistency results from the printed oracle. Do not read the historical seed and do not download cluster data or compute cluster-derived estimates.

Read `task-1-report.md`, `../../paper/targets/README.md`, `../../paper/targets/printed-targets.csv`, `../../paper/targets/figure-bars.csv`, and source-native PDF pages as needed. Those printed values, not the seed, are your premises.

## Required work

Write `planning/step0/arithmetic.md` with formulas, exact arithmetic, assumptions, and verdicts for:

1. **C4 removal ceiling.** From Table 2's train-with-train percentage and train/validation sizes, derive the maximum removals compatible with NEARDUP keep-one semantics, then compare with Table 13's implied removal range. Explain the assumption that a removed train document has a duplicate in train or validation, and distinguish an internal contradiction from a release/convention mismatch.
2. **Fig. 1 bounds.** From the printed bars derive singletons, multi-cluster documents, plotted clusters, the keep-one removal upper bound and its percentage. Explain the effect of omitted exact edge sizes and derive the lower-bin-edge document share if possible.
3. **Random-split identities.** Derive the expected evaluation-with-train and evaluation-with-evaluation duplication probabilities for a randomly split cluster of size s, including finite-population formulas. State precisely when the all-document multi-cluster share is an approximation and what extra information the exact validation-with-validation expectation needs. Do not substitute an unobserved cluster-size distribution.
4. **LM1B printed-only floor.** Using Fig. 8(a), derive the multi-cluster document count, plotted lower-edge count, maximum omitted edge-size cluster count, and the minimum removals after accounting for validation documents and plotted multi-doc clusters. Compare with Table 13's implied removal range. Check every premise against the target CSV.
5. **Supporting arithmetic.** Recompute the 61,036/61 sentences as percentages of their respective C4 split sizes; compare Table 13's C4 NEARDUP/EXACTSUBSTR cells with Appendix C and §5.1 without asserting an established copy error.

Also write `planning/step0/arithmetic.json` containing each named derivation's premises, formula strings, exact or sufficiently precise numerical outputs, and verdict (`contradiction`, `consistent`, or `indeterminate`). Use Python stdlib exact arithmetic where useful, but do not create a general analysis package. Include a self-review and command summary in `planning/step0/task-2-report.md`.

Use UTF-8/LF. Do not edit PREREGISTRATION.md, CLAIM_INVENTORY.md, or Task 1's target files. Do not dispatch subagents.
