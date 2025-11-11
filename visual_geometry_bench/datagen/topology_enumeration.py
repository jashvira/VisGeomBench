"""Topology enumeration problems: corner labelings that force class intersections.

Problems ask which corner-label configurations of a unit square guarantee that
distinct classes must meet inside the square, given only corner observations
and the assumption of continuous boundaries.
"""

from __future__ import annotations

from visual_geometry_bench.datagen.utils import (
    CANONICAL_CORNER_ORDER,
    canonicalize_first_occurrence,
    compute_content_hash,
    corner_order_permutation,
    permute_config,
    validate_corner_order,
)


def _inverse_perm(perm: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    """Return the inverse permutation (perm maps canonical→target)."""

    inv = [0, 0, 0, 0]
    for idx, pos in enumerate(perm):
        inv[pos] = idx
    return tuple(inv)  # type: ignore[return-value]


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
    return canonicalize_first_occurrence(config)


def make_prompt(
    n_classes: int,
    corner_order: tuple[str, str, str, str] = CANONICAL_CORNER_ORDER,
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
    validate_corner_order(corner_order)

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
    corner_order: tuple[str, str, str, str] = CANONICAL_CORNER_ORDER,
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

    validate_corner_order(corner_order)

    if corner_order == CANONICAL_CORNER_ORDER:
        return canonical_solutions.copy()

    perm = corner_order_permutation(corner_order)
    inv = _inverse_perm(perm)
    return [permute_config(cfg, inv) for cfg in canonical_solutions]


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
    return compute_content_hash(
        problem_type=problem_type,
        datagen_args=datagen_args,
        prompt=prompt,
        ground_truth=ground_truth,
        hash_name="sha1",
        prefix_len=8,
    )


def generate_dataset_record(
    datagen_args: dict,
    *,
    record_id: str | None = None,
    tags: list[str] | None = None,
    difficulty: str | None = None,
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
        },
        "datagen_args": datagen_args,
    }
