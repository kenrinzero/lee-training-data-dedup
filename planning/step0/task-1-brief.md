# Task 1 — source-native targets and locators

Project: Lee et al. (2022) duplication-statistics audit, Step 0. This task creates the printed oracle only. Do not download cluster data or compute cluster-derived estimates.

Read `../../AGENTS.md`, `../../SCOPE.md`, and `../../CLAIM_INVENTORY.md` for context, but the requirements below are authoritative. The source of record is `../../paper/paper.pdf` (ACL Anthology, 22 pages). Use `pdftotext -layout`, `pdfinfo`, and page rendering/inspection where needed. Do not treat the historical seed or study-unit Markdown as the numerical oracle.

## Required work

1. Inspect the PDF's title/byline, rights notice, and all source-native pages containing the included claims: Table 2, Table 11, Table 13, Fig. 1, Fig. 8, §5.1, Appendix C/D, and the LM1B material needed for printed-only arithmetic.
2. Produce `paper/targets/README.md` with a complete locator map for claim IDs C1–C7, exact printed values and units, and any source discrepancies. Map every seed target in the current claim inventory; do not add deferred memorization or EXACTSUBSTR targets.
3. Produce `paper/targets/printed-targets.csv` with header `target_id,claim_id,page,locator,corpus,quantity,split_or_arm,printed_value,unit,notes`. Include every scalar needed for C1–C6, including C4 train/validation sizes, Wiki-40B sizes if printed, RealNews Table 13 values, appendix timing/size anchors, and LM1B Fig. 8/Table 13 inputs. Preserve printed precision and distinguish counts, percentages, days/hours/steps and ratios.
4. Produce `paper/targets/figure-bars.csv` with header `figure,page,corpus,bin_index,bin_label,printed_count,notes`. Transcribe all 11 bars for each of Fig. 1 (C4) and Fig. 8(a–d) (LM1B, RealNews, Wiki-40B), using the printed bin labels and bar labels. If any bar is unreadable, mark it unresolved rather than guessing.
5. Record whether Fig. 1/Fig. 8 labels omit exact cluster sizes 10, 20, 50, 500 and 5000, and whether the PDF states a licence. Update `paper/PROVENANCE.md` only with inspected source facts and rights; do not change its custody/hash history.
6. Write a self-review and command/evidence summary to `planning/step0/task-1-report.md`. List every output, any unresolved locator/value, and confirm that no cluster archive was downloaded and no cluster estimate ran.

Use UTF-8/LF. Do not edit PREREGISTRATION.md or CLAIM_INVENTORY.md in this task. Do not dispatch subagents.
