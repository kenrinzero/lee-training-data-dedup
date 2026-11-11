# Step 0 Task 1 report — source-native targets and locators

## Outcome

The printed oracle is complete for the current C1–C7 claim inventory. The ACL
PDF, not the historical seed or study-unit Markdown, supplied every numerical
value recorded as printed. No cluster archive was downloaded or opened, and no
cluster-derived estimate or printed-arithmetic derivation was run.

The source itself leaves four exact public split-size inputs unprinted and
omits the twentieth C4 URL promised by Table 11. These are explicit unresolved
items rather than guessed values; the missing Table 11 total and fraction also
have structured ledger rows. All 44 requested figure bars were readable and
transcribed.

## Outputs

1. `paper/targets/README.md`
   - Complete C1–C7 source-native locator map.
   - Exact Table 2, Table 13, Table 11, appendix, and figure values with units.
   - Figure bin-edge findings, source discrepancies, unresolved inputs, and CSV
     conventions.
2. `paper/targets/printed-targets.csv`
   - Required ten-column header.
   - 193 unique scalar rows covering C1–C6, including all 44 figure scalars.
   - Claim row counts: C1 3; C2 23; C3 55; C4 21; C5 59; C6 32.
   - Exact `UNRESOLVED` sentinels for four split-size inputs absent from the
     PDF and two absent Table 11 cells; no blank printed values or units.
3. `paper/targets/figure-bars.csv`
   - Required seven-column header.
   - 44 rows: 11 C4 bars from Figure 1 and 11 bars from each of the three
     Figure 8 panels (LM1B, Real News, Wiki40B).
   - Exact printed bin labels, including `[5001, ∞)`, and integer bar labels.
4. `paper/PROVENANCE.md`
   - Added only inspected title/byline/page facts and the PDF rights finding.
   - Existing custody, byte count, and SHA-256 history were left unchanged.
5. `planning/step0/task-1-report.md`
   - This self-review and evidence summary.

`PREREGISTRATION.md` and `CLAIM_INVENTORY.md` were not edited. No Git repository
was initialized and no commit was made.

## Source inspection

The preserved `paper/paper.pdf` was inspected with `pdfinfo`, layout text, and
rendered pages. It has 22 A4 pages, 720,473 bytes, and SHA-256
`dcfa46d7aced43a97b9cf2ebd705919b65d4dd8a44d0914b1e646fe2d59ea8d3`, matching
the existing provenance receipt.

Rendered inspection covered the title/byline page (p. 1), which was also
checked for a rights notice, dataset descriptions (p. 3), method context (p. 4), Table 2/Figure 1/§5.1
(p. 5), Appendices C/D (p. 15), Table 6 and appendix prose (p. 16), the
EXACTSUBSTR dataset-size continuation (p. 18), and Tables 11/13 plus Figure 8
(pp. 21–22). Page 20 was also rendered during the appendix sequence. The
source-native page numbers equal PDF page indices.

Important inspection findings:

- Page 1 prints the expected title and seven-author byline and carries the
  `arXiv:2107.06499v2 [cs.CL] 24 Mar 2022` watermark.
- No paper licence, copyright notice, or Creative Commons statement appears in
  the 22-page PDF. This is recorded as absence of a stated licence, not as a
  determination of unrestricted rights.
- Figure 1 and every Figure 8 panel omit exact cluster sizes 10, 20, 50, 500,
  and 5000 through their printed half-open bin labels.
- Figure 8 has three unlettered panels, not four lettered panels. The CSV names
  (a), (b), and (c) are documented top-to-bottom reading-order conventions.
- Table 11 prints 19 C4 rows although its caption promises 20.
- Layout extraction misaligns Table 11 totals and interleaves Table 13. The
  delivered values were checked against native-resolution rendered crops.
- Table 13's C4 EXACTSUBSTR example size repeats NEARDUP at 350.48M, whereas
  Appendix C groups ORIGINAL and EXACTSUBSTR at approximately 365M. This is
  logged as a source consistency issue, not asserted to be a copy error.

## Initial commands and evidence (190-row version)

This historical validation record is superseded by the appended review fix
report, which contains the current 193-row counts and validation output. The
following command classes were run from the member root:

```bash
pdfinfo paper/paper.pdf
pdftotext -layout paper/paper.pdf planning/step0/paper-layout.txt
pdftoppm -f 1 -l 1 -png -r 150 -singlefile paper/paper.pdf planning/step0/rendered/page-01
pdftoppm -f 3 -l 3 -png -r 200 -singlefile paper/paper.pdf planning/step0/rendered/page-03
pdftoppm -f 4 -l 5 -png -r 200 paper/paper.pdf planning/step0/rendered/page
pdftoppm -f 14 -l 22 -png -r 200 paper/paper.pdf planning/step0/rendered/page
sha256sum paper/paper.pdf
wc -c paper/paper.pdf
```

The actual rendering was split into shorter `pdftoppm` ranges covering the same
pages. The layout extraction contained invalid UTF-8 font bytes, so a temporary
inspection copy was decoded with replacement solely for navigation. Numerical
transcription was verified against the rendered PDF, especially where extraction
order was ambiguous.

A Python 3 standard-library validation script was run with `python -B`. It:

- parsed both CSVs with `csv.DictReader` and asserted the exact required
  headers;
- asserted 190 rows and globally unique `target_id` values;
- asserted the C1–C6 per-claim row counts listed above;
- asserted every Table 2 and Table 13 cell against an independent expectation
  dictionary transcribed from the rendered tables;
- asserted exactly 44 figure rows, four figure groups, and bin indices 1–11 in
  each group;
- asserted integer figure counts and exact value/page agreement between the two
  CSV representations;
- asserted exactly the three named `UNRESOLVED` rows and no blank printed value
  or unit; and
- decoded the Markdown/CSV/provenance outputs as UTF-8 and asserted that they
  contain no carriage returns.

Final validation output:

```text
PASS: 190 unique scalar rows; C1-C6 counts 3/23/53/21/59/31; Table 2 and Table 13 exact-value assertions passed.
PASS: 44 bars in four groups of 11; all figure values and pages agree across CSVs; exactly 3 explicit UNRESOLVED split-size rows.
PASS UTF-8/LF: paper/targets/README.md
PASS UTF-8/LF: paper/targets/printed-targets.csv
PASS UTF-8/LF: paper/targets/figure-bars.csv
PASS UTF-8/LF: paper/PROVENANCE.md
```

An earlier validation invocation used an incorrect expected total of 192 and
stopped at that assertion. Inspection showed the actual planned total was 190;
the expectation was corrected and the complete validation above passed. No CSV
value was changed in response to that checking error.

The source receipt was rechecked after output generation:

```text
dcfa46d7aced43a97b9cf2ebd705919b65d4dd8a44d0914b1e646fe2d59ea8d3 *paper/paper.pdf
720473 paper/paper.pdf
```

`data/raw/` still contains only its pre-existing `MANIFEST.md`. No acquisition
command, cluster parser, split join, removal rule, or cluster estimate was run.
Temporary layout text and rendered inspection images were removed after checks;
they are not deliverables.

## Self-review against the brief

| Requirement | Result |
|---|---|
| Inspect title/byline, rights, and all included source-native claims | Done using layout text plus rendered source pages and crops. |
| Complete C1–C7 locator map and source discrepancies | Done in `paper/targets/README.md`. |
| Every C1–C6 scalar, units, precision, Table 13, appendix anchors, LM1B inputs | Done in 193-row scalar ledger; four exact unprinted split inputs and two absent Table 11 cells are explicitly unresolved. |
| All 11 bars for Figure 1 and each actual Figure 8 corpus panel | Done: 44 readable bars; no guessed or unresolved bar. |
| Record omitted exact edge sizes 10/20/50/500/5000 | Done for Figure 1 and all Figure 8 panels. |
| Record whether the PDF states a licence | Done: no licence statement found; provenance updated without altering custody/hash history. |
| Avoid deferred targets | No memorization or standalone EXACTSUBSTR reproduction target added; contextual EXACTSUBSTR cells are limited to existing C2/C4/C5/C6 consistency checks. |
| Avoid cluster data and estimates | Confirmed; no archive downloaded/opened and no cluster computation ran. |
| UTF-8/LF | Verified programmatically for all text deliverables. |
| Protect inventory and preregistration | Neither file edited. |
| No subagent | No subagent or reviewer was dispatched. |

## Unresolved locators and values

1. `c4-exact-train-size`: no exact public C4 train split count is printed. The
   PDF supplies only §3's 360M and Table 13's rounded 364.87M descriptions.
2. `c4-exact-validation-size`: no exact C4 validation split count is printed.
3. `lm1b-exact-train-size`: no exact public LM1B train split count is printed.
   Section 3's coarse 30M and Table 13's rounded 30.30M are not the exact public
   split count required for LM1B arithmetic.
4. `lm1b-exact-validation-size`: no exact LM1B validation split count is
   printed.
5. Table 11's twentieth C4 URL, its total, and its duplicate fraction are absent
   from the PDF and cannot be located from this source. The total and fraction
   are represented by `table11-c4-r20-total` and `table11-c4-r20-frac`, both
   `UNRESOLVED`; the URL identity remains unresolved in `split_or_arm`.

The seed's exact public split counts were deliberately not imported. Later
printed-plus-public-split arithmetic must pin and document a separate source for
those inputs. There are no unresolved figure bars, Table 2 cells, Table 13
cells, printed Table 11 rows, or appendix anchors.


## Review fix report — LM1B ledger, Table 11 sentinels, and rights wording

All three review findings were addressed without editing `PREREGISTRATION.md`
or `CLAIM_INVENTORY.md` and without dispatching a subagent.

1. Added `lm1b-exact-train-size` as `UNRESOLVED`. Its notes explicitly
   distinguish §3's coarse 30M and Table 13's rounded 30.30M from the exact
   public train-split count needed for LM1B arithmetic. The README and current
   report completeness statements now cover four public split sizes: C4
   train/validation and LM1B train/validation.
2. Added `table11-c4-r20-total` and `table11-c4-r20-frac` as structured C3
   `UNRESOLVED` rows on source page 21, with units `examples` and `ratio`.
   Their `split_or_arm` fields record that the URL identity is also unresolved.
   The README now points to these machine-readable entries.
3. Replaced the ambiguous “rights-bearing” phrase in provenance and this report.
   Provenance now says only that none of the licence/copyright occurrences
   concerns the paper's own licence, without misclassifying the p. 9 body prose.

The scalar ledger now has 193 unique rows: C1 3; C2 23; C3 55; C4 21; C5 59;
C6 32. There are six `UNRESOLVED` rows in total: exactly four public split
sizes plus the two structured Table 11 cells.

### Covering validation command

```bash
python -B - <<'PY'
import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

root = Path('paper/targets')
with (root / 'printed-targets.csv').open(encoding='utf-8', newline='') as f:
    reader = csv.DictReader(f)
    targets = list(reader)
    assert reader.fieldnames == ['target_id','claim_id','page','locator','corpus','quantity','split_or_arm','printed_value','unit','notes']
with (root / 'figure-bars.csv').open(encoding='utf-8', newline='') as f:
    reader = csv.DictReader(f)
    bars = list(reader)
    assert reader.fieldnames == ['figure','page','corpus','bin_index','bin_label','printed_count','notes']
by_id = {r['target_id']: r for r in targets}
assert len(targets) == len(by_id) == 193
assert Counter(r['claim_id'] for r in targets) == {'C1':3,'C2':23,'C3':55,'C4':21,'C5':59,'C6':32}
unresolved = {r['target_id'] for r in targets if r['printed_value'] == 'UNRESOLVED'}
split_ids = {'c4-exact-train-size','c4-exact-validation-size','lm1b-exact-train-size','lm1b-exact-validation-size'}
row20_ids = {'table11-c4-r20-total','table11-c4-r20-frac'}
assert unresolved == split_ids | row20_ids
assert len(split_ids) == 4
for target_id in split_ids:
    assert by_id[target_id]['page'] == 'NA'
assert by_id['lm1b-exact-train-size']['notes'].startswith('Only coarse 30M in §3 and rounded 30.30M')
assert by_id['table11-c4-r20-total']['unit'] == 'examples'
assert by_id['table11-c4-r20-frac']['unit'] == 'ratio'
for target_id in row20_ids:
    row = by_id[target_id]
    assert row['claim_id'] == 'C3' and row['page'] == '21'
    assert row['split_or_arm'] == 'UNRESOLVED'
print('PASS: 193 unique scalar rows; C1-C6 counts 3/23/55/21/59/32.')
print('PASS: exactly four unresolved public split sizes (C4 train/validation; LM1B train/validation).')
print('PASS: structured unresolved Table 11 twentieth-row total/fraction; six UNRESOLVED rows total.')

groups = defaultdict(list)
for row in bars:
    groups[row['figure']].append(row)
assert len(bars) == 44
assert set(groups) == {'Figure 1','Figure 8(a)','Figure 8(b)','Figure 8(c)'}
prefix = {'Figure 1':'fig1-c4-bin-','Figure 8(a)':'fig8-lm1b-bin-','Figure 8(b)':'fig8-realnews-bin-','Figure 8(c)':'fig8-wiki40b-bin-'}
for figure, rows in groups.items():
    assert len(rows) == 11
    assert [int(r['bin_index']) for r in rows] == list(range(1,12))
    for row in rows:
        scalar = by_id[prefix[figure] + f"{int(row['bin_index']):02d}"]
        assert scalar['printed_value'] == row['printed_count']
        assert scalar['page'] == row['page']
print('PASS: all 44 bars in four groups of 11 agree with the scalar ledger.')

paths = [root/'README.md',root/'printed-targets.csv',root/'figure-bars.csv',Path('paper/PROVENANCE.md'),Path('planning/step0/task-1-report.md')]
for path in paths:
    data = path.read_bytes()
    data.decode('utf-8')
    assert b'\r' not in data
    print(f'PASS UTF-8/LF: {path}')
pdf = Path('paper/paper.pdf').read_bytes()
digest = hashlib.sha256(pdf).hexdigest()
assert len(pdf) == 720473
assert digest == 'dcfa46d7aced43a97b9cf2ebd705919b65d4dd8a44d0914b1e646fe2d59ea8d3'
print(f'PASS PDF unchanged: {digest} ({len(pdf)} bytes)')
raw_entries = sorted(p.name for p in Path('data/raw').iterdir())
assert raw_entries == ['MANIFEST.md']
print('PASS data/raw acquisition check: only MANIFEST.md present.')
PY
sha256sum paper/paper.pdf
```

### Covering validation output

```text
PASS: 193 unique scalar rows; C1-C6 counts 3/23/55/21/59/32.
PASS: exactly four unresolved public split sizes (C4 train/validation; LM1B train/validation).
PASS: structured unresolved Table 11 twentieth-row total/fraction; six UNRESOLVED rows total.
PASS: all 44 bars in four groups of 11 agree with the scalar ledger.
PASS UTF-8/LF: paper/targets/README.md
PASS UTF-8/LF: paper/targets/printed-targets.csv
PASS UTF-8/LF: paper/targets/figure-bars.csv
PASS UTF-8/LF: paper/PROVENANCE.md
PASS UTF-8/LF: planning/step0/task-1-report.md
PASS PDF unchanged: dcfa46d7aced43a97b9cf2ebd705919b65d4dd8a44d0914b1e646fe2d59ea8d3 (720473 bytes)
PASS data/raw acquisition check: only MANIFEST.md present.
dcfa46d7aced43a97b9cf2ebd705919b65d4dd8a44d0914b1e646fe2d59ea8d3 *paper/paper.pdf
```

No cluster archive was downloaded or opened and no cluster-derived estimate was
run during the fixes. `data/raw/` still contains only `MANIFEST.md`.
