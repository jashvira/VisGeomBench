"""Topology task renderers (edge tasks, enumeration)."""

from __future__ import annotations

import ast
import math
import re
from collections.abc import Iterable, Mapping
from typing import Any, Sequence

import matplotlib.pyplot as plt
import numpy as np

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

from .render import register_renderer
from .styles import COLOURS

_TEXT_FONTSIZE = 11
_TITLE_STYLE = dict(fontsize=13, weight="bold")


def _format_cases(record: Mapping[str, Any]) -> list[str]:
    datagen_args = record.get("datagen_args", {})
    corner_order = datagen_args.get("corner_order")
    cases = datagen_args.get("cases", [])
    lines: list[str] = []
    if corner_order:
        lines.append(f"corner_order={tuple(corner_order)}")
    for idx, case in enumerate(cases):
        lines.append(f"[{idx}] {tuple(case)}")
    if not lines:
        prompt = record.get("prompt", "")
        lines.extend(prompt.splitlines())
    return lines


def _create_two_text_axes(fig: plt.Figure) -> tuple[plt.Axes, plt.Axes]:
    gs = fig.add_gridspec(2, 1, hspace=0.25)
    axes = [fig.add_subplot(gs[i, 0]) for i in range(2)]
    titles = ["Ground truth", "Answer"]
    for ax, title in zip(axes, titles, strict=True):
        ax.set_axis_off()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title(title, fontsize=13, weight="semibold", pad=10)
    return tuple(axes)


def _text_block(ax: plt.Axes, lines: list[str], color: str = COLOURS["annotation"]) -> None:
    if not lines:
        lines = ["(none)"]
    # Create table-like layout with better spacing
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
    """Draw a unit square with corner labels and edge indices."""
    ax.set_xlim(-0.35, 1.35)
    ax.set_ylim(-0.35, 1.35)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=11, weight="semibold", pad=8)

    # Draw square
    square = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
    ax.plot(square[:, 0], square[:, 1], 'k-', linewidth=2.2, zorder=1)

    corner_positions = _resolve_corner_positions(corner_order)
    offsets = []
    for x, y in corner_positions:
        vx = x - 0.5
        vy = y - 0.5
        norm = math.hypot(vx, vy) or 1.0
        offsets.append((0.18 * vx / norm, 0.18 * vy / norm))

    # Ensure corner_labels is iterable
    if not hasattr(corner_labels, '__iter__') or isinstance(corner_labels, str):
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
) -> None:
    """Draw arcs showing which edges connect using supplied edge centres."""
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

        ax.plot(
            curve[:, 0],
            curve[:, 1],
            color=color,
            linewidth=2.6,
            alpha=0.85,
            label=label if idx == 0 else "",
            zorder=2,
        )


_PROMPT_TUPLE_PATTERN = re.compile(r"\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)")


def _extract_cases_from_prompt(prompt: str) -> list[tuple[int, int, int, int]]:
    """Extract corner label tuples from prompt text."""
    matches = _PROMPT_TUPLE_PATTERN.findall(prompt or "")
    return [tuple(map(int, m)) for m in matches]


def _render_topology_edge(record: Mapping[str, Any], answer: Any, detail: bool) -> plt.Figure:
    """Render topology edge tasks with visual square diagrams."""
    datagen_args = record.get("datagen_args", {})
    cases = datagen_args.get("cases", [])
    corner_order = datagen_args.get("corner_order", _DEFAULT_CORNER_ORDER)
    edge_order = datagen_args.get("edge_order", _DEFAULT_EDGE_ORDER)
    ground_truth = record.get("ground_truth") or []

    # If cases aren't explicit tuples, attempt to parse from prompt
    if not cases or not all(isinstance(c, (list, tuple)) and len(c) >= 4 for c in cases):
        prompt = record.get("prompt", "")
        extracted_cases = _extract_cases_from_prompt(prompt)
        if extracted_cases:
            cases = extracted_cases
        else:
            # Fall back to zero square if still unavailable
            cases = [tuple([0, 0, 0, 0])]

    # Parse answer
    parsed_answer: list[Any] | None = None
    if isinstance(answer, str):
        try:
            parsed_answer = ast.literal_eval(answer)
        except (ValueError, SyntaxError):
            parsed_answer = None
    elif isinstance(answer, Iterable):
        parsed_answer = list(answer)

    if parsed_answer is None:
        parsed_answer = [[] for _ in cases]

    # Ensure we have matching lengths
    num_cases = max(len(cases), len(ground_truth), len(parsed_answer))
    while len(cases) < num_cases:
        cases.append(tuple([0, 0, 0, 0]))
    while len(ground_truth) < num_cases:
        ground_truth.append([])
    while len(parsed_answer) < num_cases:
        parsed_answer.append([])

    # Layout: create grid of squares
    ncols = min(3, max(1, num_cases))
    nrows = math.ceil(num_cases / ncols)

    fig, axes = plt.subplots(nrows, ncols, figsize=(4.2 * ncols, 4.2 * nrows))
    fig.suptitle("topology_edge_tasks • Guaranteed edge connections", fontsize=15, weight="bold")
    fig.patch.set_facecolor("white")

    if num_cases == 1:
        axes = np.array([axes])
    axes = axes.flatten()

    for idx in range(num_cases):
        ax = axes[idx]
        case_labels = cases[idx]
        gt_connections = ground_truth[idx] if idx < len(ground_truth) else []
        ans_connections = parsed_answer[idx] if idx < len(parsed_answer) else []

        edge_centers = _draw_square_with_labels(
            ax,
            case_labels,
            corner_order,
            edge_order,
            f"Square {idx + 1}: {tuple(case_labels)}",
        )

        # Draw ground truth connections (green)
        _draw_edge_connections(
            ax,
            gt_connections,
            COLOURS["truth"],
            "Ground truth",
            edge_centers,
            offset=1.0,
        )

        # Draw model answer connections (red, offset slightly)
        _draw_edge_connections(
            ax,
            ans_connections,
            COLOURS["answer"],
            "Model answer",
            edge_centers,
            offset=-1.0,
        )

        # Add legend for first square only if there are actual connections with labels
        if idx == 0 and (gt_connections or ans_connections):
            handles, labels = ax.get_legend_handles_labels()
            if handles:
                ax.legend(loc="upper left", fontsize=9, framealpha=0.9)

    # Hide extra axes
    for idx in range(num_cases, len(axes)):
        axes[idx].axis("off")

    return fig


def _render_topology_enumeration(record: Mapping[str, Any], answer: Any, detail: bool) -> plt.Figure:
    fig = plt.figure(figsize=(12, 6))
    fig.suptitle("topology_enumeration", fontsize=15, weight="bold")
    fig.patch.set_facecolor("white")
    ax_gt, ax_ans = _create_two_text_axes(fig)

    ground_truth = record.get("ground_truth", [])
    gt_lines = [str(tuple(cfg)) for cfg in ground_truth]
    _text_block(ax_gt, gt_lines, color=COLOURS["truth"])

    parsed_answer: list[Any] | None = None
    if isinstance(answer, str):
        try:
            parsed_answer = ast.literal_eval(answer)
        except (ValueError, SyntaxError):
            parsed_answer = None
    elif isinstance(answer, Iterable) and not isinstance(answer, (int, float, bool)):
        parsed_answer = list(answer)

    if parsed_answer is None:
        _text_block(ax_ans, ["Invalid answer"], color=COLOURS["answer"])
    else:
        ans_lines = [str(tuple(cfg)) for cfg in parsed_answer]
        _text_block(ax_ans, ans_lines, color=COLOURS["answer"])

    return fig


register_renderer("topology_edge_tasks", _render_topology_edge)
register_renderer("topology_enumeration", _render_topology_enumeration)
