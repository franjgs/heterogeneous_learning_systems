"""Fetch a pinned PACS snapshot, validate it, and write a local data manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from io import BytesIO
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from hls.b2_pacs_calibration import CLASSES, DOMAINS, SPLIT_FRACTIONS, stratified_splits  # noqa: E402

REPO_ID = "flwrlabs/pacs"
REVISION = "394113073258ead631f617d2e13bb377c0715c4b"
PARQUET_PATH = "data/train-00000-of-00001.parquet"
PARQUET_SHA256 = "4fc041ee92eec6043fe6e2859e8bdd138e5f958bc621afd153879812cbe65ff5"
PARQUET_BYTES = 191395900
SEEDS = (0, 1, 2, 3, 4)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/pilots/b2_pacs_calibration")
    parser.add_argument("--cache-dir", type=Path, default=Path.home() / ".cache/hls/pacs")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = args.cache_dir / REVISION
    cache_dir.mkdir(parents=True, exist_ok=True)
    parquet = Path(
        hf_hub_download(
            repo_id=REPO_ID,
            repo_type="dataset",
            filename=PARQUET_PATH,
            revision=REVISION,
        )
    )
    source_sha = sha256_file(parquet)
    if parquet.stat().st_size != PARQUET_BYTES or source_sha != PARQUET_SHA256:
        raise RuntimeError("downloaded PACS parquet does not match the pinned checksum")

    image_root = cache_dir / "images"
    rows: list[dict[str, object]] = []
    cells: Counter[tuple[str, int]] = Counter()
    hashes: set[str] = set()
    corrupt: list[dict[str, object]] = []
    missing = 0
    row_index = 0
    parquet_file = pq.ParquetFile(parquet)
    # The Arrow extension metadata carries labels; assert the explicit canonical map.
    metadata = parquet_file.schema_arrow.metadata or {}
    arrow_metadata = json.loads(metadata[b"huggingface"])
    observed_names = arrow_metadata["info"]["features"]["label"]["names"]
    if tuple(observed_names) != CLASSES:
        raise RuntimeError(f"unexpected PACS class metadata: {observed_names}")
    for batch in parquet_file.iter_batches(batch_size=64):
        for row in batch.to_pylist():
            domain = row["domain"]
            label = int(row["label"])
            image = row["image"]
            raw = image.get("bytes") if image else None
            source_path = image.get("path") if image else None
            if domain not in DOMAINS or label not in range(len(CLASSES)):
                raise RuntimeError(f"unexpected domain/class at row {row_index}: {domain}/{label}")
            cells[(domain, label)] += 1
            if raw is None:
                missing += 1
                row_index += 1
                continue
            digest = hashlib.sha256(raw).hexdigest()
            duplicate = digest in hashes
            hashes.add(digest)
            try:
                with Image.open(BytesIO(raw)) as im:
                    image_format = (im.format or "JPEG").lower()
                    width, height = im.size
                    im.verify()
            except Exception as exc:  # manifest the issue; do not silently drop data
                corrupt.append({"row": row_index, "domain": domain, "label": label, "error": str(exc)})
                row_index += 1
                continue
            extension = "jpg" if image_format in {"jpeg", "jpg"} else image_format
            relative_path = f"{domain}/{CLASSES[label]}/{row_index:05d}.{extension}"
            destination = image_root / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not destination.exists():
                destination.write_bytes(raw)
            rows.append(
                {
                    "sample_id": row_index,
                    "domain": domain,
                    "label": label,
                    "class_name": CLASSES[label],
                    "source_path": source_path,
                    "relative_path": relative_path,
                    "sha256": digest,
                    "width": width,
                    "height": height,
                    "format": image_format,
                    "duplicate_content": duplicate,
                }
            )
            row_index += 1

    manifest = pd.DataFrame(rows).sort_values("sample_id")
    if missing or corrupt or len(manifest) != parquet_file.metadata.num_rows or len(hashes) != len(manifest):
        raise RuntimeError(
            "PACS audit found missing/corrupt/duplicate rows; refusing to silently create a reduced manifest"
        )
    manifest.to_csv(args.output_dir / "dataset_manifest.csv", index=False)
    count_rows = [
        {"domain": domain, "label": label, "class_name": CLASSES[label], "count": cells[domain, label]}
        for domain in DOMAINS
        for label in range(len(CLASSES))
    ]
    pd.DataFrame(count_rows).to_csv(args.output_dir / "domain_class_counts.csv", index=False)
    split_rows = []
    for seed in SEEDS:
        splits = stratified_splits(manifest, seed)
        lookup = manifest.set_index("sample_id")
        for split, ids in splits.items():
            subset = lookup.loc[ids]
            split_rows.extend(
                {
                    "seed": seed,
                    "sample_id": int(sample_id),
                    "split": split,
                    "domain": row.domain,
                    "label": int(row.label),
                }
                for sample_id, row in subset.iterrows()
            )
    pd.DataFrame(split_rows).to_csv(args.output_dir / "split_manifest.csv", index=False)
    audit = {
        "status": "DATASET_VALIDATED",
        "source": {
            "repo_id": REPO_ID,
            "revision": REVISION,
            "file": PARQUET_PATH,
            "url": f"https://huggingface.co/datasets/{REPO_ID}/resolve/{REVISION}/{PARQUET_PATH}",
            "bytes": parquet.stat().st_size,
            "sha256": source_sha,
        },
        "rows": int(len(manifest)),
        "domains": {domain: int(sum(cells[domain, label] for label in range(len(CLASSES)))) for domain in DOMAINS},
        "classes": {str(label): name for label, name in enumerate(CLASSES)},
        "domain_class_counts": {
            domain: {CLASSES[label]: int(cells[domain, label]) for label in range(len(CLASSES))}
            for domain in DOMAINS
        },
        "splits": SPLIT_FRACTIONS,
        "split_seeds": list(SEEDS),
        "image_audit": {
            "missing_bytes": missing,
            "corrupt_or_unreadable": len(corrupt),
            "unique_raw_sha256": len(hashes),
            "duplicate_rows_by_exact_sha256": len(manifest) - len(hashes),
            "corrupt_examples": corrupt[:20],
        },
        "image_cache_relative_path": str(image_root),
        "note": "PACS dataset/image files remain outside the Git repository.",
    }
    (args.output_dir / "dataset_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
