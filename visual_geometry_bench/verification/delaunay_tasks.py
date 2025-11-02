"""Verification for Delaunay triangulation task model outputs.

Semantics:
- Format: List of triangles (JSON or Python literal), each triangle a 3-element list of integers.
- Each triangle must be sorted in ascending order.
- The list of triangles must be sorted lexicographically.
- Pass criterion: exact equality with ground truth after canonicalisation.
- return_diff=False: early exits for efficiency.
- return_diff=True: full diagnostics with missing/extra triangles.
"""

from __future__ import annotations

from collections import Counter
import ast
import json


def _parse_triangulation(raw: str) -> list[list[int]] | None:
    """Parse model output expecting a list of triangle index triples.

    Args:
        raw: Raw model output string

    Returns:
        Parsed list of triangles, or None on parse failure
    """
    # Try JSON first
    try:
        parsed = json.loads(raw.strip())
        if isinstance(parsed, list):
            return parsed
    except (json.JSONDecodeError, ValueError):
        pass

    # Fallback to Python literal eval
    try:
        parsed = ast.literal_eval(raw.strip())
        if isinstance(parsed, list):
            return parsed
    except (ValueError, SyntaxError):
        pass

    return None


def _validate_triangulation_format(triangles: list) -> tuple[bool, str]:
    """Validate that triangles is a well-formed list of integer triples.

    Args:
        triangles: Parsed triangulation candidate

    Returns:
        (is_valid, error_message) tuple
    """
    if not isinstance(triangles, list):
        return False, "not_a_list"

    for i, tri in enumerate(triangles):
        if not isinstance(tri, list):
            return False, f"triangle_{i}_not_list"
        if len(tri) != 3:
            return False, f"triangle_{i}_wrong_length"
        if not all(isinstance(idx, int) and idx >= 0 for idx in tri):
            return False, f"triangle_{i}_invalid_indices"

    return True, ""


def _canonicalise_triangulation(triangles: list[list[int]]) -> list[list[int]]:
    """Canonicalise triangulation: sort each triangle, then sort the list.

    Args:
        triangles: List of triangle index triples

    Returns:
        Canonicalised triangulation
    """
    return sorted([sorted(tri) for tri in triangles])


def _compare_triangulations(
    pred: list[list[int]], gt: list[list[int]], *, return_diff: bool
) -> bool | dict:
    """Compare canonicalised triangulations, optionally returning diagnostics."""

    pred_counter = Counter(map(tuple, pred))
    gt_counter = Counter(map(tuple, gt))

    if not return_diff:
        return pred_counter == gt_counter

    missing = sorted(
        [list(tri) for tri, count in (gt_counter - pred_counter).items() for _ in range(count)]
    )
    extra = sorted(
        [list(tri) for tri, count in (pred_counter - gt_counter).items() for _ in range(count)]
    )

    return {
        "passed": not missing and not extra,
        "missing": missing,
        "extra": extra,
        "errors": [],
    }


def verify_delaunay_triangulation(
    model_output: str, record: dict, *, return_diff: bool = False
) -> bool | dict:
    """Verify model output matches ground truth Delaunay triangulation.

    Args:
        model_output: Raw model output string (expected list of triangles)
        record: Dataset record with ground_truth triangulation
        return_diff: If True, return detailed diagnostic dict instead of bool

    Returns:
        If return_diff=False: True if exact match, False otherwise
        If return_diff=True: Dict with keys:
            - passed (bool): Whether verification passed
            - missing (list): Triangles in ground truth but not in prediction
            - extra (list): Triangles in prediction but not in ground truth
            - errors (list): Parse or validation error messages
    """
    # Parse prediction
    parsed = _parse_triangulation(model_output)
    if parsed is None:
        if return_diff:
            return {
                "passed": False,
                "missing": [],
                "extra": [],
                "errors": ["parse_failure"],
            }
        return False

    # Validate format
    valid, error_msg = _validate_triangulation_format(parsed)
    if not valid:
        if return_diff:
            return {
                "passed": False,
                "missing": [],
                "extra": [],
                "errors": [error_msg],
            }
        return False

    # Extract and validate ground truth
    ground_truth = record.get("ground_truth", [])
    if not isinstance(ground_truth, list):
        if return_diff:
            return {
                "passed": False,
                "missing": [],
                "extra": [],
                "errors": ["ground_truth_not_list"],
            }
        return False

    # Canonicalise both
    pred_canonical = _canonicalise_triangulation(parsed)
    gt_canonical = _canonicalise_triangulation(ground_truth)

    return _compare_triangulations(pred_canonical, gt_canonical, return_diff=return_diff)
