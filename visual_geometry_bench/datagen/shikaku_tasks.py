"""Shikaku puzzle data generation utilities.

Converts pre-generated rectangles puzzles into evaluation records following the
Visual Geometry Bench conventions described in ``task_creation.md``.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

from visual_geometry_bench.datagen.utils import compute_content_hash

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _resolve_dataset_path(dataset_path: str) -> Path:
    path = Path(dataset_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


@lru_cache(maxsize=8)
def _load_dataset(dataset_path: str) -> List[dict]:
    path = _resolve_dataset_path(dataset_path)
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        raise ValueError(f"Shikaku dataset must contain a list of records: {path}")
    return data


def _select_puzzle(records: Sequence[dict], *, puzzle_id: str | None, puzzle_index: int | None) -> Tuple[dict, int]:
    if puzzle_id is not None:
        for idx, rec in enumerate(records):
            if rec.get("id") == puzzle_id:
                return rec, idx
        raise ValueError(f"puzzle_id '{puzzle_id}' not found in dataset")
    if puzzle_index is None:
        raise AssertionError("datagen_args must include either 'puzzle_id' or 'puzzle_index'")
    if puzzle_index < 0 or puzzle_index >= len(records):
        raise ValueError(f"puzzle_index {puzzle_index} out of range (dataset has {len(records)} records)")
    return records[puzzle_index], puzzle_index


def load_puzzle(datagen_args: dict) -> Tuple[dict, int]:
    """Return the puzzle dict and index referenced by datagen_args."""

    dataset_path = datagen_args.get("dataset_path")
    assert isinstance(dataset_path, str) and dataset_path, "datagen_args missing valid 'dataset_path'"

    puzzle_id = datagen_args.get("puzzle_id")
    puzzle_index = datagen_args.get("puzzle_index")
    if puzzle_id is not None and not isinstance(puzzle_id, str):
        raise AssertionError("'puzzle_id' must be a string if provided")
    if puzzle_index is not None:
        try:
            puzzle_index = int(puzzle_index)
        except (TypeError, ValueError) as exc:  # pragma: no cover - defensive
            raise AssertionError("'puzzle_index' must be an integer") from exc

    records = _load_dataset(dataset_path)
    puzzle, idx = _select_puzzle(records, puzzle_id=puzzle_id, puzzle_index=puzzle_index)
    return puzzle, idx


def _format_grid(numbers: Sequence[Sequence[int]]) -> str:
    return "\n".join(" ".join(str(cell) for cell in row) for row in numbers)


def make_prompt(datagen_args: dict) -> str:
    """Construct the natural-language prompt describing the puzzle."""

    puzzle, _ = load_puzzle(datagen_args)
    width = puzzle["width"]
    height = puzzle["height"]
    grid_text = _format_grid(puzzle["numbers"])

    lines = [
        f"Solve the Shikaku puzzle on a {height}×{width} grid.",
        "Cells contain numbers indicating the area of the rectangle that must cover them;",
        "all blank cells are denoted by 0.",
        "Grid (rows listed top to bottom, values space-separated):",
        grid_text,
        "",
        "Return the solution as a Python list of bounding boxes.",
        "Each rectangle must be [left_col, top_row, right_col, bottom_row] using 0-indexed inclusive coordinates.",
        "Rectangles must exactly partition the grid and each must contain exactly one clue equal to its area.",
        "Before presenting the final list, begin your response with <thinking>...</thinking> containing your full chain of thought or reasoning for your answer.",
    ]
    return "\n".join(lines)


def _canonical_rectangles(rectangles: Iterable[dict]) -> List[List[int]]:
    ordered: List[List[int]] = []
    for rect in rectangles:
        top = int(rect["top"])
        left = int(rect["left"])
        height = int(rect["height"])
        width = int(rect["width"])
        bottom = top + height - 1
        right = left + width - 1
        ordered.append([left, top, right, bottom])
    ordered.sort()
    return ordered


def get_solutions(datagen_args: dict) -> List[List[int]]:
    """Return the canonical list of rectangles for the specified puzzle."""

    puzzle, _ = load_puzzle(datagen_args)
    return _canonical_rectangles(puzzle.get("solution_rectangles", []))


def generate_dataset_record(
    datagen_args: dict,
    *,
    record_id: str | None = None,
    tags: Sequence[str] | None = None,
    difficulty: str | None = None,
    requires_visual: bool = True,
) -> Dict[str, object]:
    """Generate an evaluation record following Visual Geometry Bench schema."""

    puzzle, idx = load_puzzle(datagen_args)
    dataset_path = str(datagen_args["dataset_path"])
    prompt = make_prompt(datagen_args)
    ground_truth = get_solutions(datagen_args)

    hash_args = {
        "dataset_path": dataset_path,
        "puzzle_id": puzzle["id"],
        "puzzle_index": idx,
    }

    rid = record_id or compute_content_hash(
        problem_type="shikaku_rectangles",
        datagen_args=hash_args,
        prompt=prompt,
        ground_truth=ground_truth,
    )

    metadata = {
        "problem_type": "shikaku_rectangles",
        "tags": sorted(set(tags or ("shikaku", "rectangles", "grid"))),
        "difficulty": difficulty or "",
        "requires_visual": bool(requires_visual),
        "grid_shape": [puzzle["height"], puzzle["width"]],
    }

    record_datagen_args = {
        "dataset_path": dataset_path,
        "puzzle_id": puzzle["id"],
        "puzzle_index": idx,
    }

    return {
        "id": rid,
        "prompt": prompt,
        "ground_truth": ground_truth,
        "metadata": metadata,
        "datagen_args": record_datagen_args,
        "puzzle": {
            "numbers": puzzle["numbers"],
            "width": puzzle["width"],
            "height": puzzle["height"],
        },
    }
