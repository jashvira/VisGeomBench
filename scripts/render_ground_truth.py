"""Render ground-truth visualisations for every record in a dataset JSONL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from visualisations import visualise_record
from visualisations.render import RenderMode


def _iter_records(dataset_path: Path):
    with dataset_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="Path to dataset JSONL file")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/figures/questions"),
        help="Directory to write rendered figures (default: data/figures/questions)",
    )
    parser.add_argument("--fmt", default="png", help="Image format (default: png)")
    parser.add_argument(
        "--detail",
        action="store_true",
        help="Render in detail mode (passes detail=True to the renderer)",
    )
    parser.add_argument(
        "--suffix",
        default="gt",
        help="Suffix appended to the record id for the output filename",
    )
    parser.add_argument(
        "--metadata-caption",
        default=None,
        help="Optional caption rendered under each figure",
    )
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    for record in _iter_records(args.dataset):
        record_id = record.get("id", "record")
        stub = f"{record_id}_{args.suffix}" if args.suffix else record_id
        visualise_record(
            record,
            answer=None,
            detail=args.detail,
            save_dir=args.out,
            fmt=args.fmt,
            output_stub=stub,
            metadata_caption=args.metadata_caption,
            mode=RenderMode.GROUND_TRUTH,
        )


if __name__ == "__main__":
    main()

