# Implementation state

Stages 1, 2, 3 and 7 are implemented under [FROZEN v1](../PREREGISTRATION.md)
and its dated amendments. Acquisition, deterministic counting, printed-target
comparison, verification and reader generation are separate. Never extract the
full C4 or RealNews CSV or start a NEARDUP implementation.

## Stage 1 programs

- `stage1_audit.py`: verifies all 24 expected input SHA-256 values before output
  creation, parses the released archive and exact split keys, and writes derived
  aggregates and diagnostics.
- `stage1_compare.py`: grades printed cells and locks conventions without
  overwriting outputs.
- `verify_stage1.py`: runs hand-derived fixtures and recomputes metrics and figures.
- `stage1_report.py` and `verify_stage1_report.py`: generate and read-check the
  reader report and receipts.

## Stage 2 programs

- `stage2_identity.py`: streams the C4 cluster CSV and applies the release kill gate.
- `stage2_acquire.py`: resumably streams original train shards, checks every LFS
  SHA-256 and preserves exact URL/split rows and receipts under Amendment A1.
- `stage2_audit.py`: streams exact joins into compact arrays and DuckDB tables,
  then computes metrics, removals and URL diagnostics.
- `stage2_compare.py`: grades all printed cells and companion dispositions.
- `stage2_finalize.py`: links preserved numerical evidence to new immutable
  finalization runs and verifies all 1,024 train receipts.
- `verify_stage2.py`, `stage2_report.py` and `verify_stage2_report.py`: provide
  independent numerical, custody and reader checks.

## Stage 3 programs

- `stage3_audit.py`: verifies the RealNews archive before output creation,
  streams typed rows into DuckDB, and derives histograms, figures, exact-ID URL
  statistics and the split-free ceiling without reading printed targets.
- `stage3_compare.py`: grades all Figure 8(b) conventions, 19 exact-ID URL rows,
  conditional Table 13 arithmetic and split/token sentinels.
- `stage3_report.py`: renders the reader report and immutable output/code receipts.
- `verify_stage3.py`: runs hand-derived and mutation fixtures, rebuilds cluster
  histograms and URL aggregates directly from `released`, independently checks
  figure/ranking logic and re-hashes the raw archive with `--full`.
- `verify_stage3_report.py`: checks reader qualifications and every recorded
  output/code hash without modifying the run.

## Stage 7 programs

- `stage7_build.py`: verifies frozen and accepted-source receipts, builds the
  complete printed-value ledger and figure data, and generates the integrated
  report, standalone SVGs and dependency-free offline reader.
- `verify_stage7.py`: runs contract and mutation fixtures, then verifies every
  regenerated public artifact, accepted-source receipt, output hash and code
  hash without modifying the candidate.

Use an unused run name for every regeneration. Final candidates are
`results/stage1/run-004/audit/`, `results/stage2/run-004/audit/`,
`results/stage3/run-002/audit/` and `results/stage7/run-002/audit/`; earlier
runs preserve correction lineage. DuckDB 2.0.0 is installed only in the
project-local `.venv`; Stage 7 uses the standard library and has no runtime
browser dependencies. Write CSV/JSON/text as UTF-8 with LF line endings and run
Python with `-B`.
