# Task 3 — revised Step-0 contract candidate

Project: Lee et al. (2022) duplication-statistics audit. Tasks 1 and 2 are complete and independently approved. Produce a review-ready contract, but do not freeze it yet.

Read `../../AGENTS.md`, `../../SCOPE.md`, the current `../../PREREGISTRATION.md` and `../../CLAIM_INVENTORY.md`, plus Task 1/2 reports and their approved artifacts. The historical seed may now be read only to label prior exposure; approved Task 1/2 artifacts are the numerical authority. Do not download cluster archives or full datasets and do not compute cluster-derived estimates.

## Required source metadata

Without downloading dataset content, independently pin the public Wiki-40B dataset revision and exact train/validation/test counts needed for Stage 1, and the authors' deduplicate-text-datasets repository commit and licence/rights statements. Record exact URLs and access date. Check cluster archive availability with metadata/HEAD/range requests only, not archive downloads. Preserve Task 2's pinned C4 and LM1B metadata. If a fact cannot be sourced, mark it unresolved with a gate rather than importing it from the seed.

## Required edits

1. Rewrite `PREREGISTRATION.md` as `DRAFT v1 CANDIDATE — NOT FROZEN`, complete enough for independent review. Preserve the authorized Stages 1–3 and 7 boundary and exposed-versus-prospective ledger.
2. Update `CLAIM_INVENTORY.md` to final source-native locators and explicit computability limits. RealNews Table 2 split cells and other targets lacking necessary inputs must not be presented as executable released-cluster checks.
3. Write `STEP0_DERIVATIONS.md` summarizing the approved printed oracle, public metadata, formulas, corrected bounds, internal-consistency findings, assumptions, and checklist lenses. Distinguish Step-0 findings from future cluster tests.
4. Update `data/raw/MANIFEST.md` with the pinned planned sources and acquisition gates, but leave every archive/input unacquired.
5. Write `planning/step0/task-3-report.md` with decisions, unresolved items, verification and self-review.

## Contract rules that must be deterministic

- Define train-with-train, evaluation-with-evaluation and evaluation-with-train by cluster membership, not merely by the CSV `keep` flag. Stage 1 must test the seed's exposed `keep=1 singleton / keep=0 multi-document` lead before applying it to C4.
- Pin exact split versions and denominators. Evaluate Wiki-40B validation and test separately; figures use all released rows, with the split population named. Do not relabel the paper's `valid` before results.
- Removal rule A (evaluation-preferred): for each cluster, if any evaluation document exists, retain one evaluation copy and remove every train member; otherwise retain one train copy and remove the other train members. Removal rule B (uniform train keep-one): remove `max(0, n_train − 1)` train documents from every cluster. Also report remove-every-train-member sensitivity. Define treatment of validation-only/test-only clusters and clusters spanning splits.
- Figure candidates assign exact edge sizes 10/20/50/500/5000 low, high, or dropped. The primary convention is the unique one reproducing all 11 Wiki-40B labels. If zero or multiple conventions match, report ambiguity and retain all candidates; never choose by desired C4 outcome. Stage 2's release-identity test requires physical C4 rows = 365,233,500 and at least one predeclared convention reproducing all 11 C4 labels. Duplicate URLs are measured and reported, not an unspecified exemption.
- Printed percentages match by ROUND_HALF_UP to their printed precision; counts/bars match exactly. Table 13 comparisons use the exact public original size and the printed rounding intervals. Any tolerance exception must be explicit and justified.
- Stage 2 computes the exact C4 validation-with-validation random-split expectation from the full cluster-size histogram before comparing with 1.59%. Printed aggregates alone leave it indeterminate.
- Incorporate Task 2's corrected Figure 1 train floor 8,001,466 and upper bound 14,410,977, the C4 robust ceiling gap 2,905,134.2386, and the conditional LM1B floor 510,877. Do not revive the corrected lower-bound error or the seed's different numbers without a new derivation.
- Define verdicts for every included printed cell, the §5.1 approximate 1.8M pair-cluster statement, 280/largest 250,933, Table 11's 19 printed rows plus missing twentieth, RealNews removal ceiling, and the release-identity kill branch. Exposed pilot bands are reproduction targets, not novel predictions.
- Stage outputs remain immutable, source hashes precede each run, C4 streams unextracted, and no post-result convention can silently become faithful.

Use UTF-8/LF. Do not create a freeze receipt yet, do not run analysis, and do not dispatch subagents.
