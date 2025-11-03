"""Datagen for Delaunay triangulation tasks (point sets → triangle index triples).

Task format:
- Input: n points in general position (no three collinear, no four concyclic)
  sampled from [0,1)². Point indices correspond to input order.
- Output: List of triangles, each represented as a sorted 3-element list of
  point indices describing the unique Delaunay triangulation.

Implementation:
- Uses rejection sampling to guarantee general position (unique triangulation).
- Ground truth computed via scipy.spatial.Delaunay and canonicalised.
- Deterministic content-hash IDs include prompt and exact ground truth.
"""

from __future__ import annotations

from itertools import combinations
from typing import List, Tuple

import numpy as np
from scipy.spatial import Delaunay as SciPyDelaunay

from visual_geometry_bench.datagen.utils import (
    compute_content_hash,
    validate_point_array,
)

__all__ = [
    "sample_unique_delaunay_points",
    "make_prompt",
    "get_solutions",
    "generate_dataset_record",
]

EPSILON = 1e-12


def _orientation_area(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """Return twice the signed area of triangle ABC via cross product."""
    u, v = b - a, c - a
    return float(u[0] * v[1] - u[1] * v[0])


def _incircle_det(points: np.ndarray) -> float:
    """Return the 4×4 incircle determinant for four 2-D points."""
    x, y = points[:, 0], points[:, 1]
    mat = np.column_stack((x, y, x * x + y * y, np.ones(4)))
    return float(np.linalg.det(mat))


def sample_unique_delaunay_points(
    n: int,
    *,
    box: Tuple[float, float] = (0.0, 1.0),
    eps: float = EPSILON,
    max_tries: int = 10_000,
    seed: int | None = None,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Sample n points in general position guaranteeing unique Delaunay triangulation.

    Args:
        n: Number of points (must be ≥3)
        box: (lo, hi) bounds for uniform sampling
        eps: Tolerance for degeneracy checks (scaled by box size²)
        max_tries: Maximum rejection-sampling attempts
        seed: RNG seed for deterministic sampling (mutually exclusive with ``rng``)
        rng: Optional pre-seeded numpy Generator to sample points from

    Returns:
        (n, 2) array of point coordinates

    Raises:
        ValueError: If n < 3, or if both seed and rng are specified
        RuntimeError: If general-position sample not found within max_tries
    """
    if rng is not None and seed is not None:
        raise ValueError("Specify either seed or rng, not both")

    if n < 3:
        raise ValueError("Delaunay triangulation requires at least 3 points")

    if rng is None:
        rng = np.random.default_rng(seed)

    lo, hi = box
    scale = hi - lo
    # Determinants scale with box diameter², so scale tolerance likewise.
    tol = eps * scale * scale

    for _ in range(max_tries):
        pts = rng.uniform(lo, hi, size=(n, 2))

        # Reject collinear triples: zero-area triangles collapse the triangulation.
        if any(
            abs(_orientation_area(pts[i], pts[j], pts[k])) <= tol
            for i, j, k in combinations(range(n), 3)
        ):
            continue

        # Reject concyclic quadruples: empty cocircular quadruples break uniqueness.
        def _is_concyclic(indices: Tuple[int, int, int, int]) -> bool:
            idx = np.array(indices, dtype=int)
            return abs(_incircle_det(pts[idx])) <= tol

        if any(_is_concyclic(combo) for combo in combinations(range(n), 4)):
            continue

        # General position achieved; return to preserve deterministic RNG sequence.
        return pts

    raise RuntimeError(
        f"Failed to find general-position sample after {max_tries} attempts"
    )


def _to_points(datagen_args: dict) -> List[Tuple[float, float]]:
    """Generate points from datagen_args via rejection sampling.

    Args:
        datagen_args: Must contain 'num_points' (int ≥3) and 'seed' (int)

    Returns:
        List of (x, y) float tuples in general position

    Raises:
        ValueError: If num_points < 3 or required keys missing
    """
    # Extract and validate required parameters
    try:
        num_points = int(datagen_args["num_points"])
        seed = int(datagen_args["seed"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("datagen_args must contain 'num_points' and 'seed'") from exc

    if num_points < 3:
        raise ValueError("num_points must be at least 3")

    # Parse optional box parameter (sampling bounds)
    box = datagen_args.get("box", (0.0, 1.0))
    try:
        lo, hi = map(float, box)
    except (TypeError, ValueError) as exc:
        raise ValueError("box must be an iterable of two numeric bounds") from exc
    if hi <= lo:
        raise ValueError("box upper bound must exceed lower bound")

    # Extract optional sampling parameters
    eps = float(datagen_args.get("eps", EPSILON))
    max_tries = int(datagen_args.get("max_tries", 10_000))

    # Generate points in general position using rejection sampling
    pts = sample_unique_delaunay_points(
        num_points,
        seed=seed,
        box=(lo, hi),
        eps=eps,
        max_tries=max_tries,
    )
    # Validate and return as list of tuples
    return validate_point_array(pts.tolist(), min_points=3)


def _compute_delaunay_triangulation(
    points: List[Tuple[float, float]],
) -> List[List[int]]:
    """Compute canonical Delaunay triangulation as sorted list of sorted triples.

    Args:
        points: List of (x, y) coordinate pairs

    Returns:
        Sorted list of triangles, each a sorted 3-element list of point indices
    """
    point_array = np.array(points, dtype=float)
    tri = SciPyDelaunay(point_array)
    # Canonicalise: sort each simplex, then sort the list of simplices
    simplices = [sorted(map(int, simplex)) for simplex in tri.simplices]
    return sorted(simplices)


def make_prompt(datagen_args: dict) -> str:
    """Generate task prompt for Delaunay triangulation.

    Args:
        datagen_args: Arguments containing point generation parameters

    Returns:
        Formatted prompt string requesting triangle index triples
    """
    points = _to_points(datagen_args)
    display_points = np.round(points, 3)
    points_text = ",\n".join(f"  {list(map(float, pt))}" for pt in display_points)

    prompt_lines = [
        "You are given a set of 2D points in general position (indices correspond to the order shown):",
        "[",
        points_text,
        "]",
        "",
        "Return the Delaunay triangulation as a list of triangles.",
        "Each triangle is a list of three point indices (sorted in ascending order).",
        "Before presenting the final list, begin your response with <thinking>...</thinking> containing your full chain of thought or reasoning for your answer.",
        "Strict output: a Python list of lists of integers only.",
    ]
    return "\n".join(prompt_lines)


def get_solutions(datagen_args: dict) -> List[List[int]]:
    """Return the canonical Delaunay triangulation for the given point set.

    Args:
        datagen_args: Arguments containing point generation parameters

    Returns:
        Sorted list of triangles (each a sorted 3-element list of indices)
    """
    points = _to_points(datagen_args)
    return _compute_delaunay_triangulation(points)


def generate_dataset_record(
    datagen_args: dict,
    *,
    tags: list[str] | None = None,
    difficulty: str = "",
    record_id: str | None = None,
    metadata: dict | None = None,
) -> dict:
    """Generate a complete evaluation record for Delaunay triangulation task.

    Args:
        datagen_args: Point generation parameters (num_points, seed)
        metadata: Optional metadata overrides (tags, difficulty)

    Returns:
        Dataset record with id, prompt, ground_truth, metadata, datagen_args
    """
    prompt = make_prompt(datagen_args)
    ground_truth = get_solutions(datagen_args)

    base_tags = ["geometry", "triangulation", "delaunay"]
    merged_tags = list({*base_tags, *(tags or [])})

    record_metadata = {
        "problem_type": "delaunay_triangulation",
        "tags": merged_tags,
        "difficulty": difficulty,
    }
    if metadata:
        filtered_metadata = {k: v for k, v in metadata.items() if k != "requires_visual"}
        record_metadata.update(filtered_metadata)

    content_id = record_id or compute_content_hash(
        problem_type="delaunay_triangulation",
        datagen_args=datagen_args,
        prompt=prompt,
        ground_truth=ground_truth,
    )

    return {
        "id": content_id,
        "prompt": prompt,
        "ground_truth": ground_truth,
        "metadata": record_metadata,
        "datagen_args": datagen_args,
    }
