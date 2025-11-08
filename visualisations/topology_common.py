"""Shared helpers for topology visualisations."""

from __future__ import annotations

import math
from typing import Any, Mapping, Sequence

import matplotlib.pyplot as plt
import numpy as np

from .styles import COLOURS

_CORNER_POSITIONS = {
    "bottom-left": (0.0, 0.0),
    "bottom-right": (1.0, 0.0),
    "top-right": (1.0, 1.0),
    "top-left": (0.0, 1.0),
    "left-bottom": (0.0, 0.0),
    "right-bottom": (1.0, 0.0),
    "right-top": (1.0, 1.0),
    "left-top": (0.0, 1.0),
    "tl": (0.0, 1.0),
    "tr": (1.0, 1.0),
    "bl": (0.0, 0.0),
    "br": (1.0, 0.0),
}

_EDGE_CENTERS = {
    "bottom": (0.5, 0.0),
    "top": (0.5, 1.0),
    "left": (0.0, 0.5),
    "right": (1.0, 0.5),
}

_DEFAULT_CORNER_ORDER = ["bottom-left", "bottom-right", "top-right", "top-left"]
_DEFAULT_EDGE_ORDER = ["bottom", "right", "top", "left"]


def _text_block(ax: plt.Axes, lines: list[str], color: str = COLOURS["annotation"]) -> None:
    if not lines:
        lines = ["(none)"]
    text = "\n".join(lines)
    ax.text(
        0.5,
        0.5,
        text,
        ha="center",
        va="center",
        color=color,
        fontsize=11,
        family="monospace",
        bbox=dict(boxstyle="round,pad=1", facecolor="white", edgecolor="#DDDDDD", linewidth=1.5),
        linespacing=1.6,
    )


def _resolve_corner_positions(order: Sequence[str]) -> list[tuple[float, float]]:
    positions: list[tuple[float, float]] = []
    for idx, name in enumerate(order):
        key = name.lower()
        pos = _CORNER_POSITIONS.get(key)
        if pos is None:
            pos = _CORNER_POSITIONS[_DEFAULT_CORNER_ORDER[idx % 4]]
        positions.append(pos)
    return positions


def _resolve_edge_centers(order: Sequence[str]) -> list[tuple[float, float]]:
    centers: list[tuple[float, float]] = []
    for idx, name in enumerate(order):
        key = name.lower()
        pos = _EDGE_CENTERS.get(key)
        if pos is None:
            pos = _EDGE_CENTERS[_DEFAULT_EDGE_ORDER[idx % 4]]
        centers.append(pos)
    return centers


def _draw_square_with_labels(
    ax: plt.Axes,
    corner_labels: Sequence[Any],
    corner_order: Sequence[str],
    edge_order: Sequence[str],
    title: str,
) -> None:
    ax.set_xlim(-0.35, 1.35)
    ax.set_ylim(-0.35, 1.35)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=11, weight="semibold", pad=8)

    square = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
    ax.plot(square[:, 0], square[:, 1], "k-", linewidth=2.2, zorder=1)

    corner_positions = _resolve_corner_positions(corner_order)
    offsets = []
    for x, y in corner_positions:
        vx = x - 0.5
        vy = y - 0.5
        norm = math.hypot(vx, vy) or 1.0
        offsets.append((0.18 * vx / norm, 0.18 * vy / norm))

    if not hasattr(corner_labels, "__iter__") or isinstance(corner_labels, str):
        corner_labels = [corner_labels] * 4

    labels_list = list(corner_labels)
    if len(labels_list) < 4:
        labels_list.extend([0] * (4 - len(labels_list)))

    for (x, y), label, (ox, oy) in zip(corner_positions, labels_list, offsets):
        ax.scatter([x], [y], s=110, color=COLOURS["points"], edgecolors="white", linewidths=2, zorder=3)
        ax.text(
            x + ox,
            y + oy,
            str(label),
            ha="center",
            va="center",
            fontsize=13,
            weight="bold",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="#333", linewidth=1.2),
            zorder=4,
        )

    edge_centers = _resolve_edge_centers(edge_order)
    for idx, (x, y) in enumerate(edge_centers):
        ox = (x - 0.5) * 0.25
        oy = (y - 0.5) * 0.25
        ax.text(
            x + ox,
            y + oy,
            f"E{idx}",
            ha="center",
            va="center",
            fontsize=10,
            style="italic",
            color=COLOURS["annotation"],
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#F0F0F0", alpha=0.85),
            zorder=3,
        )

    return edge_centers


def _draw_edge_connections(
    ax: plt.Axes,
    connections: list,
    color: str,
    label: str,
    edge_centers: Sequence[tuple[float, float]],
    offset: float = 0.0,
    line_kwargs: Mapping[str, Any] | None = None,
) -> None:
    if not connections:
        return

    edge_centers = np.array(edge_centers)

    for idx, pair in enumerate(connections):
        if len(pair) != 2:
            continue
        i, j = sorted(pair)
        if i < 0 or i >= len(edge_centers) or j < 0 or j >= len(edge_centers):
            continue

        p1 = edge_centers[i]
        p2 = edge_centers[j]

        mid = (p1 + p2) / 2
        direction = mid - np.array([0.5, 0.5])
        perp = np.array([-direction[1], direction[0]])
        norm = np.linalg.norm(perp) or 1.0
        perp /= norm
        control = mid + offset * 0.3 * perp

        t = np.linspace(0, 1, 60)
        curve = ((1 - t)[:, None] ** 2) * p1 + 2 * (1 - t)[:, None] * t[:, None] * control + (t[:, None] ** 2) * p2

        plot_kwargs = {
            "color": color,
            "linewidth": 2.6,
            "alpha": 0.85,
            "label": label if idx == 0 else "",
            "zorder": 2,
        }
        if line_kwargs:
            plot_kwargs.update(dict(line_kwargs))

        ax.plot(
            curve[:, 0],
            curve[:, 1],
            **plot_kwargs,
        )


__all__ = [
    "_DEFAULT_CORNER_ORDER",
    "_DEFAULT_EDGE_ORDER",
    "_text_block",
    "_draw_square_with_labels",
    "_draw_edge_connections",
]
