"""Geometry task renderers (convex hull, Delaunay)."""

from __future__ import annotations

import ast
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from visual_geometry_bench.datagen.convex_hull_tasks import _to_points as _convex_to_points
from visual_geometry_bench.datagen.delaunay_tasks import _to_points as _delaunay_to_points

from .render import register_renderer
from .styles import COLOURS


def _make_two_panel(record: Mapping[str, Any]) -> tuple[plt.Figure, list[plt.Axes]]:
    fig, axes = plt.subplots(1, 2, figsize=(10, 5), constrained_layout=True)
    fig.suptitle(record.get("metadata", {}).get("problem_type", ""), fontsize=15, weight="bold")
    for ax, title in zip(axes, ("Ground truth", "Answer"), strict=True):
        ax.set_title(title, fontsize=13, weight="semibold", pad=10)
        ax.set_aspect("equal")
        ax.set_xlim(-0.08, 1.08)
        ax.set_ylim(-0.08, 1.08)
        ax.grid(True, linestyle="--", linewidth=0.3, alpha=0.3, color="#CCCCCC")
        ax.set_facecolor("#FAFAFA")
    return fig, list(axes)


def _scatter_with_labels(ax: plt.Axes, points: np.ndarray) -> None:
    ax.scatter(points[:, 0], points[:, 1], s=80, color=COLOURS["points"], edgecolors="white", linewidths=1.5, zorder=3)
    for idx, (x, y) in enumerate(points):
        ax.text(x + 0.02, y + 0.02, str(idx), color="black", fontsize=11, ha="left", va="bottom", 
                weight="bold", bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0.8))


def _draw_polyline(ax: plt.Axes, points: np.ndarray, indices: Sequence[int], *, color: str, closed: bool) -> None:
    if len(indices) < 2:
        return
    path = np.array([points[i] for i in indices], dtype=float)
    if closed:
        path = np.vstack((path, path[0]))
    ax.plot(path[:, 0], path[:, 1], color=color, linewidth=2.5, zorder=2, alpha=0.9)


def _coerce_index_list(answer: Any) -> list[int] | None:
    if isinstance(answer, str):
        try:
            answer = ast.literal_eval(answer)
        except (ValueError, SyntaxError):
            return None
    if not isinstance(answer, Iterable):
        return None
    result: list[int] = []
    for item in answer:
        try:
            idx = int(item)
        except (TypeError, ValueError):
            return None
        result.append(idx)
    return result if result else None


def _draw_invalid_message(ax: plt.Axes, message: str) -> None:
    ax.text(0.5, 0.5, message, color=COLOURS["answer"], ha="center", va="center", fontsize=11)


def _coerce_triangle_list(answer: Any) -> list[tuple[int, int, int]] | None:
    if isinstance(answer, str):
        try:
            answer = ast.literal_eval(answer)
        except (ValueError, SyntaxError):
            return None
    if not isinstance(answer, Iterable):
        return None
    triangles: list[tuple[int, int, int]] = []
    for tri in answer:
        if not isinstance(tri, Iterable):
            return None
        items = list(tri)
        if len(items) != 3:
            return None
        try:
            triangles.append(tuple(int(v) for v in items))
        except (TypeError, ValueError):
            return None
    return triangles if triangles else None


def _draw_triangles(ax: plt.Axes, points: np.ndarray, triangles: Sequence[Sequence[int]], *, color: str) -> None:
    for tri in triangles:
        coords = np.array([points[i] for i in tri], dtype=float)
        coords = np.vstack((coords, coords[0]))
        ax.plot(coords[:, 0], coords[:, 1], color=color, linewidth=2, zorder=2, alpha=0.8)


def _render_convex_hull(
    record: Mapping[str, Any],
    answer: Any,
    detail: bool,
    *,
    show: bool | None = None,
) -> plt.Figure:
    points = np.array(_convex_to_points(record["datagen_args"]), dtype=float)
    ground_truth = record.get("ground_truth") or []

    fig, (ax_gt, ax_ans) = _make_two_panel(record)

    _scatter_with_labels(ax_gt, points)

    hull_indices = list(map(int, ground_truth))
    if hull_indices:
        _draw_polyline(ax_gt, points, hull_indices, color=COLOURS["truth"], closed=True)
        for idx in hull_indices:
            x, y = points[idx]
            ax_gt.scatter([x], [y], color=COLOURS["truth"], s=100, edgecolors="white", linewidths=2, zorder=4)

    _scatter_with_labels(ax_ans, points)

    parsed_answer = _coerce_index_list(answer)
    if parsed_answer is None:
        _draw_invalid_message(ax_ans, "Invalid answer")
    else:
        _draw_polyline(ax_ans, points, parsed_answer, color=COLOURS["answer"], closed=True)
        for idx in parsed_answer:
            if 0 <= idx < len(points):
                x, y = points[idx]
                ax_ans.scatter([x], [y], color=COLOURS["answer"], s=100, edgecolors="white", linewidths=2, zorder=4)

    return fig


def _render_delaunay(
    record: Mapping[str, Any],
    answer: Any,
    detail: bool,
    *,
    show: bool | None = None,
) -> plt.Figure:
    points = np.array(_delaunay_to_points(record["datagen_args"]), dtype=float)
    ground_truth = record.get("ground_truth") or []

    fig, (ax_gt, ax_ans) = _make_two_panel(record)

    _scatter_with_labels(ax_gt, points)

    if ground_truth:
        _draw_triangles(ax_gt, points, ground_truth, color=COLOURS["truth"])

    _scatter_with_labels(ax_ans, points)

    parsed_answer = _coerce_triangle_list(answer)
    if parsed_answer is None:
        _draw_invalid_message(ax_ans, "Invalid answer")
    else:
        _draw_triangles(ax_ans, points, parsed_answer, color=COLOURS["answer"])

    return fig


register_renderer("convex_hull_ordering", _render_convex_hull)
register_renderer("delaunay_triangulation", _render_delaunay)
