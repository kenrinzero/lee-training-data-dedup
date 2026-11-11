# SDD ledger — plan: PREREGISTRATION.md §7 (FROZEN v1)

Run-004 supersedes run-003 after fresh-context review. The numerical findings were independently reproduced without defect; this run adds the two required execution controls.
Final: fixed comparison overwrite path — `test_comparison_refuses_existing_outputs` RED→GREEN; fresh comparison directories are required for all verdict, lock, report, and manifest outputs.
Final: fixed pre-run source identity — `test_receipt_rejects_same_length_hash_change` RED→GREEN; all 24 expected SHA-256 values are pinned and checked before output creation or parsing. The complete mapping matches run-003's independently reviewed receipt.
Final: minor (deferred): Table 13 report should state adjacent to universal agreement that Rules A/B are interpretations, not observed author deletions.
Final: minor (deferred): Report wording `every composition-derived metric` overstates verifier coverage; use an exact list or extend coverage.
Final: minor (deferred): Reader report displays an absolute workstation path instead of a relative raw-input path.
Final: minor (deferred): Run code-identity receipt omits both verifier scripts.
Task 3: complete — run-004 audit/comparison/report all executed; 10/10 contract fixtures PASS; 3,234,610-cluster full verifier PASS; read-only report and all output/code receipts PASS; actual comparison rerun refusal left every final output byte unchanged.
Final: all 12 numerical/verdict artifacts are byte-identical between independently reviewed run-003 and control-fixed run-004. Updated README, SCOPE, raw manifest, src/README and results/README are UTF-8/LF.
Final: Ruling: preserve the SDD ledgers instead of deleting the plan workspace — this non-Git scientific member has no commit history, and the frozen contract requires immutable correction/run receipts — cost if wrong: none; the ledgers are the required custody record.
Stage 1 completion: all frozen outputs and discrepancies are written, the `dropped` singleton primary is locked before C4, both Important review findings have RED→GREEN regression fixes, and four Minor items are deferred as listed above.
