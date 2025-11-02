"""Prompt and record generation for two-segment partition tasks."""

from __future__ import annotations

import random
from typing import Mapping, Sequence

from visual_geometry_bench.datagen.utils import compute_content_hash

_UNIT_SQUARE: tuple[tuple[float, float], ...] = (
    (0.0, 0.0),
    (1.0, 0.0),
    (1.0, 1.0),
    (0.0, 1.0),
)

_SHAPE_ORDER: tuple[str, ...] = ("triangle", "quadrilateral", "pentagon", "hexagon")


def _format_counts(counts: Mapping[str, int]) -> str:
    parts = []
    for shape in _SHAPE_ORDER:
        total = counts.get(shape)
        if not total:
            continue
        name = shape if total == 1 else f"{shape}s"
        parts.append(f"{total} {name}")
    if not parts:
        return "0 regions"
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return " and ".join(parts)
    return ", ".join(parts[:-1]) + f", and {parts[-1]}"


def make_prompt(
    counts: Mapping[str, int],
    *,
    corners: Sequence[Sequence[float]] | None = None,
    coordinate_grid: Sequence[float] | None = None,
) -> str:
    """Create a textual prompt describing the target partition counts."""

    counts_text = _format_counts(counts)
    if corners:
        formatted_corners = ", ".join(f"({float(x):g}, {float(y):g})" for x, y in corners)
        header = (
            "Work inside the square whose boundary corners (in order) are "
            f"{formatted_corners}."
        )
    else:
        header = "Work inside the unit square with corners (0, 0), (1, 0), (1, 1), and (0, 1)."

    lines = [
        header,
        "Provide two straight segments whose endpoints lie on the boundary of this square.",
        f"The two segments together with the square's edges must partition the interior into exactly {counts_text}.",
        "Before presenting the final list, begin your response with <thinking>...</thinking> containing your full chain of thought or reasoning for your answer.",
        "Return a Python list of the two segments in the form [((x0, y0), (x1, y1)), ((x2, y2), (x3, y3))].",
    ]
    if coordinate_grid:
        grid_values = ", ".join(f"{value:g}" for value in sorted(set(coordinate_grid)))
        lines.insert(
            2,
            f"Use boundary points whose coordinates are drawn from {{{grid_values}}}.",
        )
    return "\n".join(lines)


def _normalise_counts(raw_counts) -> dict[str, int]:
    assert raw_counts is not None, "datagen_args missing 'counts'"
    if not isinstance(raw_counts, Mapping):
        raise AssertionError("counts must be a mapping of shape name -> integer count")

    counts = {
        str(shape): int(total)
        for shape, total in raw_counts.items()
        if int(total) > 0
    }
    assert counts, "counts must contain at least one positive entry"
    return counts


def _resolve_square(record_args: dict) -> Sequence[Sequence[float]] | None:
    corners_override = record_args.pop("corners", None)
    square_spec = record_args.pop("square", "unit")
    corners: list[tuple[float, float]] | None = None
    square_label = "unit"

    if isinstance(square_spec, str):
        if square_spec == "unit":
            corners = list(_UNIT_SQUARE)
            square_label = "unit"
        elif square_spec == "random":
            seed = record_args.pop("square_seed", None)
            rng = random.Random(seed)
            side = rng.uniform(0.3, 1.0)
            origin_x = rng.uniform(0.0, 1.0 - side)
            origin_y = rng.uniform(0.0, 1.0 - side)
            corners = [
                (origin_x, origin_y),
                (origin_x + side, origin_y),
                (origin_x + side, origin_y + side),
                (origin_x, origin_y + side),
            ]
            square_label = "random"
            if seed is not None:
                record_args["square_seed"] = seed
        else:
            raise AssertionError("square must be 'unit', 'random', or a list of corners")
    else:
        corners = [tuple(map(float, corner)) for corner in square_spec]
        if len(corners) != 4:
            raise AssertionError("square must provide exactly four corner points")
        square_label = "explicit"

    if corners_override is not None:
        corners = [tuple(map(float, corner)) for corner in corners_override]
        if len(corners) != 4:
            raise AssertionError("corners must contain exactly four points")
        square_label = "explicit"

    record_args["square"] = square_label

    if corners is None:
        record_args.pop("corners", None)
        return None

    corners_list = [list(corner) for corner in corners]
    record_args["corners"] = corners_list

    if square_label == "unit" and corners_override is None:
        # Do not display corners for the canonical unit square
        return None

    return corners_list


def generate_dataset_record(
    datagen_args: dict,
    *,
    record_id: str | None = None,
    tags: list[str] | None = None,
    difficulty: str | None = None,
    requires_visual: bool = True,
) -> dict:
    """Generate dataset record for a two-segment partition specification."""

    record_args = dict(datagen_args)
    record_args.pop("variant_id", None)

    counts = _normalise_counts(record_args.pop("counts", None))
    record_args["counts"] = counts

    corners = _resolve_square(record_args)

    record_args["snap_decimals"] = int(record_args.get("snap_decimals", 2))

    prompt = make_prompt(
        counts,
        corners=corners,
        coordinate_grid=record_args.get("coordinate_grid"),
    )
    ground_truth = [
        {"shape": shape, "count": int(total)}
        for shape, total in sorted(counts.items())
    ]

    rid = record_id or compute_content_hash(
        problem_type="two_segments",
        datagen_args=record_args,
        prompt=prompt,
        ground_truth=ground_truth,
    )

    return {
        "id": rid,
        "prompt": prompt,
        "ground_truth": ground_truth,
        "metadata": {
            "problem_type": "two_segments",
            "tags": tags or [],
            "difficulty": difficulty,
            "requires_visual": requires_visual,
        },
        "datagen_args": record_args,
    }
