"""Shikaku rectangles task renderer."""

from __future__ import annotations

import ast
from collections.abc import Iterable, Mapping
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors as mcolors

from visual_geometry_bench.datagen.shikaku_tasks import load_puzzle

from .render import get_answer_label, register_renderer
from .styles import COLOURS


def _lighten(hex_colour: str, factor: float) -> tuple[float, float, float]:
    """Blend the provided colour with white by the given factor (0=no change)."""

    rgb = np.array(mcolors.to_rgb(hex_colour))
    return tuple((1.0 - factor) * rgb + factor * np.ones_like(rgb))


def _palette_from_color(base_color: str, count: int) -> tuple[list[tuple[float, float, float]], str]:
    """Return a colour-blind friendly palette with distinct hues per rectangle."""

    okabe_ito = [
        "#E69F00",  # orange
        "#56B4E9",  # sky blue
        "#009E73",  # bluish green
        "#F0E442",  # yellow
        "#0072B2",  # blue
        "#D55E00",  # vermillion
        "#CC79A7",  # reddish purple
        "#999999",  # grey
    ]

    colour_key = base_color.lower()
    start_idx = 0
    if colour_key == COLOURS["answer"]:
        start_idx = 4  # start mid palette to avoid matching truth
    elif colour_key not in {COLOURS["truth"], COLOURS["answer"]}:
        start_idx = 2

    fills: list[tuple[float, float, float]] = []
    for idx in range(max(count, 1)):
        base = okabe_ito[(start_idx + idx) % len(okabe_ito)]
        cycle = idx // len(okabe_ito)
        factor = min(0.18 * cycle, 0.65)
        fills.append(_lighten(base, factor))

    return fills, "#3C3C3C"


def _draw_grid(ax: plt.Axes, width: int, height: int, numbers: np.ndarray) -> None:
    for i in range(height + 1):
        ax.axhline(i, color="#666666", linewidth=0.8, zorder=10)
    for j in range(width + 1):
        ax.axvline(j, color="#666666", linewidth=0.8, zorder=10)

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
    """Fill each rectangle with a distinct colour while retaining crisp bounds."""

    if not rectangles:
        return

    fills, stroke = _palette_from_color(color, len(rectangles))

    for idx, rect in enumerate(rectangles):
        left, top, right, bottom = rect
        width = right - left + 1
        height = bottom - top + 1

        face = fills[idx % len(fills)]

        patch = plt.Rectangle(
            (left, top),
            width,
            height,
            facecolor=face,
            edgecolor=stroke,
            linewidth=1.6,
            zorder=max(1, zorder - 2),
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

    answer_title = get_answer_label(record)
    for ax, title in zip(axes, ("Ground truth", answer_title), strict=True):
        ax.set_title(title, fontsize=13, weight="semibold", pad=10)
        ax.set_aspect("equal")
        ax.set_xlim(-0.05, width + 0.05)
        ax.set_ylim(-0.05, height + 0.05)
        ax.invert_yaxis()
        ax.grid(False)
        ax.set_facecolor("#FAFAFA")

    # Ground truth: rectangles first, then overlay grid for crisp separators
    if ground_truth:
        _draw_rectangles(axes[0], ground_truth, color=COLOURS["truth"], zorder=5)
    _draw_grid(axes[0], width, height, numbers)

    # Answer: grid + model rectangles
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
    _draw_grid(axes[1], width, height, numbers)

    return fig


register_renderer("shikaku_rectangles", _render_shikaku)
