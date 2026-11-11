# Raw inputs and planned-source manifest

**State on 2026-11-10:** the Wiki-40B cluster archive and all 23 pinned English
split shards are acquired and hash-verified for Stage 1. The C4 cluster archive
is acquired and its release identity passed. All 1,024 original C4 train JSON
shards were streamed with per-shard SHA-256 receipts under Amendment A1; the
exact URL/split store is preserved locally. Full validation Parquet is acquired.
The RealNews cluster archive is acquired and hash-verified for Stage 3. LM1B and
deferred-stage inputs remain **UNACQUIRED**. Complete receipts are in the Stage 1
run-004, final Stage 2 run-004, Stage 3 run-001 acquisition and final run-002
manifests; generation code pins and checks expected digests before every new run.

Raw inputs are immutable after acquisition. Record actual bytes and SHA-256
immediately, verify source hashes before every named run, and never overwrite a
raw file or run receipt. Cluster redistribution rights are unresolved; keep raw
inputs local and publish code/aggregates only unless a later rights review
permits more.

## 1. Authors' repository and release documentation

- **Repository:** `google-research/deduplicate-text-datasets`
- **Pinned commit:** `4e9888ac3f95dc4f6169867a04c4c19df02dafe3`
- **Commit date:** 2024-05-21T17:47:37Z
- **Accessed:** 2026-11-08
- **Commit API:** https://api.github.com/repos/google-research/deduplicate-text-datasets/commits/4e9888ac3f95dc4f6169867a04c4c19df02dafe3
- **Commit page:** https://github.com/google-research/deduplicate-text-datasets/commit/4e9888ac3f95dc4f6169867a04c4c19df02dafe3
- **Pinned README:** https://raw.githubusercontent.com/google-research/deduplicate-text-datasets/4e9888ac3f95dc4f6169867a04c4c19df02dafe3/README.md
- **Pinned LICENSE:** https://raw.githubusercontent.com/google-research/deduplicate-text-datasets/4e9888ac3f95dc4f6169867a04c4c19df02dafe3/LICENSE
- **Rights finding:** repository/code licence is Apache-2.0. The README requests
  citation when using the repository or deduplicated datasets and states that
  this is not an officially supported Google product. It provides no separate
  explicit cluster-CSV licence; redistribution rights remain unresolved.
- **Schema statement to test, not assume:** README names document ID, a boolean
  described as deletion status, and cluster ID. C4/RealNews IDs are URLs;
  Wiki-40B IDs are `wikidata_id`. Stage 1 must test the exposed `keep=1`
  singleton / `keep=0` multi-document lead before C4 diagnostics use it.

The repository itself is not acquired as a runtime dependency. No NEARDUP
reimplementation is authorized.

## 2. Planned released-cluster archives — HEAD only

Source base: `https://storage.googleapis.com/gresearch/data_deduplication/`.
The following response metadata was observed on **2026-11-08**. Compressed byte
counts are HEAD `Content-Length` acquisition checks, not local-file receipts.
Wiki-40B was acquired on 2026-11-09: member `wiki40b.csv`, 61,018,605
decompressed bytes, SHA-256
`db1df97ef3268e0bdf36c15b66c4f71e4b465c42864f7c009104bb96bf8f8a32`.
C4 was acquired on 2026-11-09 with SHA-256
`5b73b507b3aa08c7dca5d5da55afe27babe6a4ddde40f4107ad1e88e82986723`.
RealNews was acquired on 2026-11-10: member `realnews.csv`, 3,432,651,696
decompressed bytes, SHA-256
`27b14ae911e3bb2632f2a087e84f24c0f5163786d77ff92e1bbfa9d47473046c`.

| Planned local path | Exact source URL | HEAD status | Content-Length bytes | Last-Modified | ETag / generation | State |
|---|---|---:|---:|---|---|---|
| `clusters/wiki40b.tar.gz` | https://storage.googleapis.com/gresearch/data_deduplication/wiki40b.tar.gz | 200 | 26,773,963 | Tue, 27 Jul 2021 17:34:16 GMT | `e4eba37eb831246da906198444366c79` / `1627407256261584` | ACQUIRED 2026-11-09; hash verified |
| `clusters/c4.tar.gz` | https://storage.googleapis.com/gresearch/data_deduplication/c4.tar.gz | 200 | 13,872,073,006 | Tue, 27 Jul 2021 17:38:23 GMT | `220d839f47e8c743a3d8c50b66a494e4` / `1627407503614361` | ACQUIRED 2026-11-09; stream CSV unextracted |
| `clusters/realnews.tar.gz` | https://storage.googleapis.com/gresearch/data_deduplication/realnews.tar.gz | 200 | 1,428,191,066 | Tue, 27 Jul 2021 17:34:54 GMT | `cb8b64ed9840355ef00ff4a97175dac9` / `1627407294457178` | ACQUIRED 2026-11-10; hash verified; stream CSV unextracted |

All three successful HEAD responses reported `Content-Type: application/x-tar`
and `Accept-Ranges: bytes`. No range request was made. The Google MD5 metadata
observed was `5OujfrgxJG2pBhmERDZseQ==` for Wiki-40B,
`Ig2Dn0fox0Oj2MULZqSU5A==` for C4 and `y4tk7ZhANV7wD/SpcXXayQ==` for
RealNews; these do not replace SHA-256 receipts.

Historical seed-provided uncompressed CSV sizes are not promoted to verified
metadata. They remain prior exposure only and must be established from the
acquired archive if needed.

### LM1B unavailable endpoint

- **URL:** https://storage.googleapis.com/gresearch/data_deduplication/lm1b.tar.gz
- **HEAD on 2026-11-08:** 404; `Content-Length: 202`;
  `Content-Type: application/xml; charset=UTF-8`.
- **State:** UNACQUIRED / no alternative cluster source pinned.
- **Gate:** LM1B remains printed-only. Do not treat the README's general release
  sentence as proof of an available LM1B file and do not re-run NEARDUP to fill
  the gap.

## 3. Pinned public split metadata

All metadata was accessed on **2026-11-08**. Counts below pin join
denominators. Wiki-40B rows were acquired on 2026-11-09; C4 and LM1B rows were
not acquired.

### Wiki-40B

- **Dataset/config:** Hugging Face `google/wiki40b`, `en`
- **Revision:** `06bfe584d8193cf58f79c6354ecc2a2b94a7deea`
- **Exact counts:** train **2,926,536**; validation **163,597**; test
  **162,274** pages
- **Join field:** `wikidata_id`
- **Pinned card:** https://huggingface.co/datasets/google/wiki40b/raw/06bfe584d8193cf58f79c6354ecc2a2b94a7deea/README.md
- **API record:** https://huggingface.co/api/datasets/wiki40b (resolves to
  `google/wiki40b` and reports the pinned revision/counts)
- **Rights:** pinned card's Licensing Information says "More Information
  Needed"; no unrestricted redistribution right is inferred.
- **Acquisition completed:** all 23 exact split files are receipted in the
  Stage 1 run-004 input manifest. Physical counts and population balances match
  exactly; unique public keys equal released rows, with zero duplicate,
  cross-split, unmatched or missing keys. Validation and test remain separate.

### C4

- **Dataset/config:** Hugging Face `legacy-datasets/c4`, `en`
- **Revision:** `21e98d7063e4037e836a0299d7fbb7efd484e6c3`
- **Exact counts:** train **364,868,892**; validation **364,608** examples
- **Join field:** `url`
- **Pinned card:** https://huggingface.co/datasets/legacy-datasets/c4/raw/21e98d7063e4037e836a0299d7fbb7efd484e6c3/README.md
- **API record:** https://huggingface.co/api/datasets/legacy-datasets/c4
- **Authority:** preserved from approved Task 2; not re-derived from the seed.
- **Actual split source:** `allenai/c4` root revision
  `1588ec454efa1a09f29cd18ddd04fe05fc8653a2`. The maintained Parquet train
  contains only 2,207,027 rows and is preserved but excluded. Instead, all 1,024
  original train JSON shards (326,778,635,540 bytes) were streamed under
  Amendment A1; exact URLs and per-shard receipts are retained without their
  compressed document bodies. Two full validation Parquet files are acquired.
- **Derived public store:** `results/stage2/run-002/work/public.duckdb`,
  14,786,244,608 bytes, SHA-256
  `f0fc381d48dcb2f25f8f1121980b8f8f0bc030a86857f21e9e6cdb44a7751297`.
  Exact physical counts match the frozen sizes. Duplicate/cross-split and
  population-balance diagnostics remain mandatory in the full audit. The C4 CSV
  is streamed from its archive without full extraction.

### LM1B

- **Dataset/config:** Hugging Face `billion-word-benchmark/lm1b`, `plain_text`
- **Revision:** `35161838ea9e05371a25a8db037f94fcae4c2064`
- **Exact counts:** train **30,301,028**; held-out **`test` 306,688** sentences
- **Pinned card:** https://huggingface.co/datasets/billion-word-benchmark/lm1b/raw/35161838ea9e05371a25a8db037f94fcae4c2064/README.md
- **API record:** https://huggingface.co/api/datasets/billion-word-benchmark/lm1b
- **Pinned loader:** https://huggingface.co/datasets/billion-word-benchmark/lm1b/raw/35161838ea9e05371a25a8db037f94fcae4c2064/lm1b.py
- **Authority:** preserved from approved Task 2. The public split is `test`, not
  validation; printed-only arithmetic maps evaluation to it explicitly.
- **Acquisition gate:** none for the authorized cluster stages; no LM1B cluster
  archive is pinned and LM1B Table 2 is not executable.

### RealNews

- **Exact public original train size:** UNRESOLVED.
- **Train/validation/test mapping and counts:** UNRESOLVED.
- **Gate:** RealNews Table 2 split cells and direct split-dependent Table 13
  train removals are `NOT_EXECUTABLE_INPUT`. Stage 3 may compute all-row figures,
  URL cells and a split-free keep-one ceiling. Do not invent split assignments
  or promote the archive total to a verified public train size without a source.

## 4. Acquisition and execution checklist

Before any future acquisition or run:

1. Confirm the frozen contract permits the input and stage; follow the three-
   attempt cap for repeated acquisition failures.
2. Record exact URL, revision/commit, access/acquisition date, planned local
   path, actual bytes, SHA-256 and rights in a new receipt.
3. Verify archive member name, parser/schema, physical rows and decompressed
   member size from the authorized input. Never treat HEAD availability as
   release identity.
4. Verify public split counts and exact-key joins; report duplicate IDs/URLs,
   cross-split keys, unmatched released keys and missing public keys.
5. Assert all source hashes before each run. Keep outputs immutable and create
   a new named run for corrections.
6. Keep C4 and RealNews streaming and unextracted as full CSVs. Do not download
   deferred substring, EXACTSUBSTR, memorization or model inputs under this manifest.

Stage 1 acquisition ran on 2026-11-09 for the Wiki-40B items above. One
transient validation-shard 404 was resolved by an identical pinned-URL request
returning the expected bytes; no alternate source or revision was used. Stage 2
acquired the C4 cluster and full validation files and completed streamed train
acquisition on 2026-11-10. Stage 3 acquired only the RealNews cluster archive on
2026-11-10. No LM1B, RealNews split or deferred-stage acquisition command has run.
