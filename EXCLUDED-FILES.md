# Excluded material

The public export is allowlisted. It excludes:

- Raw cluster archives, public dataset rows, Parquet/JSON shards, and DuckDB work
  stores; only aggregate audit outputs and the raw-input manifest remain.
- The source paper PDF and its local study unit.
- Python virtual environments, caches, temporary browser/server files, design
  reference downloads, and local scratch state.
- Superseded Stage 1–3 runs and their correction lineage. Final accepted run
  reports and final progress ledgers remain; Stage 7 run-001 and run-002 remain
  to preserve the final correction and independent review chain.
- Local Atelier control-plane files, private session records, and absolute
  workstation paths. Public receipt copies use member-relative paths and have
  recomputed byte and SHA-256 receipts.
- Deferred substring, EXACTSUBSTR, memorization, perplexity, and model-quality
  inputs and experiments, which were outside the authorized project scope.
