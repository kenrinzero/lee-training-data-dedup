# Step 0 Task 3 report — revised contract candidate

## Outcome

Produced a review-ready **DRAFT v1 CANDIDATE — NOT FROZEN** for the authorized
Stages 1–3 and 7. The candidate carries the approved Task 1 printed oracle and
Task 2 arithmetic, including the corrected Figure 1 train floor, and adds
independently pinned Wiki-40B/repository/archive metadata.

No cluster archive, archive range/body, full dataset or split-row content was
downloaded or opened. No cluster-derived estimate or stage analysis ran. No Git
command, freeze receipt or subagent was used. Task 1/2 artifacts were not edited.

## Outputs

1. `PREREGISTRATION.md` — complete draft candidate: exposure ledger, source pins,
   cluster/split semantics, removal rules, figure conventions, rounding,
   release-identity kill branch, per-claim verdict coverage, immutable outputs
   and review gates.
2. `CLAIM_INVENTORY.md` — final PDF page/table/figure locators, cell-level
   computability, missing-input verdicts and checklist lenses.
3. `STEP0_DERIVATIONS.md` — approved oracle, public metadata, formulas, corrected
   bounds, internal-consistency findings, assumptions and the boundary between
   Step-0 findings and future cluster tests.
4. `data/raw/MANIFEST.md` — exact planned URLs, revisions, HEAD metadata, rights
   and acquisition gates; every input remains unacquired.
5. `planning/step0/task-3-report.md` — this decision, verification and self-review
   record.

## Source decisions

All source records below were accessed on **2026-11-08**.

- **Wiki-40B:** pinned Hugging Face `google/wiki40b`, `en`, revision
  `06bfe584d8193cf58f79c6354ecc2a2b94a7deea`. The pinned card/API record gives
  **2,926,536 train**, **163,597 validation** and **162,274 test** pages. The API
  request `https://huggingface.co/api/datasets/wiki40b` resolves to
  `google/wiki40b`; the inaccessible `legacy-datasets/wiki40b` alias was not used
  as authority.
- **C4 and LM1B:** preserved Task 2's exact revisions, counts and URLs without
  alteration. LM1B held-out evaluation remains public `test`, not a renamed
  validation split.
- **Authors' repository:** pinned commit
  `4e9888ac3f95dc4f6169867a04c4c19df02dafe3` through the GitHub commit API and
  commit-pinned README/LICENSE URLs. The repository/code licence is Apache-2.0;
  the README's citation request is recorded. No separate cluster-CSV licence was
  found, so redistribution remains gated.
- **Archive HEAD:** Wiki-40B, C4 and RealNews returned 200 with compressed sizes
  26,773,963 / 13,872,073,006 / 1,428,191,066 bytes and 2021-07-27 modification
  metadata. LM1B returned 404. These are availability/acquisition checks, not
  integrity or release-identity findings.
- **External C4 context:** pinned the Google Research publication abstract URL
  carrying 1.68%; it remains separate from the ACL PDF's cells.

## Contract decisions

1. **Membership before `keep`.** TT, EE, ET and Table 11 duplicate fractions use
   physical cluster membership. Stage 1 must first test the exposed Wiki
   `keep=1` singleton / `keep=0` multi-document lead; C4 `keep` is diagnostic
   only thereafter.
2. **Separate evaluation arms.** Wiki validation and test are evaluated
   separately, with exact public denominators and no advance relabelling of
   printed `valid`. Figures use all released rows and name their population.
3. **Deterministic joins.** IDs are exact parsed strings with no URL
   normalization. Duplicate keys remain physical rows; cross-split keys cause
   `INDETERMINATE_JOIN`, not arbitrary occurrence assignment. Duplicate URLs are
   not an exemption from C4's exact physical-row gate.
4. **Three removal outputs.** Rule A is evaluation-preferred, Rule B is uniform
   train keep-one, and the all-train sensitivity applies only to multi-document
   clusters. Validation-only/test-only and spanning clusters follow explicit
   formulas; a Wiki evaluation-union arm is sensitivity only.
5. **Convention fidelity.** Exact edge sizes 10/20/50/500/5000 are low, high or
   dropped. The primary is the unique convention matching all 11 Wiki bars;
   zero/multiple matches remain ambiguous. C4 requires exactly 365,233,500
   physical rows and at least one predeclared 11/11 convention match. A C4
   result cannot silently replace the Wiki-locked faithful convention.
6. **Rounding and size bases.** Percentages/ratios use ROUND_HALF_UP at displayed
   precision; counts and bars are exact. Table 13 uses exact public original
   size plus printed rounding intervals. Exact-original removal intervals are
   kept separate from Task 2's difference between independently rounded printed
   cells.
7. **Exact VV expectation.** Stage 2 must serialize the finite-population
   validation-with-validation expectation from the full cluster-size histogram
   before its comparison routine reads printed 1.59%. Direct observed EE remains
   a separate target.
8. **Every included target has a disposition.** This includes all printed cells,
   approximate 1.8M size-2 clusters plus "majority", exact 280 and 250,933,
   Table 11's 19 rows per corpus, the missing twentieth C4 row, RealNews's
   split-free ceiling and the release-identity kill branch.
9. **Non-executable is explicit.** RealNews Table 2 split cells/direct train
   removal, LM1B Table 2/cluster recounts, cluster-only token counts and missing
   printed source cells are not presented as executable released-cluster checks.
10. **No post-result faithfulness.** Inputs and outputs are immutable, hashes
    precede runs, C4 streams unextracted, all sensitivities remain visible and
    new post-result conventions require an amendment rather than silent adoption.

## Verification

### Source/metadata checks

- Fetched the pinned Wiki-40B card and API metadata; confirmed revision, `en`
  features and all three exact counts. Their sum is 3,252,407.
- Fetched the authors' commit record and commit-pinned README/LICENSE; confirmed
  the full commit SHA, CSV documentation, Apache-2.0 text, citation request and
  LM1B "coming soon" statement.
- Ran HEAD only against all four archive URLs. Confirmed three 200 responses,
  exact byte counts and LM1B 404. No archive body/range request was made.
- Confirmed `data/raw/` contains only `MANIFEST.md`; no `planning/step0/` freeze
  artifact exists.

### Numerical and content checks

Python 3 standard-library checks were run with `python -B`. They:

- strict-decoded all deliverables as UTF-8 and rejected carriage returns;
- asserted the exact candidate header and required membership, removal, edge,
  kill, rounding, histogram, verdict and streaming language;
- asserted all new source revisions/counts, repository commit, licence and
  unacquired states;
- checked the approved Task 2 JSON values for robust gap 2,905,134.2386,
  corrected Figure 1 bounds 8,001,466/14,410,977 and LM1B floor 510,877;
- independently recomputed those values with exact `Fraction`/integer arithmetic;
- recomputed exact-original Table 13 intervals and ROUND_HALF_UP original sizes;
- verified pinned split sums and that the approved Task 1 oracle still contains
  193 unique scalars and 44 bars; and
- rejected stale LM1B/seed values in the new deliverables.

Final pre-report output:

```text
PASS UTF-8/LF: PREREGISTRATION.md
PASS UTF-8/LF: CLAIM_INVENTORY.md
PASS UTF-8/LF: STEP0_DERIVATIONS.md
PASS UTF-8/LF: data/raw/MANIFEST.md
PASS: required contract, metadata, computability, corrected-number and stale-number assertions
PASS: approved JSON values and exact C4/Figure 1/LM1B arithmetic
PASS exact-original interval: N=364868892, removals=(14383892, 14393892), ORIGINAL=364.87
PASS exact-original interval: N=2926536, removals=(11536, 21536), ORIGINAL=2.93
PASS exact-original interval: N=30301028, removals=(426028, 436028), ORIGINAL=30.30
PASS: all pinned split sums
PASS: approved Task 1 oracle remains 193 scalars / 44 bars
PASS: data/raw contains only MANIFEST.md; all planned inputs unacquired
ALL PRE-REPORT CHECKS PASSED
```

An initial arithmetic assertion caught a Task 3 transcription error in the new
LM1B exact-original interval. It was corrected from the mistaken
`(423,028,433,028]` to **`(426,028,436,028]`** in both documents that carry it.
The approved Task 2 510,877 floor and its printed-difference comparison were not
changed. Two subsequent verification-harness assertions used overly specific
source-wording tokens (`nineteenth`, then `PDF p. 22`); inspection confirmed the
inventory's equivalent `19 printed` and `p. 22` wording. Only the harness tokens
were corrected, and the complete third run passed. These were checking errors,
not numerical or source changes.

## Self-review against the brief

| Requirement | Result |
|---|---|
| Read governing scope, current contract/inventory and approved Task 1/2 artifacts | Done; seed read afterward only for exposure labels |
| Pin Wiki-40B revision and exact train/validation/test counts | Done with commit-pinned card, API URL and access date |
| Pin authors' commit and licence/rights statements | Done; code licence and unresolved cluster rights distinguished |
| Check archive availability without downloads | Done by HEAD only; exact headers in manifest |
| Preserve C4/LM1B metadata and corrected arithmetic | Done and numerically asserted against approved JSON |
| Rewrite contract as DRAFT v1 CANDIDATE — NOT FROZEN | Done; no result graded and no freeze receipt created |
| Final source-native inventory and computability limits | Done; RealNews/LM1B/missing-input cells explicitly non-executable |
| Membership-based TT/EE/ET and Wiki `keep` lead test | Done |
| Split denominators, separate evaluation arms, all-row figures | Done |
| Rules A/B, all-train sensitivity and split-spanning treatment | Done with formulas |
| Three edge conventions, unique Wiki primary, C4 kill identity | Done; ambiguity and non-promotion rules explicit |
| ROUND_HALF_UP, exact counts, exact-original Table 13 intervals | Done; interval bases distinguished |
| Full-histogram C4 VV expectation before 1.59% comparison | Done |
| Corrected 8,001,466/14,410,977, 2,905,134.2386 and 510,877 | Done in contract/derivations and checked exactly |
| Verdicts for all cells, §5.1, Table 11, RealNews ceiling and kill branch | Done |
| Immutable outputs, source hashes, unextracted C4, no silent convention change | Done |
| UTF-8/LF, no analysis, no Git, no subagent | Verified |

## Unresolved items and gates

1. Independent Type-B contract/scientific review and an explicit freeze remain
   pending. This candidate is not authorization to grade confirmatory results.
2. RealNews exact public original size and split mapping are unresolved; its
   Table 2 cells and direct train-removal comparison remain gated.
3. LM1B has no pinned cluster archive (HEAD 404); its Table 2 remains
   non-executable and its floor remains conditional on full-population figure
   coverage and public-test mapping.
4. Actual archive SHA-256, member identity, decompressed sizes, schemas and join
   coverage await authorized acquisition. HEAD 200 is not release identity.
5. Cluster-CSV and Wiki-40B redistribution rights remain unresolved; repository
   Apache-2.0 does not settle them.
6. Table 11's twentieth printed C4 URL/total/fraction is absent from the PDF;
   a future released-ranking candidate cannot become a recovered printed cell.
7. Figure 1/LM1B total-based derivations retain their full train+evaluation
   coverage assumption. Duplicate/cross-split joins may make future exact cells
   indeterminate and must be reported rather than repaired post hoc.

The appropriate next action is independent candidate review, not data analysis
or an automatic freeze.

---

## Independent-review fix report — six findings (2026-11-08)

The independent Spec FAIL findings are addressed in `PREREGISTRATION.md`,
`CLAIM_INVENTORY.md` and `STEP0_DERIVATIONS.md`. This section supersedes the
original report's Table 11 membership-estimand decision and its incomplete
ambiguity/join/RealNews branches. No approved Task 1/2 artifact or arithmetic
value changed. The candidate remains **DRAFT v1 CANDIDATE — NOT FROZEN**.

1. **Table 11 faithful estimand restored.** The caption's "marked as
   near-duplicates by NEARDUP" is operationalized as physical `keep=0` rows /
   physical `# Total` for both C4 and RealNews. Cluster-membership fractions are
   diagnostic/sensitivity only. `KEEP_MEMBERSHIP_DIVERGENCE` preserves both and
   forbids substituting membership to manufacture a printed-cell `MISMATCH`.
   Table 2 remains cluster-membership based.
2. **Ambiguous Wiki lock made executable.** A unique 11/11 match locks a primary;
   zero matches lock all three candidates; multiple matches lock exactly the
   matching subset. Ambiguous branches have no primary and C4 cannot break the
   tie. Convention-dependent C4 outputs remain sensitivity/
   `AMBIGUOUS_CONVENTION` or stop; non-convention outputs may proceed when release
   identity otherwise holds.
3. **Population balance added.** Every split requires `sum_c n_S(c)=N_S` in
   addition to unmatched/missing/cross-split checks, else `INDETERMINATE_JOIN`.
   Accepted unequal same-split multiplicities require balanced totals and are
   explicitly released-physical-row weighted.
4. **C4 top-20 eligibility restored.** Candidates first have unrounded `keep=0`
   share exactly 1, then rank by total descending and URL bytewise ascending.
   Directly transcribed rows remain unchanged.
5. **RealNews ceiling made exact.** Printed-difference removals lie in
   (2,760,000,2,780,000), with minimum integer 2,760,001. `U <= 2,760,000` is
   `CONTRADICTION`; otherwise the result is only `CEILING_COMPATIBLE`.
6. **RealNews 14.4% covered.** Table 2's 14.35% rounds half up to §5.3's 14.4%.
   This is printed-rounding consistency, not reproduction of the unavailable
   split cell.

No data were downloaded or opened, no cluster analysis ran, no subagent was
dispatched, no Git command was used and no freeze artifact was created.

### Covering verification command

Run from the member root with Python 3 standard library:

```bash
python -B - <<'PY'
import csv
import json
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from pathlib import Path

root = Path('.')
paths = {
    'contract': root / 'PREREGISTRATION.md',
    'inventory': root / 'CLAIM_INVENTORY.md',
    'derivations': root / 'STEP0_DERIVATIONS.md',
}
text = {name: path.read_text(encoding='utf-8') for name, path in paths.items()}
compact = lambda value: ''.join(value.split()).lower()
norm = {name: compact(value) for name, value in text.items()}
man = (root / 'data/raw/MANIFEST.md').read_text(encoding='utf-8')

# F1: faithful source-native Table 11 estimand and divergence branch.
for name, value in norm.items():
    for token in ['keep=0', '#total', 'keep_membership_divergence', 'sensitivity']:
        assert token in value, (name, token)
    assert 'fracdups`isthemulti-document' not in value
    assert 'keep=0`agreementisdiagnosticonly' not in value
assert 'physicalrowswith`keep=0`dividedbyphysical`#total`' in norm['contract']
assert 'fracdups=keep=0physicalrows/#total' in norm['derivations']
print('PASS F1: Table 11 faithful Frac Dups = keep=0 / physical # Total; membership sensitivity; explicit divergence')

# F4: C4 eligibility filter before ranking.
for name, value in norm.items():
    assert 'unrounded`keep=0`' in value, name
    assert 'shareequals1' in value or 'shareisexactly1' in value, name
    assert 'bytewiseascending' in value, name
assert 'directlytranscribedoraclerowsremainunchanged' in norm['contract']
assert 'directlytranscribedrowsremainunchanged' in norm['inventory']
assert (lambda k: sum(x == 0 for x in k) / len(k) == 1)([0, 0])
assert not (lambda k: sum(x == 0 for x in k) / len(k) == 1)([0, 0, 1])
print('PASS F4: unrounded keep=0 share == 1 eligibility filter precedes C4 total/URL ranking; transcription unchanged')

# F2: ambiguity locks and executable downstream branch.
for name, value in norm.items():
    for token in ['ambiguous_convention', 'non-convention', 'mayproceed', 'cannotbreakthetie']:
        assert token in value, (name, token)
    assert 'noprimary' in value or 'hasaprimary' in value, name
    assert 'zeromatcheslockallthreecandidates' in value or 'if**zero**match,thelockedcandidatesetis**allthree**' in value
    assert 'multiplematcheslockthematchingsubset' in value or 'if**multiple**match,thelockedsetisexactlythematchingsubset' in value
lock = lambda m: ('primary', m[0]) if len(m) == 1 else ('ambiguous', m if m else ['dropped', 'low', 'high'])
assert lock(['dropped']) == ('primary', 'dropped')
assert lock([]) == ('ambiguous', ['dropped', 'low', 'high'])
assert lock(['low', 'high']) == ('ambiguous', ['low', 'high'])
print('PASS F2: unique/zero/multiple locks explicit; no ambiguous primary or C4 tie-break; non-convention outputs may proceed')

# F3: per-split balance and physical-row estimand label.
for name, value in norm.items():
    for token in ['sum_cn_s(c)', 'n_s', 'indeterminate_join', 'released-physical-row']:
        assert token in value, (name, token)
assert 'sum_cn_s(c)=n_s' in norm['contract']
clusters = ({'train': 2, 'validation': 1}, {'train': 1, 'validation': 0})
assert sum(c['train'] for c in clusters) == 3
assert sum(c['validation'] for c in clusters) == 1
assert sum(c['validation'] for c in clusters) != 2
print('PASS F3: sum_c n_S(c)=N_S required per split; balanced unequal multiplicities labelled physical-row weighted')

# F5/F6: RealNews exact ceiling boundary and 14.4 disposition.
for name, value in norm.items():
    for token in ['(2,760,000,2,780,000)', '2,760,001', 'u<=2,760,000', 'u>=2,760,001', 'ceiling_compatible', '14.35%', '14.4%', 'reproduc']:
        assert token in value, (name, token)
verdict = lambda u: 'CONTRADICTION' if u <= 2760000 else 'CEILING_COMPATIBLE'
assert verdict(2760000) == 'CONTRADICTION'
assert verdict(2760001) == 'CEILING_COMPATIBLE'
assert Decimal('14.35').quantize(Decimal('0.1'), rounding=ROUND_HALF_UP) == Decimal('14.4')
print('PASS F5/F6: contradiction at U <= 2,760,000; compatible at 2,760,001; 14.35->14.4 rounding-only')

# Approved arithmetic regression.
with (root / 'planning/step0/arithmetic.json').open(encoding='utf-8') as f:
    approved = json.load(f)
d = {x['id']: x for x in approved['derivations']}
assert d['c4_removal_ceiling']['outputs']['robust_minimum_shortfall'] == 2905134.2386
assert d['fig1_bounds']['outputs']['train_removal_lower'] == 8001466
assert d['fig1_bounds']['outputs']['train_removal_upper'] == 14410977
assert d['lm1b_printed_only_floor']['outputs']['heldout_adjusted_train_removal_floor'] == 510877
assert Fraction(14380000) - (Fraction(3045, 100000) * 364868892 + 364608) == Fraction(29051342386, 10000)
assert 10868122 - 2502048 - 364608 == 8001466
assert 365233500 - 348320475 - 2502048 == 14410977
assert 1505410 - 687845 - 306688 == 510877
for n, m, expected in [(364868892, 350480000, (14383892, 14393892)), (2926536, 2910000, (11536, 21536)), (30301028, 29870000, (426028, 436028))]:
    assert (n - m - 5000, n - m + 5000) == expected
print('PASS regression: 2,905,134.2386; 8,001,466; 14,410,977; 510,877; exact-original Table 13 intervals unchanged')

# Source, oracle, acquisition, encoding and freeze integrity.
for token in ['06bfe584d8193cf58f79c6354ecc2a2b94a7deea', '4e9888ac3f95dc4f6169867a04c4c19df02dafe3', 'UNACQUIRED']:
    assert token in man
with (root / 'paper/targets/printed-targets.csv').open(encoding='utf-8', newline='') as f:
    targets = list(csv.DictReader(f))
with (root / 'paper/targets/figure-bars.csv').open(encoding='utf-8', newline='') as f:
    bars = list(csv.DictReader(f))
assert len(targets) == 193 and len({r['target_id'] for r in targets}) == 193 and len(bars) == 44
assert sorted(p.name for p in (root / 'data/raw').iterdir()) == ['MANIFEST.md']
assert not list((root / 'planning/step0').glob('*freeze*'))
all_paths = list(paths.values()) + [root / 'data/raw/MANIFEST.md', root / 'planning/step0/task-3-report.md']
for path in all_paths:
    data = path.read_bytes()
    data.decode('utf-8')
    assert b'\r' not in data, path
    print(f'PASS UTF-8/LF: {path} ({len(data)} bytes)')
print('PASS integrity: source pins and 193/44 oracle intact; inputs unacquired; no freeze artifact')
print('ALL SIX-FINDING REVIEW-FIX CHECKS PASSED')
PY
```

### Covering verification output

```text
PASS F1: Table 11 faithful Frac Dups = keep=0 / physical # Total; membership sensitivity; explicit divergence
PASS F4: unrounded keep=0 share == 1 eligibility filter precedes C4 total/URL ranking; transcription unchanged
PASS F2: unique/zero/multiple locks explicit; no ambiguous primary or C4 tie-break; non-convention outputs may proceed
PASS F3: sum_c n_S(c)=N_S required per split; balanced unequal multiplicities labelled physical-row weighted
PASS F5/F6: contradiction at U <= 2,760,000; compatible at 2,760,001; 14.35->14.4 rounding-only
PASS regression: 2,905,134.2386; 8,001,466; 14,410,977; 510,877; exact-original Table 13 intervals unchanged
PASS UTF-8/LF: PREREGISTRATION.md (27908 bytes)
PASS UTF-8/LF: CLAIM_INVENTORY.md (13819 bytes)
PASS UTF-8/LF: STEP0_DERIVATIONS.md (19341 bytes)
PASS UTF-8/LF: data/raw/MANIFEST.md (8616 bytes)
PASS UTF-8/LF: planning/step0/task-3-report.md (11666 bytes)
PASS integrity: source pins and 193/44 oracle intact; inputs unacquired; no freeze artifact
ALL SIX-FINDING REVIEW-FIX CHECKS PASSED
```

The next action is another independent candidate review, not an automatic freeze.

---

## Freeze report — FROZEN v1 (2026-11-08)

Independent re-review returned **Spec PASS / Quality APPROVED / Ready to freeze
YES** (agent-5 fresh context). Step 0 is frozen without changing the approved
scientific content. Stage 1 is next. No data were acquired, no cluster-derived
estimate or stage analysis ran, no subagent was dispatched and no Git repository
was initialized or used.

Lifecycle updates:

- `PREREGISTRATION.md`, `CLAIM_INVENTORY.md` and `STEP0_DERIVATIONS.md` now carry
  `FROZEN v1`, frozen date 2026-11-08, completed-review status and dated-appended-
  amendment-only history.
- Byte-identical immutable snapshots were created at
  `planning/preregistration-v1.md`, `planning/claim-inventory-v1.md` and
  `planning/step0-derivations-v1.md` after those updates.
- `planning/FREEZE-v1.json` records actual UTC freeze timestamp
  **2026-11-08T20:19:22Z**, no-analysis state, working/snapshot paths, agent-5
  fresh-context approval and SHA-256 for all 14 required files.
- `README.md` and `SCOPE.md` now state Step 0 complete / FROZEN v1 / Stage 1 next,
  while preserving the Stages 1–3 and 7 boundary and no-analysis-data state.

### Freeze validation command

Run from the member root with Python 3 standard library:

```bash
python -B - <<'PY'
import csv
import hashlib
import json
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

root = Path('.')
receipt_path = root / 'planning/FREEZE-v1.json'
receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
assert receipt['schema_version'] == 1
assert receipt['state']['label'] == 'FROZEN v1'
assert receipt['state']['step0_complete'] is True
assert receipt['state']['next_stage'] == 'Stage 1'
assert receipt['state']['cluster_derived_estimate_ran'] is False
assert receipt['state']['cluster_archive_downloaded_or_opened'] is False
assert receipt['state']['full_dataset_downloaded'] is False
assert receipt['state']['analysis_inputs_acquired'] is False
approval = receipt['independent_reviewer_approval']
assert approval == {'spec':'PASS','quality':'APPROVED','ready_to_freeze':True,'reviewer':'agent-5','context':'fresh context'}
timestamp = datetime.strptime(receipt['frozen_at_utc'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
assert timestamp.date().isoformat() == '2026-11-08'
print('PASS receipt metadata:', receipt['frozen_at_utc'], 'FROZEN v1; Stage 1 next; agent-5 fresh-context approval')

working = ['PREREGISTRATION.md','CLAIM_INVENTORY.md','STEP0_DERIVATIONS.md']
snapshots = ['planning/preregistration-v1.md','planning/claim-inventory-v1.md','planning/step0-derivations-v1.md']
assert receipt['working_files'] == working
assert receipt['snapshot_files'] == snapshots
assert receipt['snapshot_byte_equality'] == dict(zip(working, snapshots))
for w, s in zip(working, snapshots):
    wb, sb = (root/w).read_bytes(), (root/s).read_bytes()
    assert wb == sb, (w,s)
    text = wb.decode('utf-8')
    assert text.splitlines()[0].endswith('FROZEN v1'), w
    assert '**Frozen date:** 2026-11-08' in text, w
    assert 'Amendments and freeze history' in text and 'agent-5 fresh context' in text, w
    assert 'DRAFT v1 CANDIDATE' not in text and 'draft candidate' not in text and 'not frozen' not in text.lower(), w
    print(f'PASS frozen/equal: {w} == {s}')

required = set(working + snapshots + [
    'paper/targets/README.md','paper/targets/printed-targets.csv','paper/targets/figure-bars.csv',
    'planning/step0/arithmetic.md','planning/step0/arithmetic.json','data/raw/MANIFEST.md',
    'paper/paper.pdf','planning/SEED-2026-09-30.md'])
assert set(receipt['sha256']) == required
for path in sorted(required):
    digest = hashlib.sha256((root/path).read_bytes()).hexdigest()
    assert receipt['sha256'][path] == digest, path
    print(f'PASS SHA-256: {path} {digest}')
for w,s in zip(working,snapshots):
    assert receipt['sha256'][w] == receipt['sha256'][s]

for path in ['README.md','SCOPE.md']:
    text = (root/path).read_text(encoding='utf-8')
    assert 'draft' not in text.lower() and 'unfrozen' not in text.lower(), path
    assert 'FROZEN v1' in text and 'Stage 1 is next' in text, path
    assert 'no cluster-derived estimate or stage analysis has run' in text, path
    print(f'PASS lifecycle: {path} has FROZEN v1 / Stage 1 next / no analysis state')

pre = (root/'PREREGISTRATION.md').read_text(encoding='utf-8')
inv = (root/'CLAIM_INVENTORY.md').read_text(encoding='utf-8')
der = (root/'STEP0_DERIVATIONS.md').read_text(encoding='utf-8')
for name,text in [('contract',pre),('inventory',inv),('derivations',der)]:
    for token in ['KEEP_MEMBERSHIP_DIVERGENCE','AMBIGUOUS_CONVENTION','released-physical-row','U <= 2,760,000','14.35%','14.4%']:
        assert token in text,(name,token)
    assert 'unrounded `keep=0`' in text,name
print('PASS reviewed conventions preserved: Table 11, ambiguity, balance, RealNews threshold and 14.4 disposition')

with (root/'paper/targets/printed-targets.csv').open(encoding='utf-8',newline='') as f: targets=list(csv.DictReader(f))
with (root/'paper/targets/figure-bars.csv').open(encoding='utf-8',newline='') as f: bars=list(csv.DictReader(f))
assert len(targets)==193 and len({r['target_id'] for r in targets})==193 and len(bars)==44
with (root/'planning/step0/arithmetic.json').open(encoding='utf-8') as f: arithmetic=json.load(f)
d={x['id']:x for x in arithmetic['derivations']}
assert d['c4_removal_ceiling']['outputs']['robust_minimum_shortfall']==2905134.2386
assert d['fig1_bounds']['outputs']['train_removal_lower']==8001466
assert d['fig1_bounds']['outputs']['train_removal_upper']==14410977
assert d['lm1b_printed_only_floor']['outputs']['heldout_adjusted_train_removal_floor']==510877
assert Fraction(14380000)-(Fraction(3045,100000)*364868892+364608)==Fraction(29051342386,10000)
assert 10868122-2502048-364608==8001466
assert 365233500-348320475-2502048==14410977
assert 1505410-687845-306688==510877
print('PASS oracle/arithmetic: 193 scalars / 44 bars; 2,905,134.2386; 8,001,466; 14,410,977; 510,877 unchanged')

assert sorted(p.name for p in (root/'data/raw').iterdir())==['MANIFEST.md']
assert sorted(p.name for p in (root/'results').iterdir())==['README.md']
assert sorted(p.name for p in (root/'src').iterdir())==['README.md']
print('PASS no-analysis state: data/raw only MANIFEST.md; results/src only README.md; no cluster-derived result files')

text_paths = [root/p for p in sorted(required) if not p.endswith('.pdf')]
text_paths += [root/'README.md',root/'SCOPE.md',receipt_path,root/'planning/step0/task-3-report.md']
for path in text_paths:
    data=path.read_bytes(); data.decode('utf-8'); assert b'\r' not in data,path
print(f'PASS UTF-8/LF: {len(text_paths)} text files including freeze JSON, working files, snapshots, oracle and reports')
print('ALL FREEZE-v1 VALIDATION CHECKS PASSED')
PY
```

### Freeze validation output

```text
PASS receipt metadata: 2026-11-08T20:19:22Z FROZEN v1; Stage 1 next; agent-5 fresh-context approval
PASS frozen/equal: PREREGISTRATION.md == planning/preregistration-v1.md
PASS frozen/equal: CLAIM_INVENTORY.md == planning/claim-inventory-v1.md
PASS frozen/equal: STEP0_DERIVATIONS.md == planning/step0-derivations-v1.md
PASS SHA-256: CLAIM_INVENTORY.md faf1846b3c6b413d95905a75245aa5f0e914ef36da12d7cf0f1c63b250e6dbd4
PASS SHA-256: PREREGISTRATION.md 491718a862062c54006f509b1a54f8e0583e0b3dfb9765d85935c0dc51d8914c
PASS SHA-256: STEP0_DERIVATIONS.md e7cd7484b6eda077e8c26af063e30024b450e625ea10f9564fadabaf80d6d416
PASS SHA-256: data/raw/MANIFEST.md bfd8d213b98a3e69ae4f3dc8f3290547c8041c7db52338616988d97b268b16e1
PASS SHA-256: paper/paper.pdf dcfa46d7aced43a97b9cf2ebd705919b65d4dd8a44d0914b1e646fe2d59ea8d3
PASS SHA-256: paper/targets/README.md 0b475e7d28d81f83f2760b0050594a8698bd93221f001bcf3fd71437be432656
PASS SHA-256: paper/targets/figure-bars.csv adfa6dfb4d399245bf992a5de9103542c71c01903230b52b13321efe2b8b1067
PASS SHA-256: paper/targets/printed-targets.csv 78381f32a1f3bf48489e35db1c191db83de7362c8b3d7bb6936c9f707d3d0212
PASS SHA-256: planning/SEED-2026-09-30.md b20cbb510e44e36aa6e183087a3a4929e5706b94eef591e9d72b4c8049e259ab
PASS SHA-256: planning/claim-inventory-v1.md faf1846b3c6b413d95905a75245aa5f0e914ef36da12d7cf0f1c63b250e6dbd4
PASS SHA-256: planning/preregistration-v1.md 491718a862062c54006f509b1a54f8e0583e0b3dfb9765d85935c0dc51d8914c
PASS SHA-256: planning/step0-derivations-v1.md e7cd7484b6eda077e8c26af063e30024b450e625ea10f9564fadabaf80d6d416
PASS SHA-256: planning/step0/arithmetic.json 4b7c99e6ae7252f1aad56e1b3dba2a8ba25822ea4ea5008ec7214020c9643581
PASS SHA-256: planning/step0/arithmetic.md dd74783909ff309cf6091f253db817192530593e13dfc78da86e2d77f474b844
PASS lifecycle: README.md has FROZEN v1 / Stage 1 next / no analysis state
PASS lifecycle: SCOPE.md has FROZEN v1 / Stage 1 next / no analysis state
PASS reviewed conventions preserved: Table 11, ambiguity, balance, RealNews threshold and 14.4 disposition
PASS oracle/arithmetic: 193 scalars / 44 bars; 2,905,134.2386; 8,001,466; 14,410,977; 510,877 unchanged
PASS no-analysis state: data/raw only MANIFEST.md; results/src only README.md; no cluster-derived result files
PASS UTF-8/LF: 17 text files including freeze JSON, working files, snapshots, oracle and reports
ALL FREEZE-v1 VALIDATION CHECKS PASSED
```
