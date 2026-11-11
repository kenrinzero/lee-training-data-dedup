# SDD ledger — plan: PREREGISTRATION.md §10–§12 (FROZEN v1)

Stage 7 integrates the accepted Stage 1 run-004, Stage 2 run-004 and Stage 3 run-002 outputs with the frozen Step-0 oracle and arithmetic. It does not reopen cluster estimation, select conventions, normalize URLs, or add deferred experiments.

Plan:
1. Verify every accepted source output against its immutable run manifest before creating Stage 7 outputs.
2. Build a complete printed-value ledger, preserving all 193 oracle rows and expanding multi-arm, multi-rule and multi-convention checks. Add the external 1.68% statement separately.
3. Generate Figure 1 and Figure 8 as standalone SVG and an offline HTML reader. Show dropped/low/high results, exact omitted edge sizes, accessible data tables, printed-only LM1B values and non-executable reasons.
4. Generate an integrated report and immutable input/output/code receipts. Refuse overwrite and require an unused run for corrections.
5. Verify numerical structure, source identity, reader qualifiers, internal links, UTF-8/LF, browser behavior and the deferred cold-disk raw-input hashes.
6. Obtain fresh-context scientific and reader review; fix Critical/Important findings in a new immutable run and defer only recorded Minor items.

Design decisions (executor calls under the existing frozen design):
- Use Python standard-library generation and dependency-free HTML/CSS/JavaScript/SVG; no runtime network or package dependency.
- Make `index.html` the default reader surface, with `report.md`, `ledger.csv`, `ledger.json`, `figures.json` and standalone SVG as linked audit outputs.
- Use a light scientific-dashboard layout inspired by the preserved Octen references: restrained navigation, white reading surfaces, compact status colors and proportional horizontal bars. Reference content is design material only, not copied implementation.
- Apply semantic landmarks, labeled filters, a polite result-count region, keyboard-scrollable responsive tables, visible focus and chart data-table alternatives from modern-web-guidance.
- Preserve the raw inputs and all earlier runs unchanged. Only aggregate values and source-relative links enter the reader.

Ruling: include all 193 printed-oracle rows, including context and source sentinels, so coverage is auditable; rows without an authorized executable verdict carry an explicit disposition and reason rather than disappearing — cost if wrong: the ledger is longer, but no printed target or limitation is hidden.
Ruling: preserve run ledgers instead of deleting plan workspaces — this non-Git scientific member uses them as immutable custody records — cost if wrong: none; earlier stages follow the same rule.
