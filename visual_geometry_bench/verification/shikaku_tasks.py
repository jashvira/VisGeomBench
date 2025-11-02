"""Verification logic for Shikaku bounding-box solutions.

Answer format (model output): JSON or Python literal list of
[left_col, top_row, right_col, bottom_row] entries, 0-indexed, inclusive.
Each rectangle must:
- Stay within the puzzle bounds.
- Exactly partition the grid (no overlap, full coverage).
- Contain exactly one clue equal to its area.
"""

from __future__ import annotations

import ast
import json
from typing import Iterable, List, Sequence


def _parse_boxes(raw: str) -> list[list[int]] | None:
    """Parse model output expecting a list of bounding boxes."""

    text = raw.strip()
    if not text:
        return None

    # Try JSON first
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed  # type: ignore[return-value]
    except (json.JSONDecodeError, TypeError):
        pass

    # Fallback to Python literal
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list):
            return parsed  # type: ignore[return-value]
    except (SyntaxError, ValueError):
        pass

    return None


def _validate_box_structure(boxes: list) -> tuple[bool, str]:
    """Ensure boxes is a list of 4-int lists with sane ordering."""

    if not isinstance(boxes, list):
        return False, "not_a_list"

    for idx, box in enumerate(boxes):
        if not isinstance(box, (list, tuple)):
            return False, f"box_{idx}_not_sequence"
        if len(box) != 4:
            return False, f"box_{idx}_wrong_length"
        try:
            left, top, right, bottom = [int(v) for v in box]
        except (TypeError, ValueError):
            return False, f"box_{idx}_non_integer"
        if left < 0 or top < 0 or right < 0 or bottom < 0:
            return False, f"box_{idx}_negative"
        if right < left or bottom < top:
            return False, f"box_{idx}_invalid_order"
    return True, ""


def _canonicalise(boxes: Iterable[Sequence[int]]) -> List[List[int]]:
    """Convert bounding boxes to canonical integer form sorted lexicographically."""

    canonical = [[int(box[0]), int(box[1]), int(box[2]), int(box[3])] for box in boxes]
    canonical.sort()
    return canonical


def _check_partition(
    boxes: Iterable[Sequence[int]],
    numbers: Sequence[Sequence[int]],
) -> tuple[bool, str]:
    """Validate coverage and clue constraints."""

    if not numbers or not numbers[0]:
        return False, "empty_puzzle"

    height = len(numbers)
    width = len(numbers[0])
    coverage = [[0] * width for _ in range(height)]

    for idx, box in enumerate(boxes):
        left, top, right, bottom = map(int, box)

        if right >= width or bottom >= height:
            return False, f"box_{idx}_out_of_bounds"

        area = (right - left + 1) * (bottom - top + 1)
        clues = []
        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                coverage[y][x] += 1
                if coverage[y][x] > 1:
                    return False, f"box_{idx}_overlap"
                val = numbers[y][x]
                if isinstance(val, int) and val > 0:
                    clues.append(val)

        if len(clues) != 1:
            return False, f"box_{idx}_clue_count_{len(clues)}"
        if clues[0] != area:
            return False, f"box_{idx}_clue_mismatch"

    for y, row in enumerate(coverage):
        for x, count in enumerate(row):
            if count != 1:
                return False, f"cell_{y}_{x}_uncovered"
    return True, ""


def _compare(
    pred: List[List[int]],
    truth: List[List[int]],
    *,
    return_diff: bool,
) -> bool | dict:
    if not return_diff:
        return pred == truth

    missing = [box for box in truth if box not in pred]
    extra = [box for box in pred if box not in truth]
    return {
        "passed": not missing and not extra,
        "missing": missing,
        "extra": extra,
        "errors": [],
    }


def verify_shikaku(
    model_output: str,
    record: dict,
    *,
    return_diff: bool = False,
) -> bool | dict:
    """Verify model predictions for Shikaku bounding boxes."""

    parsed = _parse_boxes(model_output)
    if parsed is None:
        if return_diff:
            return {"passed": False, "missing": [], "extra": [], "errors": ["parse_failure"]}
        return False

    valid, error = _validate_box_structure(parsed)
    if not valid:
        if return_diff:
            return {"passed": False, "missing": [], "extra": [], "errors": [error]}
        return False

    canonical_pred = _canonicalise(parsed)
    ground_truth = record.get("ground_truth")
    if not isinstance(ground_truth, list):
        if return_diff:
            return {"passed": False, "missing": [], "extra": [], "errors": ["ground_truth_not_list"]}
        return False
    canonical_truth = _canonicalise(ground_truth)

    puzzle = record.get("puzzle") or {}
    numbers = puzzle.get("numbers")
    if not isinstance(numbers, list):
        if return_diff:
            return {"passed": False, "missing": [], "extra": [], "errors": ["missing_puzzle_numbers"]}
        return False

    partition_ok, partition_error = _check_partition(canonical_pred, numbers)
    if not partition_ok:
        if return_diff:
            return {"passed": False, "missing": [], "extra": [], "errors": [partition_error]}
        return False

    return _compare(canonical_pred, canonical_truth, return_diff=return_diff)
