"""Shikaku rectangles task renderer."""

from __future__ import annotations

import ast
from collections.abc import Iterable, Mapping
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from visual_geometry_bench.datagen.shikaku_tasks import load_puzzle

from .render import register_renderer
from .styles import COLOURS


def _draw_grid(ax: plt.Axes, width: int, height: int, numbers: np.ndarray) -> None:
    for i in range(height + 1):
        ax.axhline(i, color="#888888", linewidth=1.1, zorder=1)
    for j in range(width + 1):
        ax.axvline(j, color="#888888", linewidth=1.1, zorder=1)

    for i in range(height):
        for j in range(width):
            val = numbers[i, j]
            if val != 0:
                ax.text(
                    j + 0.5,
                    i + 0.5,
                    str(val),
                    ha="center",
                    va="center",
                    fontsize=14,
                    color="black",
                    weight="bold",
                    zorder=4,
                )


def _draw_rectangles(ax: plt.Axes, rectangles: list[list[int]], *, color: str, zorder: int) -> None:
    for rect in rectangles:
        left, top, right, bottom = rect
        # Matplotlib origin is bottom-left; puzzle uses top-left indexing, so shift accordingly
        x0 = left
        y0 = top
        width = (right - left + 1)
        height = (bottom - top + 1)
        patch = plt.Rectangle(
            (x0, y0),
            width,
            height,
            fill=False,
            edgecolor=color,
            linewidth=2.6,
            zorder=zorder,
            joinstyle="miter",
        )
        ax.add_patch(patch)


def _coerce_rectangles(answer: Any) -> list[list[int]] | None:
    raw = answer
    if isinstance(raw, str):
        try:
            raw = ast.literal_eval(raw)
        except (ValueError, SyntaxError):
            return None
    if not isinstance(raw, Iterable):
        return None
    rects = []
    for item in raw:
        if not isinstance(item, (list, tuple)) or len(item) != 4:
            return None
        try:
            rect = [int(v) for v in item]
        except (TypeError, ValueError):
            return None
        rects.append(rect)
    return rects if rects else None


def _render_shikaku(
    record: Mapping[str, Any],
    answer: Any,
    detail: bool,
    *,
    show: bool | None = None,
) -> plt.Figure:
    _ = show
    datagen_args = record.get("datagen_args", {})
    # Support inline grid data for tests; otherwise load from file
    if "width" in datagen_args and "height" in datagen_args and "numbers" in datagen_args:
        width = int(datagen_args["width"])
        height = int(datagen_args["height"])
        numbers = np.array(datagen_args["numbers"], dtype=int)
    else:
        puzzle, _ = load_puzzle(datagen_args)
        width = puzzle["width"]
        height = puzzle["height"]
        numbers = np.array(puzzle["numbers"], dtype=int)
    ground_truth = record.get("ground_truth", [])

    fig, axes = plt.subplots(1, 2, figsize=(12, 6), constrained_layout=True)
    fig.suptitle("Shikaku Rectangles", fontsize=15, weight="bold")
    fig.patch.set_facecolor("white")

    for ax, title in zip(axes, ("Ground truth", "Answer"), strict=True):
        ax.set_title(title, fontsize=13, weight="semibold", pad=10)
        ax.set_aspect("equal")
        ax.set_xlim(-0.05, width + 0.05)
        ax.set_ylim(-0.05, height + 0.05)
        ax.invert_yaxis()
        ax.grid(False)
        ax.set_facecolor("#FAFAFA")

    # Ground truth: grid + solution rectangles
    _draw_grid(axes[0], width, height, numbers)
    if ground_truth:
        _draw_rectangles(axes[0], ground_truth, color=COLOURS["truth"], zorder=5)

    # Answer: grid + model rectangles
    _draw_grid(axes[1], width, height, numbers)
    parsed_answer = _coerce_rectangles(answer)
    if parsed_answer is None:
        axes[1].text(
            width / 2,
            height / 2,
            "Invalid answer",
            ha="center",
            va="center",
            fontsize=11,
            color=COLOURS["answer"],
        )
    else:
        _draw_rectangles(axes[1], parsed_answer, color=COLOURS["answer"], zorder=5)

    return fig


register_renderer("shikaku_rectangles", _render_shikaku)
