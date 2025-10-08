"""Topology enumeration problems: corner labelings that force class intersections.

Problems ask which corner-label configurations of a unit square guarantee that
distinct classes must meet inside the square, given only corner observations
and the assumption of continuous boundaries.
"""

from __future__ import annotations

import hashlib
import json


# Canonical corner order used internally for storing solutions
_CANONICAL_CORNER_ORDER = ("bottom-left", "bottom-right", "top-right", "top-left")

# Ground truth solutions for n=2: configurations forcing 2 classes to meet inside.
# Stored in canonical corner order.
_SOLUTIONS_TWO_CLASSES: list[tuple[int, int, int, int]] = [
    (1, 0, 0, 0),
    (0, 1, 0, 0),
    (0, 0, 1, 0),
    (0, 0, 0, 1),
    (0, 0, 1, 1),
    (0, 1, 1, 0),
    (0, 1, 0, 1),
]

# Ground truth solutions for n=3: configurations forcing 3 classes to meet at a point inside.
# Stored in canonical corner order.
_SOLUTIONS_THREE_CLASSES: list[tuple[int, int, int, int]] = [
    (0, 0, 1, 2),
    (1, 0, 0, 2),
    (1, 2, 0, 0),
    (0, 1, 2, 0),
]


def _corner_order_permutation(corner_order: tuple[str, str, str, str]) -> tuple[int, int, int, int]:
    """Compute index permutation to map canonical corner order to the requested order.

    Returns a 4-tuple of indices describing how to reorder configurations.
    Example: if corner_order = ("top-left", "bottom-left", ...), returns (3, 0, ...).
    """
    _validate_corner_order(corner_order)
    return tuple(corner_order.index(corner) for corner in _CANONICAL_CORNER_ORDER)


def _validate_corner_order(corner_order: tuple[str, str, str, str]) -> None:
    """Ensure the provided corner_order is a permutation of the canonical names.

    Raises:
        ValueError: If corner_order is not a permutation of the canonical order
    """
    if (
        not isinstance(corner_order, tuple)
        or len(corner_order) != 4
        or set(corner_order) != set(_CANONICAL_CORNER_ORDER)
    ):
        raise ValueError(
            "corner_order must be a permutation of ('bottom-left','bottom-right','top-right','top-left')"
        )


def _permute_config(config: tuple[int, int, int, int], perm: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    """Apply an index permutation to reorder a configuration tuple.

    Args:
        config: Configuration to permute
        perm: Index permutation (4-tuple of indices)

    Returns:
        Reordered configuration
    """
    return tuple(config[perm[i]] for i in range(4))


def _relabel_first_occurrence(config: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    """Relabel configuration to 0..k-1 in first-occurrence (left-to-right) order.

    This implements the core canonicalisation: scanning left-to-right, the first
    unseen label becomes 0, the next becomes 1, and so on.

    Example: (7, 5, 7, 3) -> (0, 1, 0, 2)
    """
    seen = {}
    next_label = 0
    result = []
    for label in config:
        if label not in seen:
            seen[label] = next_label
            next_label += 1
        result.append(seen[label])
    return tuple(result)


def canonicalize(config: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    """Canonicalise a configuration to a standard form by first-occurrence relabelling.

    Maps any relabelling of the same pattern to a unique representative, so that
    (1,0,0,0), (7,5,5,5), (99,42,42,42) all map to (0,1,1,1).

    Args:
        config: A 4-tuple of integer labels

    Returns:
        The canonical form (first-occurrence relabelling)

    Example:
        >>> canonicalize((7, 5, 7, 3))
        (0, 1, 0, 2)
    """
    return _relabel_first_occurrence(config)


def make_prompt(
    n_classes: int,
    corner_order: tuple[str, str, str, str] = _CANONICAL_CORNER_ORDER,
) -> str:
    """Generate the problem prompt for topology enumeration.

    Asks for all corner-label configurations that guarantee n distinct classes
    must meet inside the square, given the specified corner reading order.

    Args:
        n_classes: Number of classes (2 or 3)
        corner_order: Corner reading order for the prompt

    Returns:
        Prompt string describing the problem

    Raises:
        ValueError: If n_classes is not 2 or 3, or corner_order is invalid
    """
    if n_classes not in (2, 3):
        raise ValueError("n_classes must be 2 or 3")
    _validate_corner_order(corner_order)

    meet_phrase = (
        "meet somewhere inside the square" if n_classes == 2
        else "meet at some point strictly inside the square"
    )

    corners_text = f"({', '.join(corner_order)})"

    return (
        "You are given a unit square with corners ordered "
        f"{corners_text}. Each corner is labeled from {{0, 1, 2...}}. Boundaries "
        "inside may be any continuous curves; only corner labels are observed.\n\n"
        f"Assume exactly {n_classes} distinct classes occur anywhere in or on the square.\n\n"
        f"List all corner-label configurations (4-tuples, in the order above) that are "
        f"sufficient to guarantee that {n_classes} distinct classes {meet_phrase}. "
        "Canonicalisation: relabel by first occurrence (scan left-to-right; first new "
        "label -> 0, next -> 1, ...). Treat any label renamings as identical; list each "
        "equivalence class once.\n\n"
        "Strict output: a Python-style list of 4-tuples only."
    )


def get_solutions(
    n_classes: int,
    corner_order: tuple[str, str, str, str] = _CANONICAL_CORNER_ORDER,
) -> list[tuple[int, int, int, int]]:
    """Return ground truth solutions for the given class count and corner order.

    Solutions are stored internally in canonical corner order and automatically
    permuted to match the requested corner order.

    Args:
        n_classes: Number of classes (2 or 3)
        corner_order: Corner reading order for the solutions

    Returns:
        List of valid configurations in the requested corner order

    Raises:
        ValueError: If n_classes is not 2 or 3, or corner_order is invalid
    """
    if n_classes == 2:
        canonical_solutions = _SOLUTIONS_TWO_CLASSES
    elif n_classes == 3:
        canonical_solutions = _SOLUTIONS_THREE_CLASSES
    else:
        raise ValueError("n_classes must be 2 or 3")

    _validate_corner_order(corner_order)

    if corner_order == _CANONICAL_CORNER_ORDER:
        return canonical_solutions.copy()

    perm = _corner_order_permutation(corner_order)
    return [_permute_config(cfg, perm) for cfg in canonical_solutions]


def build_problem_id(
    problem_type: str,
    datagen_args: dict,
    prompt: str,
    ground_truth: list,
) -> str:
    """Generate content-addressed ID: short hash over canonical representation.

    The ID is deterministic and uniquely identifies the problem based on its
    content (problem type, generation arguments, prompt, and ground truth).

    Args:
        problem_type: Type of problem (e.g. "topology_enumeration")
        datagen_args: Dictionary of generation arguments
        prompt: The problem prompt text
        ground_truth: List of ground truth solutions

    Returns:
        8-character hex hash string
    """
    # Canonical datagen_args: sorted keys for determinism
    canonical_args = json.dumps(datagen_args, sort_keys=True)
    payload = {
        "problem_type": problem_type,
        "datagen_args": canonical_args,
        "prompt": prompt,
        "ground_truth": ground_truth,
    }
    h = hashlib.sha1(json.dumps(payload, sort_keys=True).encode("utf-8"))
    return h.hexdigest()[:8]


def generate_dataset_record(
    datagen_args: dict,
    *,
    record_id: str | None = None,
    tags: list[str] | None = None,
    difficulty: str | None = None,
    requires_visual: bool = True,
) -> dict:
    """Generate an eval-focused JSON dataset record.

    Produces a complete record with prompt, ground truth, metadata, and
    generation arguments. Validates datagen_args and generates a content-
    addressed ID if not provided.

    Args:
        datagen_args: Dictionary with required keys:
            - n_classes: int (2 or 3)
            - corner_order: list/tuple of 4 corner names
        record_id: Optional custom ID (otherwise content-addressed)
        tags: List of tags for categorization
        difficulty: Difficulty level string
        requires_visual: Whether visual reasoning is required

    Returns:
        Dictionary with keys: id, prompt, ground_truth, metadata, datagen_args

    Raises:
        AssertionError: If datagen_args is missing required keys or has wrong types
        ValueError: If n_classes or corner_order is invalid
    """
    # Validate datagen_args structure
    assert "n_classes" in datagen_args, "datagen_args missing 'n_classes'"
    assert "corner_order" in datagen_args, "datagen_args missing 'corner_order'"
    assert isinstance(datagen_args["n_classes"], int), "n_classes must be int"
    assert isinstance(datagen_args["corner_order"], (list, tuple)), "corner_order must be list or tuple"
    assert len(datagen_args["corner_order"]) == 4, "corner_order must have 4 elements"

    n_classes = datagen_args["n_classes"]
    corner_order = tuple(datagen_args["corner_order"])

    # Build prompt and ground_truth using internal helpers
    prompt = make_prompt(n_classes, corner_order)
    solutions = get_solutions(n_classes, corner_order)
    ground_truth = [list(cfg) for cfg in solutions]  # No sorting - trust determinism

    # Generate content-addressed ID if not provided
    rid = record_id or build_problem_id(
        problem_type="topology_enumeration",
        datagen_args=datagen_args,
        prompt=prompt,
        ground_truth=ground_truth,
    )

    return {
        "id": rid,
        "prompt": prompt,
        "ground_truth": ground_truth,
        "metadata": {
            "problem_type": "topology_enumeration",
            "tags": tags or [],
            "difficulty": difficulty,
            "requires_visual": requires_visual,
        },
        "datagen_args": datagen_args,
    }
