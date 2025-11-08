"""Render two-segment datasets with consistent fake answers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

from visualisations import visualise_record


def _load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def _canonical_corners(datagen_args: dict[str, Any]) -> list[tuple[float, float]]:
    corners: Iterable[Iterable[float]] | None = datagen_args.get("corners")
    if corners:
        parsed = [tuple(float(v) for v in point) for point in corners]
        if len(parsed) >= 4:
            return parsed[:4]
    # Fallback to unit square
    return [
        (0.0, 0.0),
        (1.0, 0.0),
        (1.0, 1.0),
        (0.0, 1.0),
    ]


def _midpoint(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    return ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)


def _fake_answer(record: dict[str, Any]) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    datagen_args = record.get("datagen_args", {})
    corners = _canonical_corners(datagen_args)
    edges = list(zip(corners, corners[1:] + corners[:1]))
    midpoints = [_midpoint(a, b) for a, b in edges]
    if len(midpoints) < 4:
        # Degenerate fallback: connect opposite corners
        return [(corners[0], corners[2]), (corners[1], corners[3])]
    return [
        (midpoints[0], midpoints[2]),
        (midpoints[1], midpoints[3]),
    ]


def render_dataset(jsonl_path: Path, output_dir: Path) -> None:
    records = _load_records(jsonl_path)
    if not records:
        print(f"No records found in {jsonl_path}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    for idx, record in enumerate(records, 1):
        record_id = record.get("id", f"record_{idx}")
        gt_stub = f"{record_id}_gt"
        fake_stub = f"{record_id}_fake"

        visualise_record(
            record,
            None,
            detail=False,
            save_dir=output_dir,
            fmt="png",
            output_stub=gt_stub,
            metadata_caption=None,
        )

        fake_answer = _fake_answer(record)
        visualise_record(
            record,
            fake_answer,
            detail=False,
            save_dir=output_dir,
            fmt="png",
            output_stub=fake_stub,
            metadata_caption=None,
        )
        print(f"[{idx:02d}] Rendered {record_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="Path to two-segments JSONL dataset")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/figures/two_segments_curated"),
        help="Output directory for figures",
    )
    args = parser.parse_args()
    render_dataset(args.dataset, args.out)


if __name__ == "__main__":
    main()

