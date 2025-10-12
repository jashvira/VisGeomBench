"""Verification for topology edge tasks model outputs.

Semantics:
- Format: List (JSON or Python literal) matching square order from prompt.
- enumerate_edges: List of lists of [i,j] edge pairs (i < j); pair order within sublist not enforced.
- classify_behaviour: List of exact label strings.
- Valid labels: 'known behaviour', 'three domains meeting', 'ambiguous'.
- Pass: exact list equality (order-insensitive for edge pairs); no partial credit.
- return_diff=False: early exits; return_diff=True: full diagnostics.
"""

from __future__ import annotations

import ast
import json


def _parse_list(raw: str) -> list | None:
    """Parse model output expecting a list (JSON or Python literal).

    Args:
        raw: Raw model output string

    Returns:
        Parsed list, or None on any parse failure
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


def verify_topology_edge_tasks(
    model_output: str, record: dict, *, return_diff: bool = False
) -> bool | dict:
    """Verify model output matches ground truth list exactly.

    Args:
        model_output: Raw model output string (expected list)
        record: Dataset record with ground_truth list
        return_diff: If True, return detailed diagnostic dict instead of bool

    Returns:
        If return_diff=False: True if exact match, False otherwise
        If return_diff=True: Dict with keys:
            - passed (bool): Whether verification passed
            - missing (list): Indices with mismatches
            - errors (list): Parse or validation error messages
    """
    # Parse prediction
    parsed = _parse_list(model_output)
    if parsed is None:
        if return_diff:
            return {
                "passed": False,
                "missing": [],
                "errors": ["parse_failure"],
            }
        return False

    # Extract ground truth (expected to be a list)
    ground_truth = record.get("ground_truth", [])
    if not isinstance(ground_truth, list):
        if return_diff:
            return {"passed": False, "missing": [], "errors": ["ground_truth_not_list"]}
        return False

    # Length check
    if len(parsed) != len(ground_truth):
        if return_diff:
            return {
                "passed": False,
                "missing": [],
                "errors": [f"length_mismatch: expected {len(ground_truth)}, got {len(parsed)}"],
            }
        return False

    # Infer subtask from ground truth structure
    if not ground_truth:
        # Empty list - trivially pass
        return True if not return_diff else {"passed": True, "missing": [], "errors": []}

    first_elem = ground_truth[0]
    if isinstance(first_elem, list):
        subtask = "enumerate_edges"
    elif isinstance(first_elem, str):
        subtask = "classify_behaviour"
    else:
        if return_diff:
            return {"passed": False, "missing": [], "errors": ["unable_to_infer_subtask"]}
        return False

    # Compare element-wise
    errors = []
    missing_indices = []

    for idx, (pred, gt) in enumerate(zip(parsed, ground_truth)):
        if subtask == "enumerate_edges":
            # Validate pred format
            if not isinstance(pred, list):
                errors.append(f"idx_{idx}: not a list")
                if not return_diff:
                    return False
                continue

            # Validate pairs: each must be [i,j] with i < j
            valid = True
            for pair in pred:
                if not isinstance(pair, list) or len(pair) != 2:
                    errors.append(f"idx_{idx}: invalid pair format")
                    valid = False
                    break
                if not all(isinstance(x, int) for x in pair):
                    errors.append(f"idx_{idx}: non-integer in pair")
                    valid = False
                    break
                if pair[0] >= pair[1]:
                    errors.append(f"idx_{idx}: pair not sorted (i < j required)")
                    valid = False
                    break

            if not valid:
                if not return_diff:
                    return False
                continue

            # Compare (order-insensitive for pairs)
            pred_norm = sorted([list(p) for p in pred])
            gt_norm = sorted([list(p) for p in gt])
            if pred_norm != gt_norm:
                missing_indices.append(idx)
                if not return_diff:
                    return False

        elif subtask == "classify_behaviour":
            # Validate pred format
            if not isinstance(pred, str):
                errors.append(f"idx_{idx}: not a string")
                if not return_diff:
                    return False
                continue

            # Validate label
            if pred not in {"known behaviour", "three domains meeting", "ambiguous"}:
                errors.append(f"idx_{idx}: invalid label '{pred}'")
                if not return_diff:
                    return False
                continue

            # Compare
            if pred != gt:
                missing_indices.append(idx)
                if not return_diff:
                    return False

    # Early exit for non-diff mode
    if not return_diff:
        return len(errors) == 0 and len(missing_indices) == 0

    # Diff mode
    passed = len(errors) == 0 and len(missing_indices) == 0

    return {
        "passed": passed,
        "missing": missing_indices,
        "errors": errors,
    }

