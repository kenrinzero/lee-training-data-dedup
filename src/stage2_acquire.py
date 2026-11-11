#!/usr/bin/env python3
import argparse
import gzip
import hashlib
import io
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.json as pa_json
import requests

from stage1_audit import receipt, sha256, write_json
from stage2_audit import EXPECTED_SPLIT_BYTES, EXPECTED_SPLIT_SHA256, SPLIT_ROOT_SHA

SCHEMA = pa.schema([("text", pa.string()), ("timestamp", pa.string()), ("url", pa.string())])


class HashingReader(io.RawIOBase):
    def __init__(self, raw):
        self.raw = raw
        self.digest = hashlib.sha256()
        self.bytes_read = 0

    def readable(self):
        return True

    def read(self, size=-1):
        data = self.raw.read(size)
        if data:
            self.digest.update(data)
            self.bytes_read += len(data)
        return data

    def readinto(self, buffer):
        count = self.raw.readinto(buffer)
        if count:
            self.digest.update(memoryview(buffer)[:count])
            self.bytes_read += count
        return count

    def hexdigest(self):
        return self.digest.hexdigest()

    def close(self):
        self.raw.close()
        super().close()


def validate_receipt_set(metadata_files, receipts):
    expected = {row["path"]: row for row in metadata_files}
    actual = {row["path"]: row for row in receipts}
    assert expected.keys() == actual.keys(), "train shard path set differs"
    total_bytes = total_rows = 0
    for path, source in expected.items():
        receipt = actual[path]
        assert receipt["bytes"] == source["size"], f"source byte mismatch: {path}"
        assert receipt["sha256"] == source["lfs"]["oid"], f"source SHA-256 mismatch: {path}"
        total_bytes += receipt["bytes"]
        total_rows += receipt["rows"]
    return {"shards": len(expected), "bytes": total_bytes, "rows": total_rows}


def stream_train_shard(con, source):
    path = source["path"]
    url = f"https://huggingface.co/datasets/allenai/c4/resolve/{SPLIT_ROOT_SHA}/{path}"
    expected_bytes = source["size"]
    for attempt in range(1, 4):
        response = None
        try:
            con.execute("BEGIN TRANSACTION")
            response = requests.get(url, stream=True, timeout=(30, 300))
            response.raise_for_status()
            hashed = HashingReader(response.raw)
            rows = 0
            with gzip.GzipFile(fileobj=hashed) as compressed:
                reader = pa_json.open_json(
                    compressed,
                    read_options=pa_json.ReadOptions(block_size=16 * 1024 * 1024),
                    parse_options=pa_json.ParseOptions(explicit_schema=SCHEMA),
                )
                for batch in reader:
                    table = pa.Table.from_batches([batch])
                    output = pa.table({
                        "url": table.column("url"),
                        "split": pa.array(["train"] * batch.num_rows, type=pa.string()),
                    })
                    con.register("batch_arrow", output)
                    con.execute("INSERT INTO public SELECT url, split FROM batch_arrow")
                    con.unregister("batch_arrow")
                    rows += batch.num_rows
            assert hashed.bytes_read == expected_bytes, f"compressed bytes differ for {path}: {hashed.bytes_read} != {expected_bytes}"
            digest = hashed.hexdigest()
            assert digest == source["lfs"]["oid"], f"source SHA-256 mismatch for {path}: {digest} != {source['lfs']['oid']}"
            con.execute("INSERT INTO acquired_shards VALUES (?, ?, ?, ?, ?)", [path, rows, hashed.bytes_read, digest, url])
            con.execute("COMMIT")
            return {"path": path, "url": url, "rows": rows, "bytes": hashed.bytes_read, "sha256": digest, "custody": "streamed; compressed body not retained"}
        except Exception:
            con.execute("ROLLBACK")
            if response is not None:
                response.close()
            if attempt == 3:
                raise
            print(f"retry {path} after attempt {attempt} failed", flush=True)


def run_public_acquisition(root, out_dir, limit=None):
    import duckdb

    root = Path(root)
    out_dir = Path(out_dir)
    manifest_path = out_dir / "split-acquisition-manifest.json"
    if manifest_path.exists():
        raise FileExistsError(f"refusing to overwrite {manifest_path}")
    metadata = json.loads((out_dir / "train-source-metadata.json").read_text(encoding="utf-8"))
    sources = sorted(metadata["files"], key=lambda row: row["path"])
    if limit is not None:
        sources = sources[:limit]
    work = out_dir / "work"
    work.mkdir(parents=True, exist_ok=True)
    database_path = work / "public.duckdb"
    con = duckdb.connect(str(database_path))
    con.execute("SET threads TO 4")
    con.execute("SET memory_limit = '8GB'")
    con.execute(f"SET temp_directory = '{(work / 'tmp').as_posix()}'")
    con.execute("CREATE TABLE IF NOT EXISTS public (url VARCHAR, split VARCHAR)")
    con.execute("CREATE TABLE IF NOT EXISTS acquired_shards (path VARCHAR PRIMARY KEY, rows BIGINT, bytes BIGINT, sha256 VARCHAR, url VARCHAR)")
    con.execute("CREATE TABLE IF NOT EXISTS acquired_validation (name VARCHAR PRIMARY KEY)")
    completed = {row[0] for row in con.execute("SELECT path FROM acquired_shards").fetchall()}
    started = time.monotonic()
    for index, source in enumerate(sources, start=1):
        if source["path"] in completed:
            continue
        result = stream_train_shard(con, source)
        print(f"train shard {index}/{len(sources)}: {result['rows']} rows, {result['bytes']} bytes, {result['sha256']}", flush=True)

    if limit is None:
        validation_receipts = []
        for name in ("validation-00000.parquet", "validation-00001.parquet"):
            path = root / "data/raw/c4/en" / name
            index = int(name.split("-")[1].split(".")[0])
            url = f"https://huggingface.co/api/datasets/allenai/c4/parquet/en/validation/{index}.parquet"
            validation_receipts.append(receipt(path, url, EXPECTED_SPLIT_BYTES[name], "C4 is ODC-BY; keep source files local.", EXPECTED_SPLIT_SHA256[name]))
            if con.execute("SELECT COUNT(*) FROM acquired_validation WHERE name = ?", [name]).fetchone()[0]:
                continue
            con.execute("BEGIN TRANSACTION")
            con.execute("INSERT INTO public SELECT url, 'validation' FROM read_parquet(?)", [str(path)])
            con.execute("INSERT INTO acquired_validation VALUES (?)", [name])
            con.execute("COMMIT")
        counts = dict(con.execute("SELECT split, COUNT(*) FROM public GROUP BY split").fetchall())
        assert counts == {"train": 364868892, "validation": 364608}, f"public counts differ: {counts}"
        con.execute("CHECKPOINT")
        train_receipts = [dict(zip(("path", "rows", "bytes", "sha256", "url"), row)) for row in con.execute("SELECT path, rows, bytes, sha256, url FROM acquired_shards ORDER BY path").fetchall()]
        for row in train_receipts:
            row["custody"] = "streamed; compressed body not retained"
        con.close()
        write_json(manifest_path, {
            "stage": "Stage 2 public split acquisition",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "amendment": "A1 streamed C4 train custody",
            "root_revision": SPLIT_ROOT_SHA,
            "train_source": "original JSON shards",
            "validation_source": "full Parquet conversion",
            "counts": counts,
            "train_inputs": train_receipts,
            "validation_inputs": validation_receipts,
            "derived_public_db": {
                "path": str(database_path.resolve()),
                "bytes": database_path.stat().st_size,
                "sha256": sha256(database_path),
            },
            "code_sha256": {
                "stage2_acquire.py": sha256(root / "src/stage2_acquire.py"),
                "stage2_audit.py": sha256(root / "src/stage2_audit.py"),
                "verify_stage2.py": sha256(root / "src/verify_stage2.py"),
            },
        })
        print(json.dumps({"status": "COMPLETE", "counts": counts, "database": str(database_path)}, indent=2))
    else:
        counts = dict(con.execute("SELECT split, COUNT(*) FROM public GROUP BY split").fetchall())
        con.close()
        print(json.dumps({"status": "BENCHMARK", "counts": counts, "seconds": time.monotonic() - started}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    run_public_acquisition(args.root, args.out_dir, args.limit)


if __name__ == "__main__":
    main()
