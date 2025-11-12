"""Geometry task renderers (convex hull, Delaunay)."""

from __future__ import annotations

import ast
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from visual_geometry_bench.datagen.convex_hull_tasks import _to_points as _convex_to_points
from visual_geometry_bench.datagen.delaunay_tasks import _to_points as _delaunay_to_points

from .render import (
    get_answer_label,
    register_renderer,
    should_render_answers,
    should_render_truth,
)
from .styles import COLOURS

_FRIENDLY_TITLES = {
    "convex_hull_ordering": "Convex Hull Ordering",
    "delaunay_triangulation": "Delaunay Triangulation",
}

DEFAULT_VIEW_LIMITS = (-0.08, 1.08)


def _format_problem_title(record: Mapping[str, Any]) -> str:
    metadata = record.get("metadata", {}) if isinstance(record, Mapping) else {}
    raw = metadata.get("problem_type", "") if isinstance(metadata, Mapping) else ""
    if raw in _FRIENDLY_TITLES:
        return _FRIENDLY_TITLES[raw]
    if not raw:
        return "Geometry Task"
    return raw.replace("_", " ").title()


def _make_panels(record: Mapping[str, Any]) -> tuple[plt.Figure, dict[str, plt.Axes]]:
    panels: list[tuple[str, str]] = []
    if should_render_truth(record):
        panels.append(("truth", "Ground truth"))
    if should_render_answers(record):
        panels.append(("answer", get_answer_label(record)))
    if not panels:
        panels.append(("truth", "Ground truth"))

    fig_width = 5.5 * len(panels)
    fig, axes = plt.subplots(1, len(panels), figsize=(fig_width, 5.5))
    if not isinstance(axes, np.ndarray):
        axes = np.array([axes])
    axes = axes.flatten()
    fig.subplots_adjust(left=0.05, right=0.97, bottom=0.16, wspace=0.25)
    fig.suptitle(_format_problem_title(record), fontsize=15, weight="bold")

    panel_axes: dict[str, plt.Axes] = {}
    for ax, (key, title) in zip(axes, panels, strict=True):
        ax.set_title(title, fontsize=13, weight="semibold", pad=10)
        ax.set_aspect("equal")
        ax.set_xlim(*DEFAULT_VIEW_LIMITS)
        ax.set_ylim(*DEFAULT_VIEW_LIMITS)
        ax.grid(True, linestyle="--", linewidth=0.3, alpha=0.3, color="#CCCCCC")
        ax.set_facecolor("#FAFAFA")
        panel_axes[key] = ax
    return fig, panel_axes


def _scatter_with_labels(
    ax: plt.Axes,
    points: np.ndarray,
    *,
    label_fontsize: int = 7,
    label_colours: Mapping[int, str] | None = None,
    circle_label_params: tuple[np.ndarray, float] | None = None,
) -> None:
    ax.scatter(points[:, 0], points[:, 1], s=80, color=COLOURS["points"], edgecolors="white", linewidths=1.5, zorder=3)
    custom_colours = label_colours or {}
    if circle_label_params:
        center, radius = circle_label_params
        label_radius = radius * 1.14
    else:
        center = None
        label_radius = None
    for idx, (x, y) in enumerate(points):
        if label_radius is not None and center is not None:
            angle = np.arctan2(y - center[1], x - center[0])
            label_x = center[0] + label_radius * np.cos(angle)
            label_y = center[1] + label_radius * np.sin(angle)
            ha = "center"
            va = "center"
        else:
            label_x = x + 0.02
            label_y = y + 0.02
            ha = "left"
            va = "bottom"
        ax.text(
            label_x,
            label_y,
            str(idx),
            color=custom_colours.get(idx, "black"),
            fontsize=label_fontsize,
            ha=ha,
            va=va,
            weight="bold",
            bbox=None,
        )


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


def _infer_circle_params(points: np.ndarray) -> tuple[np.ndarray, float]:
    center = points.mean(axis=0)
    radius = float(np.mean(np.linalg.norm(points - center, axis=1)))
    return center, radius


def _circle_bounds(center: np.ndarray, radius: float, *, pad_ratio: float = 0.25) -> tuple[tuple[float, float], tuple[float, float]]:
    pad = radius * pad_ratio
    x_min = float(center[0] - radius - pad)
    x_max = float(center[0] + radius + pad)
    y_min = float(center[1] - radius - pad)
    y_max = float(center[1] + radius + pad)

    # Keep the zoom within global defaults to avoid clipping metadata annotations.
    lo, hi = DEFAULT_VIEW_LIMITS
    x_min = max(lo, x_min)
    y_min = max(lo, y_min)
    x_max = min(hi, x_max)
    y_max = min(hi, y_max)
    return (x_min, x_max), (y_min, y_max)


def _apply_circle_axes(ax: plt.Axes, center: np.ndarray, radius: float) -> None:
    (x_min, x_max), (y_min, y_max) = _circle_bounds(center, radius)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)


def _draw_circle_outline(ax: plt.Axes, center: np.ndarray, radius: float, *, color: str, alpha: float, zorder: float) -> None:
    theta = np.linspace(0.0, 2.0 * np.pi, 256)
    xs = center[0] + radius * np.cos(theta)
    ys = center[1] + radius * np.sin(theta)
    ax.plot(xs, ys, color=color, linestyle="--", linewidth=1.5, alpha=alpha, zorder=zorder)


def _render_convex_hull(
    record: Mapping[str, Any],
    answer: Any,
    detail: bool,
    *,
    show: bool | None = None,
) -> plt.Figure:
    points = np.array(_convex_to_points(record["datagen_args"]), dtype=float)
    ground_truth = record.get("ground_truth") or []
    metadata = record.get("metadata", {}) if isinstance(record, Mapping) else {}
    datagen_args = record.get("datagen_args", {}) if isinstance(record, Mapping) else {}
    point_distribution = metadata.get("point_distribution") or datagen_args.get("point_distribution", "")
    is_circle = point_distribution == "circle"
    circle_params = _infer_circle_params(points) if is_circle else None

    fig, panels = _make_panels(record)
    ax_gt = panels.get("truth")
    ax_ans = panels.get("answer")

    circle_axes = list(panels.values())
    if circle_params and circle_axes:
        for ax in circle_axes:
            _apply_circle_axes(ax, *circle_params)
            _draw_circle_outline(
                ax,
                *circle_params,
                color=COLOURS["annotation"],
                alpha=0.35,
                zorder=1,
            )

    label_circle = circle_params if is_circle else None

    hull_indices = list(map(int, ground_truth))
    legend_entries: dict[str, Any] = {}
    if ax_gt:
        _scatter_with_labels(ax_gt, points, circle_label_params=label_circle)
        if hull_indices:
            gt_line = _draw_polyline(ax_gt, points, hull_indices, color=COLOURS["truth"], closed=True)
            if gt_line:
                legend_entries["Ground truth hull"] = gt_line
            coords = points[hull_indices]
            gt_scatter = ax_gt.scatter(
                coords[:, 0],
                coords[:, 1],
                color=COLOURS["truth"],
                s=100,
                edgecolors="white",
                linewidths=2,
                zorder=4,
            )
            legend_entries.setdefault("Ground truth hull", gt_scatter)

    if ax_ans:
        parsed_answer = _coerce_index_list(answer)
        if parsed_answer is None:
            _scatter_with_labels(ax_ans, points, circle_label_params=label_circle)
            _draw_invalid_message(ax_ans, "Invalid answer")
        else:
            answer_points: list[int] = []
            for idx in parsed_answer:
                if 0 <= idx < len(points):
                    answer_points.append(idx)

            truth_set = set(hull_indices)
            ans_set = set(answer_points)
            missed = sorted(truth_set - ans_set)
            extra = sorted(ans_set - truth_set)
            correct = sorted(ans_set & truth_set)

            label_overrides: dict[int, str] = {}
            for idx in missed:
                label_overrides[idx] = COLOURS["missed_vertex"]
            for idx in extra:
                label_overrides[idx] = COLOURS["extra_vertex"]

            _scatter_with_labels(ax_ans, points, label_colours=label_overrides, circle_label_params=label_circle)

            draw_indices = answer_points if len(answer_points) >= 2 else []
            if draw_indices:
                _draw_polyline(ax_ans, points, draw_indices, color=COLOURS["answer"], closed=True)
            answer_label = get_answer_label(record)

            def _scatter_subset(indices: list[int], *, color: str, label: str) -> None:
                if not indices:
                    return
                coords = points[indices]
                handle = ax_ans.scatter(
                    coords[:, 0],
                    coords[:, 1],
                    color=color,
                    s=115,
                    edgecolors="white",
                    linewidths=2.2,
                    zorder=5,
                )
                legend_entries[label] = handle

            if correct:
                _scatter_subset(correct, color=COLOURS["answer"], label=answer_label)
            elif draw_indices:
                legend_entries.setdefault(
                    answer_label,
                    Line2D([], [], color=COLOURS["answer"], linewidth=2),
                )
            if missed:
                _scatter_subset(missed, color=COLOURS["missed_vertex"], label="Missed hull vertex")
            if extra:
                _scatter_subset(extra, color=COLOURS["extra_vertex"], label="Extra vertex")

    if legend_entries:
        fig.subplots_adjust(top=0.7)
        fig.legend(
            legend_entries.values(),
            legend_entries.keys(),
            loc="upper center",
            bbox_to_anchor=(0.5, 0.88),
            ncol=len(legend_entries),
            frameon=True,
            framealpha=0.95,
        )

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

    fig, panels = _make_panels(record)
    ax_gt = panels.get("truth")
    ax_ans = panels.get("answer")

    if ax_gt:
        _scatter_with_labels(ax_gt, points)
        if ground_truth:
            _draw_triangles(ax_gt, points, ground_truth, color=COLOURS["truth"])

    if ax_ans:
        _scatter_with_labels(ax_ans, points)
        parsed_answer = _coerce_triangle_list(answer)
        if parsed_answer is None:
            _draw_invalid_message(ax_ans, "Invalid answer")
        else:
            _draw_triangles(ax_ans, points, parsed_answer, color=COLOURS["answer"])

    return fig


register_renderer("convex_hull_ordering", _render_convex_hull)
register_renderer("delaunay_triangulation", _render_delaunay)
