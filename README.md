# Lee et al.: duplication statistics against the released clusters

A pre-registered, executable audit of Lee et al. (2022),
*[Deduplicating Training Data Makes Language Models Better](https://doi.org/10.18653/v1/2022.acl-long.577)*.

**[Open the offline reader](index.html)** · **[Read the integrated report](REPORT.md)** · **[Independent audit](AUDIT.md)**

## Principal finding

The released C4, RealNews, and Wiki-40B cluster assignments reproduce **all 33
printed figure bars** when exact bin-edge sizes are dropped. Direct C4
train-with-train membership is nevertheless **4.63%**, not the printed **3.04%**.
C4 Table 13 reproduces under evaluation-preferred Rule A, while Rule B and the
all-train sensitivity do not. These are rule-derived interpretations, not
observed author deletions.

The audit also preserves the negative and bounded results: Wiki-40B's printed
`valid` remains unresolved between public validation and test; RealNews split
cells are non-executable, while its split-free ceiling is compatible; LM1B stays
printed-only; and exact full-ID URL misses are not promoted to host-level
contradictions. No claim about model quality, perplexity, or memorization follows
from this package.

## Read and reproduce

The root reader and the nested reader at
`results/stage7/run-002/audit/index.html` are dependency-free HTML/CSS/JavaScript
and SVG. They work offline without a server. The complete ledger contains **286
entries covering all 193 printed-oracle rows**, including alternative evaluation
arms, removal rules, conventions, and explicit non-executable reasons.

From the repository root:

```bash
python -B src/verify_stage1.py
python -B src/verify_stage2.py
python -B src/verify_stage3.py
python -B src/verify_stage7.py
python -B src/verify_stage1_report.py --run-dir results/stage1/run-004/audit
python -B src/verify_stage2_report.py --run-dir results/stage2/run-004/audit
python -B src/verify_stage3_report.py --run-dir results/stage3/run-002/audit
python -B src/verify_stage7.py --run-dir results/stage7/run-002/audit
python -B src/verify_stage7_publication.py --run-dir .
```

Stages 2 and 3 use DuckDB only for their original raw-data audits; install the
recorded version in your chosen environment with
`python -m pip install duckdb==2.0.0` before running those two test suites.
Stage 7 and the publication exporter use only the Python standard library.
Raw clusters, dataset rows, and DuckDB stores are not included, so full raw-data
reacquisition and full original-stage audits are intentionally not part of this
public package. The included checks verify the accepted aggregate artifacts and
the deterministic Stage 7/export integration.

## Package boundary

`EXCLUDED-FILES.md` lists the omitted raw, private, superseded, and environmental
material. `PACKAGE-PROVENANCE.json` records the export transform, and
`PACKAGE-MANIFEST.json` records every released file's bytes and SHA-256. The
immutable local runs were not edited: workstation paths were relativized only in
this public copy, with dependent receipts recomputed.

## License and credits

Project code is under the [MIT License](LICENSE). Original prose and figures are
under [CC BY 4.0](REPORT-LICENSE), to the extent this project can license them.
Third-party sources and limitations are recorded in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Directed by **Kenrin** ([@kenrinzero](https://github.com/kenrinzero)); built and
packaged by **Kimi K3.1 Pro**; independently reviewed across model families by
**Gemini 4 Argon (High)**. See [CREDITS.md](CREDITS.md) for the full record and
the original paper citation.
