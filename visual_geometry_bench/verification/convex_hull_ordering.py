"""Verification for convex hull ordering task outputs.

Semantics:
- Expected answer: Python/JSON list of integer vertex indices.
- Vertices must be unique, length >= 3, indices >= 0.
- Canonical order: counter-clockwise hull, rotated so the smallest index appears first.
- Pass criterion: canonicalised prediction == canonicalised ground truth.
- return_diff=True surfaces diagnostics (parse/format errors, missing/extra indices).
"""

from __future__ import annotations

import ast
import json
from typing import Iterable, List, Sequence


def _parse_index_list(raw: str) -> list[int] | None:
    """Parse raw model output into a list of integers."""
    text = raw.strip()
    if not text:
        return None

    # Try JSON first, then Python literal.
    for parser in (json.loads, ast.literal_eval):
        try:
            parsed = parser(text)
        except (ValueError, SyntaxError, json.JSONDecodeError):
            continue
        if isinstance(parsed, list):
            return parsed
    return None


def _is_valid_index_sequence(seq: Sequence[object]) -> bool:
    """Return True if seq is a list-like of non-negative ints with >=3 unique entries."""
    if not isinstance(seq, list):
        return False
    if len(seq) < 3:
        return False
    seen: set[int] = set()
    for item in seq:
        if not isinstance(item, int) or item < 0:
            return False
        if item in seen:
            return False
        seen.add(item)
    return True


def _rotate_to_min_start(indices: Iterable[int]) -> List[int]:
    """Rotate indices so that the smallest element appears first."""
    idx_list = list(indices)
    min_idx = min(idx_list)
    start = idx_list.index(min_idx)
    return idx_list[start:] + idx_list[:start]


def _canonicalise(indices: Iterable[int]) -> List[int]:
    """Canonicalise vertex order (rotate to start at the minimum index).

    Dataset ground truth is already counter-clockwise, so we simply rotate the
    prediction the same way for comparison; clockwise submissions remain
    distinct, which is intended.
    """
    rotated = _rotate_to_min_start(indices)
    return rotated


def _compare_indices(pred: list[int], gt: list[int], *, return_diff: bool) -> bool | dict:
    pred_canon = _canonicalise(pred)
    gt_canon = _canonicalise(gt)

    if pred_canon == gt_canon:
        if return_diff:
            return {"passed": True, "missing": [], "extra": [], "errors": []}
        return True

    if return_diff:
        pred_set = set(pred_canon)
        gt_set = set(gt_canon)
        missing = sorted(gt_set - pred_set)
        extra = sorted(pred_set - gt_set)
        errors: list[str] = []
        if pred_canon != gt_canon and not missing and not extra:
            # Same set but wrong canonical ordering (e.g. clockwise).
            errors.append("order_mismatch")
        return {
            "passed": False,
            "missing": missing,
            "extra": extra,
            "errors": errors,
        }

    return False


def verify_convex_hull_ordering(
    model_output: str, record: dict, *, return_diff: bool = False
) -> bool | dict:
    """Verify a convex hull vertex ordering prediction against ground truth."""
    parsed = _parse_index_list(model_output)
    if parsed is None:
        if return_diff:
            return {"passed": False, "missing": [], "extra": [], "errors": ["parse_failure"]}
        return False

    if not _is_valid_index_sequence(parsed):
        if return_diff:
            return {"passed": False, "missing": [], "extra": [], "errors": ["invalid_sequence"]}
        return False

    ground_truth = record.get("ground_truth")
    if not _is_valid_index_sequence(ground_truth):
        if return_diff:
            return {"passed": False, "missing": [], "extra": [], "errors": ["ground_truth_invalid"]}
        return False

    return _compare_indices(parsed, ground_truth, return_diff=return_diff)
