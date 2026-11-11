# SDD ledger — plan: PREREGISTRATION.md §8 + Amendment A1

Run-004 supersedes run-003. Run-003 completed finalization and all 1,024 custody checks, but full verification stopped on relative links that resolved inside run-003/run-002 instead of the actual run-002. No numerical or custody mismatch occurred.
Correction: acquisition, source-metadata and work-store links are absolute local paths; all three Important review fixes and three deferred Minor dispositions are carried unchanged from run-003/progress.md.
Final: fixed C1/C2 companion coverage — `test_companion_dispositions` RED→GREEN; §5.3 rounding, independent printed-difference interval, token non-executability and Step-0 links are present.
Final: fixed Table 11 interpretation — exact full-URL outputs retained; report explicitly says they do not reproduce the host-level estimand or establish 19 substantive contradictions; ranking condensed.
Final: fixed train custody — `test_receipt_set_matches_metadata_lfs` RED→GREEN; acquisition enforces LFS digests and final verification checks every path, byte, digest and aggregate row count plus manifest/metadata hashes.
Final: minor (deferred): printed-total lookup is restricted to URLs with keep=0, with zero effect because all 19 printed strings have zero full-table occurrences.
Final: minor (deferred): random-split display precision, rounded pair value, exact edge table and related reader polish.
Final: minor (deferred): report verifier substring checks can be strengthened into structured rendered-row comparisons.
Final verification: 13/13 contract fixtures PASS; all 1,024 shard receipts match LFS metadata (326,778,635,540 bytes, 364,868,892 rows); identity/full numerical/custody/report verifiers PASS; final run-004 output and code receipts verified without modification.
Final: Ruling: run-004 is the final candidate — run-001 was invalid, run-002 established the numerical evidence, run-003 was a link-path correction, and run-004 carries all Important review fixes — cost if wrong: earlier evidence remains immutable for audit and no result is overwritten.
