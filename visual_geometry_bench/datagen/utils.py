"""Shared utilities for topology datagen modules.

Provides canonical corner conventions, permutation helpers, first-occurrence
canonicalisation, and deterministic content hashing used across tasks.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Iterable, Sequence


CANONICAL_CORNER_ORDER: tuple[str, str, str, str] = (
    "bottom-left",
    "bottom-right",
    "top-right",
    "top-left",
)


def validate_corner_order(corner_order: Sequence[str]) -> tuple[str, str, str, str]:
    """Validate that ``corner_order`` is a permutation of canonical corners.

    Args:
        corner_order: Sequence of length 4 describing corner order

    Returns:
        Tuple version of the provided corner order

    Raises:
        ValueError: If corner_order is not a permutation of canonical corners
    """

    if len(corner_order) != 4 or set(corner_order) != set(CANONICAL_CORNER_ORDER):
        raise ValueError(
            "corner_order must be a permutation of ('bottom-left','bottom-right','top-right','top-left')"
        )
    return tuple(corner_order)  # type: ignore[return-value]


def corner_order_permutation(corner_order: Sequence[str]) -> tuple[int, int, int, int]:
    """Compute permutation indices mapping canonical order into ``corner_order``."""

    validated = validate_corner_order(corner_order)
    return tuple(validated.index(name) for name in CANONICAL_CORNER_ORDER)


def permute_config(config: Sequence[int], perm: Sequence[int]) -> tuple[int, int, int, int]:
    """Apply permutation ``perm`` to a 4-element configuration sequence."""

    assert len(config) == 4, "config must have length 4"
    assert len(perm) == 4, "perm must have length 4"
    return tuple(config[perm[i]] for i in range(4))


def canonicalize_first_occurrence(
    config: Iterable[int], *, start_label: int = 0
) -> tuple[int, int, int, int]:
    """Relabel configuration by first-occurrence order starting at ``start_label``."""

    seen: dict[int, int] = {}
    next_label = start_label
    relabelled: list[int] = []
    for label in config:
        if label not in seen:
            seen[label] = next_label
            next_label += 1
        relabelled.append(seen[label])
    return tuple(relabelled)


def compute_content_hash(
    *,
    problem_type: str,
    datagen_args: dict,
    prompt: str,
    ground_truth,
    hash_name: str = "sha1",
    prefix_len: int = 8,
) -> str:
    """Compute a deterministic short hash for datagen records."""

    payload = {
        "problem_type": problem_type,
        "datagen_args": datagen_args,
        "prompt": prompt,
        "ground_truth": ground_truth,
    }
    data = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    digest = hashlib.new(hash_name)
    digest.update(data.encode("utf-8"))
    return digest.hexdigest()[:prefix_len]


def validate_point_array(
    points: Sequence[Sequence[float]], *, min_points: int = 0
) -> list[tuple[float, float]]:
    """Validate 2D point arrays and coerce to list of float tuples."""

    if len(points) < min_points:
        raise AssertionError(f"requires at least {min_points} points; got {len(points)}")

    coerced: list[tuple[float, float]] = []
    for idx, point in enumerate(points):
        if len(point) != 2:
            raise ValueError(f"point {idx} is not length 2: {point!r}")

        x, y = float(point[0]), float(point[1])
        if not (math.isfinite(x) and math.isfinite(y)):
            raise ValueError(f"point {idx} has non-finite coordinates: {(x, y)!r}")

        coerced.append((x, y))

    return coerced


