"""Datagen for convex hull ordering tasks (point clouds → hull vertex indices).

Task format:
- Input points are randomly generated [x, y] floats from [0,1)². Indices correspond to input order.
- The model must return the convex hull vertices in counterclockwise order as a list
  of integer indices. Output must start from the smallest index among hull vertices.

Implementation notes:
- Uses SciPy's ConvexHull; datagen never emits degenerate point sets (>=3 non-collinear).
- Deterministic content-hash IDs include prompt and exact ground truth.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple

import numpy as np
from scipy.spatial import ConvexHull as SciPyConvexHull, QhullError
from scipy.stats import qmc

from visual_geometry_bench.datagen.utils import (
    compute_content_hash,
    validate_point_array,
)


EPSILON = 1e-12


def _gen_convex_points(num_points: int, random_seed: int) -> List[Tuple[float, float]]:
    """Generate points with boundary-biased clustering to harden the task.

    Strategy: mix Poisson disk interior points (well spaced) with boundary-focused
    samples concentrated within a thin band along the unit-square edges.
    """
    assert num_points >= 3
    rng = np.random.default_rng(random_seed)

    # Mix ratio: majority near boundaries to increase hull ambiguity
    boundary_frac = 0.6
    interior_count = max(3, int(round(num_points * (1.0 - boundary_frac))))
    interior_count = min(interior_count, num_points - 3)
    boundary_count = num_points - interior_count

    # Interior via SciPy Poisson disk (blue-noise, avoids clusters)
    radius = float(0.75 / np.sqrt(max(interior_count, 3)))
    sampler = qmc.PoissonDisk(d=2, radius=radius, seed=random_seed)
    interior = sampler.random(interior_count) if interior_count > 0 else np.empty((0, 2), dtype=float)

    # Boundary-biased samples: choose side, then Beta-biased along-edge and inset
    if boundary_count > 0:
        sides = rng.integers(0, 4, size=boundary_count)  # 0:L,1:R,2:B,3:T
        u = rng.beta(0.7, 0.7, size=boundary_count)      # along-edge (corner bias)
        inset = rng.beta(1.0, 8.0, size=boundary_count) * 0.08  # toward edge

        bx = np.where(sides == 0, inset,
             np.where(sides == 1, 1.0 - inset,
             np.where(sides == 2, u, u)))
        by = np.where(sides == 0, u,
             np.where(sides == 1, u,
             np.where(sides == 2, inset, 1.0 - inset)))

        boundary = np.column_stack((bx, by))
        # Small jitter to create micro-clusters along edges without leaving [0,1)
        boundary = np.clip(boundary + rng.normal(0.0, 0.006, size=boundary.shape),
                           0.0, np.nextafter(1.0, 0.0))
    else:
        boundary = np.empty((0, 2), dtype=float)

    points = np.vstack((interior, boundary))
    # Stable shuffle for determinism while mixing groups
    perm = rng.permutation(points.shape[0])
    points = points[perm]
    return validate_point_array(points.tolist(), min_points=3)


def _to_points(datagen_args: dict) -> List[Tuple[float, float]]:
    """Generate points from datagen arguments via random convex sampling.

    Args:
        datagen_args: Dictionary containing 'num_points' and 'seed' for deterministic convex sampling

    Returns:
        List of (x, y) float tuples sampled uniformly from unit square

    Raises:
        ValueError: If num_points < 3
    """
    num_points = int(datagen_args["num_points"])  # type: ignore[arg-type]
    random_seed = int(datagen_args["seed"])  # type: ignore[arg-type]
    if num_points < 3:
        raise ValueError("convex sampling requires num_points >= 3")
    return _gen_convex_points(num_points, random_seed)


def _compute_convex_hull(points: Sequence[Tuple[float, float]]) -> SciPyConvexHull | None:
    """Compute convex hull, returning None for degenerate cases.

    Args:
        points: Sequence of (x, y) coordinate pairs

    Returns:
        SciPy ConvexHull object if valid hull exists, None if collinear or area <= EPSILON
    """
    point_array = np.array(points, dtype=float)
    try:
        hull = SciPyConvexHull(point_array)
    except QhullError:
        return None

    if float(hull.volume) <= EPSILON:
        return None

    return hull


def make_prompt(datagen_args: dict) -> str:
    """Generate task prompt for convex hull vertex ordering.

    Args:
        datagen_args: Arguments containing point data (see _to_points for format)

    Returns:
        Formatted prompt string requesting a list of hull vertex indices
    """
    points = _to_points(datagen_args)
    points_text = ",\n".join(str([float(x), float(y)]) for (x, y) in points)

    prompt_lines = [
        "You are given a set of 2D points (indices correspond to the order shown):",
        "[",
        points_text,
        "]",
        "",
        "Return the convex hull vertices as a list of integer indices in counterclockwise order.",
        "Start the list at the smallest index among the hull vertices.",
        "Before presenting the final list, begin your response with <thinking>...</thinking> containing your full chain of thought or reasoning for your answer.",
        "Strict output: a Python list of integers only.",
    ]
    return "\n".join(prompt_lines)


def _hull_to_canonical_indices(hull: SciPyConvexHull) -> List[int]:
    """Convert SciPy hull vertices to canonical list in CCW order starting at minimum index.

    Args:
        hull: SciPy ConvexHull object with vertices in CCW order

    Returns:
        List of point indices in CCW order, rotated to start at minimum index
    """
    hull_indices = hull.vertices.tolist()
    min_position = hull_indices.index(min(hull_indices))
    canonical_indices = hull_indices[min_position:] + hull_indices[:min_position]
    return canonical_indices


def get_solutions(datagen_args: dict) -> List[int]:
    """Return the convex hull vertex indices (CCW order, canonical rotation)."""
    # Generate points via random convex sampling
    points = _to_points(datagen_args)

    # Compute hull; returns None for degenerate cases (collinear or near-zero area)
    hull = _compute_convex_hull(points)

    if hull is None:
        raise ValueError("datagen_args produced a degenerate point set without a polygonal hull")

    # Rotate hull vertex indices to canonical form (start at min index)
    canonical_indices = _hull_to_canonical_indices(hull)
    return canonical_indices


def generate_dataset_record(
    datagen_args: dict,
    *,
    record_id: str | None = None,
    tags: list[str] | None = None,
    difficulty: str | None = None,
    requires_visual: bool = True,
) -> dict:
    """Generate a complete dataset record for convex hull vertex ordering task.

    Args:
        datagen_args: Must contain 'num_points' and 'seed' for deterministic convex sampling
        record_id: Optional custom ID; auto-generated via content hash if None
        tags: Optional list of tags for categorisation
        difficulty: Optional difficulty label
        requires_visual: Whether task requires visual reasoning (default True)

    Returns:
        Dictionary with keys: id, prompt, ground_truth, metadata, datagen_args

    Raises:
        AssertionError: If datagen_args format is invalid
    """
    assert isinstance(datagen_args, dict)
    assert "num_points" in datagen_args and "seed" in datagen_args, \
        "datagen_args must include 'num_points' and 'seed'"

    prompt = make_prompt(datagen_args)
    ground_truth = get_solutions(datagen_args)

    record_id_final = record_id or compute_content_hash(
        problem_type="convex_hull_ordering",
        datagen_args=datagen_args,
        prompt=prompt,
        ground_truth=ground_truth,
        hash_name="sha1",
        prefix_len=8,
    )

    metadata = {
        "problem_type": "convex_hull_ordering",
        "tags": list(set(tags or [])),
        "difficulty": difficulty or "",
        "requires_visual": bool(requires_visual),
    }

    return {
        "id": record_id_final,
        "prompt": prompt,
        "ground_truth": ground_truth,
        "metadata": metadata,
        "datagen_args": datagen_args,
    }
