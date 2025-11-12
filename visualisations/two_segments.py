"""Two-segment partition task renderer."""

from __future__ import annotations

import ast
from collections.abc import Iterable, Mapping
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from .render import (
    get_answer_label,
    register_renderer,
    should_render_answers,
    should_render_truth,
)
from .styles import COLOURS

_UNIT_SQUARE = np.array(
    [
        (0.0, 0.0),
        (1.0, 0.0),
        (1.0, 1.0),
        (0.0, 1.0),
        (0.0, 0.0),
    ],
    dtype=float,
)


def _extract_corners(datagen_args: Mapping[str, Any]) -> np.ndarray:
    corners = datagen_args.get("corners")
    if corners:
        pts = np.array(corners, dtype=float)
        if pts.shape == (4, 2):
            pts = np.vstack([pts, pts[0]])
        return pts
    return _UNIT_SQUARE


def _panel_setup(title: str, limits: tuple[float, float, float, float]) -> None:
    xmin, xmax, ymin, ymax = limits
    plt.gca().set_title(title, fontsize=13, weight="semibold", pad=10)
    plt.gca().set_xlim(xmin, xmax)
    plt.gca().set_ylim(ymin, ymax)
    plt.gca().set_aspect("equal")
    plt.gca().grid(False)
    plt.gca().axis("off")


def _draw_square(ax: plt.Axes, corners: np.ndarray) -> None:
    closed = np.vstack((corners, corners[0]))
    ax.plot(closed[:, 0], closed[:, 1], "k-", linewidth=2.5, zorder=1)


def _format_counts(counts: Iterable[Mapping[str, Any]]) -> list[str]:
    parts = []
    for entry in counts:
        shape = entry.get("shape")
        count = entry.get("count")
        if shape is None or count is None:
            continue
        parts.append(f"{count} × {shape}")
    return parts if parts else ["(counts unavailable)"]


def _format_prompt_block(counts_lines: list[str]) -> str:
    return "Requested regions:\n" + "\n".join(counts_lines)


def _coerce_segments(answer: Any) -> list[tuple[tuple[float, float], tuple[float, float]]] | None:
    raw = answer
    if isinstance(raw, str):
        try:
            raw = ast.literal_eval(raw)
        except (ValueError, SyntaxError):
            return None
    if not isinstance(raw, Iterable):
        return None
    segments = []
    for item in raw:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            return None
        try:
            p0 = tuple(float(v) for v in item[0])
            p1 = tuple(float(v) for v in item[1])
        except (TypeError, ValueError):
            return None
        if len(p0) != 2 or len(p1) != 2:
            return None
        segments.append((p0, p1))
    return segments if segments else None


def _draw_segments(ax: plt.Axes, segments: list[tuple[tuple[float, float], tuple[float, float]]], *, color: str) -> None:
    for (x0, y0), (x1, y1) in segments:
        ax.plot((x0, x1), (y0, y1), color=color, linewidth=3, zorder=2, alpha=0.9)


def _render_two_segments(
    record: Mapping[str, Any],
    answer: Any,
    detail: bool,
    *,
    show: bool | None = None,
) -> plt.Figure:
    _ = show
    datagen_args = record.get("datagen_args", {})
    corners = _extract_corners(datagen_args)
    xmin, xmax = float(corners[:, 0].min()) - 0.1, float(corners[:, 0].max()) + 0.1
    ymin, ymax = float(corners[:, 1].min()) - 0.1, float(corners[:, 1].max()) + 0.1

    render_truth = should_render_truth(record)
    render_answers = should_render_answers(record)
    if not render_truth and not render_answers:
        render_truth = True

    panels: list[tuple[str, str]] = []
    if render_truth:
        panels.append(("prompt", "Requirements"))
    if render_answers:
        panels.append(("answer", get_answer_label(record)))
    if not panels:
        panels.append(("prompt", "Requirements"))

    fig, axes = plt.subplots(1, len(panels), figsize=(5.2 * len(panels), 5), constrained_layout=True)
    if not isinstance(axes, np.ndarray):
        axes = np.array([axes])
    axes = axes.flatten()
    fig.suptitle("Two Segments", fontsize=15, weight="bold")
    fig.patch.set_facecolor("white")

    panel_axes: dict[str, plt.Axes] = {}
    for ax, (role, title) in zip(axes, panels, strict=True):
        plt.sca(ax)
        _panel_setup(title, (xmin, xmax, ymin, ymax))
        ax.set_facecolor("#FAFAFA")
        if role == "answer":
            _draw_square(ax, corners)
        panel_axes[role] = ax

    counts = record.get("ground_truth", [])
    counts_lines = _format_counts(counts)
    prompt_text = _format_prompt_block(counts_lines)
    ax_prompt = panel_axes.get("prompt")
    if ax_prompt:
        ax_prompt.text(
            0.5,
            0.5,
            prompt_text,
            ha="center",
            va="center",
            fontsize=11,
            color=COLOURS["truth"],
            weight="bold",
            bbox=dict(boxstyle="round,pad=0.8", facecolor="white", edgecolor=COLOURS["truth"], linewidth=2),
        )

    ax_ans = panel_axes.get("answer")
    if ax_ans:
        parsed_segments = _coerce_segments(answer)
        if parsed_segments is None:
            ax_ans.text(
                0.5,
                0.5,
                "No segments provided",
                ha="center",
                va="center",
                fontsize=11,
                color=COLOURS["answer"],
            )
        else:
            _draw_segments(ax_ans, parsed_segments, color=COLOURS["answer"])

    return fig


register_renderer("two_segments", _render_two_segments)
