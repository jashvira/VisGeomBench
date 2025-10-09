"""Verification for topology enumeration model outputs.

Semantics:
- Format: Python list of 4-tuples of ints, values in [0..n_classes-1].
- Order: (1) lengths match, (2) label sets match, (3) canonicalised sets match.
- Canonicalisation: first-occurrence relabelling; tuple order matters, list order doesn't.
- Pass: canonicalised(pred) == canonicalised(gt); no subset scoring.
- return_diff=False: early exits for efficiency; return_diff=True: full diagnostics.
"""

from __future__ import annotations

import ast

from visual_geometry_bench.datagen.topology_enumeration import canonicalize


def parse_model_output_topology_enumeration(raw: str) -> list[tuple[int, int, int, int]] | None:
    """Parse model output expecting a Python list of 4-tuples of ints.

    Args:
        raw: Raw model output string

    Returns:
        Parsed list of 4-tuples, or None on any violation
    """
    try:
        parsed = ast.literal_eval(raw.strip())
    except (ValueError, SyntaxError):
        return None

    if not isinstance(parsed, list):
        return None

    result = []
    for item in parsed:
        if not isinstance(item, tuple) or len(item) != 4:
            return None
        if not all(isinstance(x, int) for x in item):
            return None
        result.append(item)

    return result


def verify_topology_enumeration(model_output: str, record: dict, *, return_diff: bool = False) -> bool | dict:
    """Verify model output matches ground truth exactly (set equality).

    Args:
        model_output: Raw model output string
        record: Dataset record with ground_truth and datagen_args
        return_diff: If True, return detailed diagnostic dict instead of bool

    Returns:
        If return_diff=False: True if exact match, False otherwise
        If return_diff=True: Dict with keys:
            - passed (bool): Whether verification passed
            - missing (list): Canonical tuples in ground truth but not in prediction
            - extra (list): Canonical tuples in prediction but not in ground truth
            - errors (list): Parse or validation error messages
            - details (dict): Metadata including lengths, label sets, counts, and mismatches
    """
    # Parse prediction
    parsed = parse_model_output_topology_enumeration(model_output)
    if parsed is None:
        if return_diff:
            return {
                "passed": False,
                "missing": [],
                "extra": [],
                "errors": ["parse_failure"],
                "details": {"raw_output": model_output[:200]},
            }
        return False

    # Ground truth setup
    gt_list = record["ground_truth"]
    n_classes = record["datagen_args"]["n_classes"]

    # Lengths
    pred_len = len(parsed)
    gt_len = len(gt_list)

    if not return_diff and pred_len != gt_len:
        return False

    # Collect labels, validate range, canonicalise in one pass
    valid_range = set(range(n_classes))
    pred_labels = set()
    pred_set = set()
    validation_errors = [] if return_diff else None

    for cfg in parsed:
        cfg_tuple = tuple(cfg)
        # Range validation
        invalid = not all(val in valid_range for val in cfg_tuple)
        if invalid:
            if return_diff:
                validation_errors.append({
                    "config": list(cfg_tuple),
                    "reason": f"values not in [0, {n_classes-1}]"
                })
                continue
            return False
        # Collect labels and canonicalise
        pred_labels.update(cfg_tuple)
        pred_set.add(canonicalize(cfg_tuple))

    if return_diff and validation_errors:
        return {
            "passed": False,
            "missing": [],
            "extra": [],
            "errors": [f"{len(validation_errors)} validation issue(s)"],
            "details": {"issues": validation_errors},
        }

    # Ground truth labels and canonical set in one pass
    gt_labels = set()
    gt_set = set()
    for cfg in gt_list:
        cfg_tuple = tuple(cfg)
        gt_labels.update(cfg_tuple)
        gt_set.add(canonicalize(cfg_tuple))

    if not return_diff and pred_labels != gt_labels:
        return False

    # Compare canonical sets
    if return_diff:
        length_ok = pred_len == gt_len
        labels_ok = pred_labels == gt_labels
        missing = sorted(gt_set - pred_set)
        extra = sorted(pred_set - gt_set)
        sets_ok = len(missing) == 0 and len(extra) == 0
        passed = length_ok and labels_ok and sets_ok

        details = {
            "pred_len": pred_len,
            "gt_len": gt_len,
            "pred_label_set": sorted(pred_labels),
            "gt_label_set": sorted(gt_labels),
            "canonical_count": len(pred_set),
            "ground_truth_count": len(gt_set),
        }
        if not length_ok:
            details["length_mismatch"] = {"expected": gt_len, "actual": pred_len}
        if not labels_ok:
            details["label_set_diff"] = {
                "missing_labels": sorted(gt_labels - pred_labels),
                "extra_labels": sorted(pred_labels - gt_labels),
            }

        return {
            "passed": passed,
            "missing": [list(t) for t in missing],
            "extra": [list(t) for t in extra],
            "errors": [],
            "details": details,
        }

    return pred_set == gt_set
