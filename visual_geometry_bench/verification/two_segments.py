"""Verification for two-segment partition tasks.

Expected answer format:
- Python list with exactly two segments.
- Each segment is a 2-tuple/list of endpoints.
- Each endpoint is a 2-tuple/list of numbers (floats or ints) that lie on the boundary of the evaluation square (unit square by default, or the corners provided via datagen args).

Validity checks:
- Endpoints must map onto the boundary after normalising the square to unit coordinates.
- Optional coordinate grids must be respected when provided.
- Segment endpoints must be distinct.
- The induced polygon counts inside the unit-normalised square must match `counts`.
"""

from __future__ import annotations

import ast
from collections import Counter
from math import isclose
from typing import Iterable, Mapping, Sequence, Tuple

from shapely.geometry import LineString
from shapely.ops import polygonize_full, unary_union

Point = Tuple[float, float]
Segment = Tuple[Point, Point]

_SQUARE_FRAME: tuple[Segment, ...] = (
    ((0.0, 0.0), (1.0, 0.0)),
    ((1.0, 0.0), (1.0, 1.0)),
    ((1.0, 1.0), (0.0, 1.0)),
    ((0.0, 1.0), (0.0, 0.0)),
)

_SHAPE_BY_VERTEX_COUNT = {
    3: "triangle",
    4: "quadrilateral",
    5: "pentagon",
    6: "hexagon",
}


def classify_segments(
    segments: Sequence[Segment], *, decimals: int = 2
) -> Mapping[str, int]:
    """Return polygon counts formed by `segments` inside the unit square."""

    def snap_endpoint(point: Iterable[float]) -> Point:
        x, y = (round(coord, decimals) for coord in point[:2])
        if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
            raise ValueError(f"segment endpoint {(x, y)} lies outside unit square")
        if not _on_unit_boundary((x, y), 0.0):
            raise ValueError(
                f"segment endpoint {(x, y)} must lie on the boundary of the unit square"
            )
        return float(x), float(y)

    snapped = [tuple(snap_endpoint(p) for p in segment) for segment in segments]

    lines = [LineString(segment) for segment in (*snapped, *_SQUARE_FRAME)]
    arrangement = unary_union(lines)
    polygons, *_ = polygonize_full(arrangement)

    counts: Counter[str] = Counter()
    for poly in getattr(polygons, "geoms", ()):  # type: ignore[attr-defined]
        if poly.area == 0:
            continue

        # Deduplicate consecutive boundary vertices, snapped to the rounding grid.
        snapped_vertices: list[Point] = []
        for x_raw, y_raw, *_ in poly.exterior.coords:
            vertex = (float(round(x_raw, decimals)), float(round(y_raw, decimals)))
            if not snapped_vertices or vertex != snapped_vertices[-1]:
                snapped_vertices.append(vertex)

        # Remove collinear points while preserving polygon order.
        vertices = snapped_vertices[:-1]  # exterior repeats first vertex at the end
        simplified: list[Point] = []
        for vertex in vertices:
            if not simplified or vertex != simplified[-1]:
                simplified.append(vertex)
        vertices = simplified

        changed = True
        while changed and len(vertices) >= 3:
            changed = False
            for idx in range(len(vertices)):
                prev_vertex = vertices[idx - 1]
                current_vertex = vertices[idx]
                next_vertex = vertices[(idx + 1) % len(vertices)]
                area = (
                    (current_vertex[0] - prev_vertex[0]) * (next_vertex[1] - prev_vertex[1])
                    - (current_vertex[1] - prev_vertex[1]) * (next_vertex[0] - prev_vertex[0])
                )
                if round(area, decimals) == 0:
                    del vertices[idx]
                    changed = True
                    break

        polygon_shape = _SHAPE_BY_VERTEX_COUNT.get(len(vertices))
        if polygon_shape:
            counts[polygon_shape] += 1

    return dict(counts)

def _to_point(obj) -> Point | None:
    if not isinstance(obj, (list, tuple)) or len(obj) != 2:
        return None
    x, y = obj
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        return None
    return float(x), float(y)


def _to_segment(obj) -> Segment | None:
    if not isinstance(obj, (list, tuple)) or len(obj) != 2:
        return None
    p0 = _to_point(obj[0])
    p1 = _to_point(obj[1])
    if p0 is None or p1 is None:
        return None
    return p0, p1


def parse_model_output_two_segments(raw: str) -> list[Segment] | None:
    """Parse a model output string into two boundary segments."""

    try:
        parsed = ast.literal_eval(raw.strip())
    except (ValueError, SyntaxError):
        return None

    if not isinstance(parsed, list):
        return None

    segments: list[Segment] = []
    for item in parsed:
        segment = _to_segment(item)
        if segment is None:
            return None
        segments.append(segment)

    if len(segments) != 2:
        return None

    return segments


def _on_unit_boundary(point: Point, tol: float) -> bool:
    x, y = point
    on_vertical = isclose(x, 0.0, abs_tol=tol) or isclose(x, 1.0, abs_tol=tol)
    on_horizontal = isclose(y, 0.0, abs_tol=tol) or isclose(y, 1.0, abs_tol=tol)
    return on_vertical or on_horizontal


def _segment_on_boundary_edge(p0: Point, p1: Point, tol: float) -> bool:
    same_x = isclose(p0[0], p1[0], abs_tol=tol)
    same_y = isclose(p0[1], p1[1], abs_tol=tol)

    if same_x and (isclose(p0[0], 0.0, abs_tol=tol) or isclose(p0[0], 1.0, abs_tol=tol)):
        return True
    if same_y and (isclose(p0[1], 0.0, abs_tol=tol) or isclose(p0[1], 1.0, abs_tol=tol)):
        return True

    return False


def _value_on_grid(value: float, grid: Sequence[float], tol: float) -> bool:
    return any(abs(value - gv) <= tol for gv in grid)


def _normalise_segments(
    raw_segments: Sequence[Segment],
    *,
    mapping: tuple[Point, Point, Point, float],
    tol: float,
    grid: Sequence[float] | None,
) -> tuple[list[Segment] | None, list[str]]:
    grid_values = tuple(float(v) for v in grid) if grid else None
    normalised: list[Segment] = []

    for segment in raw_segments:
        mapped = tuple(_to_unit(point, mapping) for point in segment)
        if all(isclose(mapped[0][idx], mapped[1][idx], abs_tol=tol) for idx in (0, 1)):
            return None, ["degenerate_segment"]

        for original, transformed in zip(segment, mapped):
            if grid_values and (
                not _value_on_grid(original[0], grid_values, tol)
                or not _value_on_grid(original[1], grid_values, tol)
            ):
                return None, ["point_off_grid"]
            if not (-tol <= transformed[0] <= 1 + tol and -tol <= transformed[1] <= 1 + tol):
                return None, ["point_out_of_bounds"]
            if not _on_unit_boundary(transformed, tol):
                return None, ["point_not_on_boundary"]

        if _segment_on_boundary_edge(mapped[0], mapped[1], tol):
            return None, ["segment_on_boundary_edge"]

        normalised.append(
            (
                (float(mapped[0][0]), float(mapped[0][1])),
                (float(mapped[1][0]), float(mapped[1][1])),
            )
        )

    return normalised, []


def _prepare_unit_mapping(
    corners: Sequence[Sequence[float]] | None,
) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float], float]:
    if not corners:
        # Identity mapping encoded as origin=(0,0), axis_u=(1,0), axis_v=(0,1), inv_det=1
        return (0.0, 0.0), (1.0, 0.0), (0.0, 1.0), 1.0

    if len(corners) != 4:
        raise ValueError("corners must contain exactly four points")

    c0 = tuple(map(float, corners[0]))
    c1 = tuple(map(float, corners[1]))
    c3 = tuple(map(float, corners[3]))

    axis_u = (c1[0] - c0[0], c1[1] - c0[1])
    axis_v = (c3[0] - c0[0], c3[1] - c0[1])

    det = axis_u[0] * axis_v[1] - axis_u[1] * axis_v[0]
    if abs(det) < 1e-12:
        raise ValueError("corners define a degenerate square")

    inv_det = 1.0 / det
    return c0, axis_u, axis_v, inv_det


def _to_unit(point: Point, mapping: tuple[Point, Point, Point, float]) -> Point:
    origin, axis_u, axis_v, inv_det = mapping
    dx = point[0] - origin[0]
    dy = point[1] - origin[1]
    a = (dx * axis_v[1] - dy * axis_v[0]) * inv_det
    b = (axis_u[0] * dy - axis_u[1] * dx) * inv_det
    return (a, b)


def verify_two_segments(
    model_output: str,
    record: dict,
    *,
    return_diff: bool = False,
) -> bool | dict:
    """Verify a two-segment answer against the record specification."""

    segments = parse_model_output_two_segments(model_output)
    if segments is None:
        if return_diff:
            return {
                "passed": False,
                "errors": ["parse_failure"],
                "details": {"raw_output": model_output[:200]},
            }
        return False

    datagen_args = record.get("datagen_args", {})
    counts_expected_raw = datagen_args.get("counts")
    if counts_expected_raw is None:
        if return_diff:
            return {
                "passed": False,
                "errors": ["missing_counts"],
                "details": {"raw_output": model_output[:200]},
            }
        return False
    counts_expected = {str(k): int(v) for k, v in counts_expected_raw.items()}

    snap_decimals = int(datagen_args.get("snap_decimals", 2))
    tol = 0.5 * 10 ** (-snap_decimals)
    coordinate_grid = datagen_args.get("coordinate_grid")
    corners = datagen_args.get("corners")
    mapping = _prepare_unit_mapping(corners)

    errors: list[str] = []
    segments_unit, normalise_errors = _normalise_segments(
        segments,
        mapping=mapping,
        tol=tol,
        grid=coordinate_grid,
    )
    if segments_unit is None:
        errors.extend(normalise_errors)
        if return_diff:
            return {
                "passed": False,
                "errors": errors,
                "details": {
                    "counts_expected": counts_expected,
                    "counts_observed": {},
                    "used_corners": corners,
                },
            }
        return False

    errors.extend(normalise_errors)

    counts_observed: dict[str, int] = {}
    try:
        counts_observed = dict(classify_segments(segments_unit, decimals=snap_decimals))
    except ValueError:
        errors.append("invalid_segments")

    if not errors and counts_observed != counts_expected:
        errors.append("counts_mismatch")

    passed = len(errors) == 0

    if return_diff:
        return {
            "passed": passed,
            "errors": errors,
            "details": {
                "counts_expected": counts_expected,
                "counts_observed": counts_observed,
                "used_corners": corners,
            },
        }

    return passed
