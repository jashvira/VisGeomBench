"""Verification for half-subdivision neighbour labelling task.

Model output must be a collection of leaf labels (strings of 0/1, or "")
identifying every rectangle that shares a non-zero-length boundary with the
target leaf. Order is irrelevant, duplicates are forbidden.
"""

from __future__ import annotations

import ast
import json
from typing import Iterable, List, Sequence


def _normalise_token(token) -> str | None:
    if token is None:
        return None
    if isinstance(token, (int, float)) and not isinstance(token, bool):
        if isinstance(token, float) and not token.is_integer():
            return None
        token = str(int(token))
    elif isinstance(token, str):
        token = token.strip()
    else:
        return None

    if token in {"", '""'}:
        return ""

    if all(ch in "01" for ch in token) and token:
        return token
    return None


def _parse_sequence(raw: str) -> List[str] | None:
    text = raw.strip()
    if not text:
        return []

    def _from_iterable(items: Iterable) -> List[str] | None:
        normalised: list[str] = []
        seen: set[str] = set()
        for token in items:
            label = _normalise_token(token)
            if label is None or label in seen:
                return None
            seen.add(label)
            normalised.append(label)
        return normalised

    # Strategy 1: JSON array
    try:
        parsed = json.loads(text)
        if isinstance(parsed, Sequence) and not isinstance(parsed, (str, bytes)):
            result = _from_iterable(parsed)
            if result is not None:
                return result
    except (json.JSONDecodeError, TypeError):
        pass

    # Strategy 2: Python literal
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, Sequence) and not isinstance(parsed, (str, bytes)):
            result = _from_iterable(parsed)
            if result is not None:
                return result
    except (SyntaxError, ValueError):
        pass

    # Strategy 3: comma / whitespace separated tokens
    candidates = [tok.strip() for tok in text.replace("\n", ",").split(",") if tok.strip()]
    if not candidates:
        return None
    result = _from_iterable(candidates)
    if result is not None:
        return result

    return None


def _compare(pred: List[str], truth: List[str], *, return_diff: bool) -> bool | dict:
    truth_set = set(truth)
    pred_set = set(pred)

    if not return_diff:
        return pred_set == truth_set

    missing = sorted(truth_set - pred_set)
    extra = sorted(pred_set - truth_set)
    return {
        "passed": not missing and not extra,
        "missing": missing,
        "extra": extra,
        "errors": [],
    }


def verify_half_subdivision_neighbours(
    model_output: str,
    record: dict,
    *,
    return_diff: bool = False,
) -> bool | dict:
    """Verify neighbour lists for half-subdivision tasks."""

    if not isinstance(model_output, str):
        if return_diff:
            return {"passed": False, "missing": [], "extra": [], "errors": ["output_not_str"]}
        return False

    parsed = _parse_sequence(model_output)
    if parsed is None:
        if return_diff:
            return {"passed": False, "missing": [], "extra": [], "errors": ["parse_failure"]}
        return False

    ground_truth = record.get("ground_truth")
    if not isinstance(ground_truth, list):
        if return_diff:
            return {"passed": False, "missing": [], "extra": [], "errors": ["ground_truth_not_list"]}
        return False

    truth_labels: list[str] = []
    for label in ground_truth:
        norm = _normalise_token(label)
        if norm is None:
            if return_diff:
                return {"passed": False, "missing": [], "extra": [], "errors": ["invalid_ground_truth"]}
            return False
        truth_labels.append(norm)

    return _compare(parsed, truth_labels, return_diff=return_diff)


__all__ = ["verify_half_subdivision_neighbours"]
