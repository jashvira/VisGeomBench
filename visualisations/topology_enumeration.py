"""Topology enumeration renderer."""

from __future__ import annotations

import ast
import math
from collections import Counter
from typing import Any, Mapping, Sequence

import matplotlib.pyplot as plt

from visual_geometry_bench.datagen.topology_enumeration import (
    canonicalize,
    get_solutions,
)
from visual_geometry_bench.datagen.utils import (
    CANONICAL_CORNER_ORDER,
    corner_order_permutation,
)

from .render import get_answer_label, register_renderer
from .styles import COLOURS

CORNER_COORDS = {
    "bottom-left": (0.1, 0.1),
    "bottom-right": (0.9, 0.1),
    "top-right": (0.9, 0.9),
    "top-left": (0.1, 0.9),
}
CENTER_POINT = (0.5, 0.5)


def _parse_topology_answer(answer: Any) -> tuple[list[tuple[int, int, int, int]] | None, list[str]]:
    errors: list[str] = []

    if isinstance(answer, str):
        try:
            raw = ast.literal_eval(answer)
        except (ValueError, SyntaxError):
            errors.append("Parse failure: could not evaluate string answer.")
            return None, errors
    elif isinstance(answer, Sequence) and not isinstance(answer, (str, bytes)):
        raw = list(answer)
    else:
        errors.append(f"Unsupported answer type: {type(answer).__name__}")
        return None, errors

    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        errors.append("Answer is not an iterable of tuples.")
        return None, errors

    tuples: list[tuple[int, int, int, int]] = []
    for idx, item in enumerate(raw):
        if not isinstance(item, (list, tuple)):
            errors.append(f"Entry {idx} is not a tuple/list: {item!r}")
            return None, errors
        if len(item) != 4:
            errors.append(f"Entry {idx} has length {len(item)} (expected 4).")
            return None, errors
        try:
            coerced = tuple(int(x) for x in item)
        except (TypeError, ValueError):
            errors.append(f"Entry {idx} contains non-integer values: {item!r}")
            return None, errors
        tuples.append(coerced)

    return tuples, errors


def _canonical_tuple(labels: Sequence[int], corner_order: Sequence[str]) -> tuple[int, int, int, int]:
    perm = corner_order_permutation(corner_order)
    return tuple(labels[perm[i]] for i in range(4))


def _segments_two_classes(canonical_labels: Sequence[int]) -> list[list[tuple[float, float]]]:
    counts = Counter(canonical_labels)
    if len(counts) != 2:
        return []

    # Single odd corner: connect odd corner -> center -> midpoint of opposite edge
    if 3 in counts.values():
        odd_label = next(label for label, count in counts.items() if count == 1)
        odd_idx = canonical_labels.index(odd_label)
        odd_corner = CANONICAL_CORNER_ORDER[odd_idx]
        odd_point = CORNER_COORDS[odd_corner]

        opposite_edge = {
            "bottom-left": ((CORNER_COORDS["top-left"][0] + CORNER_COORDS["top-right"][0]) / 2.0, 0.9),
            "bottom-right": (0.1, (CORNER_COORDS["top-right"][1] + CORNER_COORDS["bottom-right"][1]) / 2.0),
            "top-right": ((CORNER_COORDS["bottom-left"][0] + CORNER_COORDS["bottom-right"][0]) / 2.0, 0.1),
            "top-left": (0.9, (CORNER_COORDS["top-left"][1] + CORNER_COORDS["bottom-right"][1]) / 2.0),
        }[odd_corner]
        return [[odd_point, CENTER_POINT, opposite_edge]]

    # Adjacent same-class pairs
    if canonical_labels[0] == canonical_labels[1] and canonical_labels[2] == canonical_labels[3]:
        return [[(0.5, 0.15), (0.5, 0.85)]]
    if canonical_labels[0] == canonical_labels[3] and canonical_labels[1] == canonical_labels[2]:
        return [[(0.15, 0.5), (0.85, 0.5)]]

    # Alternating pattern forces diagonal crossing
    if canonical_labels[0] == canonical_labels[2] and canonical_labels[1] == canonical_labels[3]:
        return [[CORNER_COORDS["bottom-left"], CENTER_POINT, CORNER_COORDS["top-right"]]]
    if canonical_labels[1] == canonical_labels[3] and canonical_labels[0] == canonical_labels[2]:
        return [[CORNER_COORDS["bottom-right"], CENTER_POINT, CORNER_COORDS["top-left"]]]

    return []


def _segments_three_classes(canonical_labels: Sequence[int]) -> list[list[tuple[float, float]]]:
    anchors: dict[int, list[tuple[float, float]]] = {}
    for idx, label in enumerate(canonical_labels):
        corner = CANONICAL_CORNER_ORDER[idx]
        anchors.setdefault(label, []).append(CORNER_COORDS[corner])
    segments: list[list[tuple[float, float]]] = []
    for pts in anchors.values():
        if not pts:
            continue
        target = (
            sum(p[0] for p in pts) / len(pts),
            sum(p[1] for p in pts) / len(pts),
        )
        lerp = (
            CENTER_POINT[0] * 0.25 + target[0] * 0.75,
            CENTER_POINT[1] * 0.25 + target[1] * 0.75,
        )
        segments.append([CENTER_POINT, lerp])
    return segments


def _draw_configuration(
    ax: plt.Axes,
    labels: Sequence[int],
    corner_order: Sequence[str],
    n_classes: int,
    *,
    colour: str,
    linestyle: str,
    title: str,
) -> None:
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor("#FFFFFF")
    ax.spines[:].set_visible(False)

    ax.plot([0.1, 0.9, 0.9, 0.1, 0.1], [0.1, 0.1, 0.9, 0.9, 0.1], color="#4B5563", linewidth=1.4)

    for corner, label in zip(corner_order, labels, strict=True):
        x, y = CORNER_COORDS[corner]
        ax.scatter(
            x,
            y,
            s=230,
            color=COLOURS["points"],
            edgecolors="white",
            linewidths=1.5,
            zorder=3,
        )
        ax.text(x, y, str(label), color="white", weight="bold", fontsize=12, ha="center", va="center", zorder=4)

    canonical = _canonical_tuple(labels, corner_order)
    segments = (
        _segments_two_classes(canonical)
        if n_classes == 2
        else _segments_three_classes(canonical)
    )
    for seg in segments:
        xs, ys = zip(*seg)
        ax.plot(
            xs,
            ys,
            color=colour,
            linewidth=2.6,
            linestyle=linestyle,
            solid_capstyle="round",
        )

    ax.set_title(title, fontsize=9.5, pad=8)


def _compute_layout(sections):
    if not sections:
        return [], [], 1
    layouts = []
    height_units = []
    for _, items, _, _ in sections:
        count = len(items)
        if count == 0:
            layouts.append((0, 0))
            height_units.append(1)
            continue
        cols = min(3, max(1, math.ceil(math.sqrt(count))))
        rows = math.ceil(count / cols)
        layouts.append((rows, cols))
        height_units.append(rows or 1)
    total_rows = sum(height_units) or 1
    return layouts, height_units, total_rows


def _render_sections(
    fig: plt.Figure,
    sections: list[tuple[str, list[tuple[int, int, int, int]], str, str]],
    corner_order: Sequence[str],
    n_classes: int,
    *,
    layouts: Sequence[tuple[int, int]],
    height_units: Sequence[int],
) -> None:
    if not sections:
        return

    gs_outer = fig.add_gridspec(len(sections), 1, height_ratios=height_units, hspace=0.6)

    for idx, ((label, items, colour, linestyle), (rows, cols)) in enumerate(zip(sections, layouts, strict=True)):
        if not items:
            continue
        sub = gs_outer[idx].subgridspec(rows, cols, hspace=0.35, wspace=0.35)
        first_ax = None
        for case_idx, labels in enumerate(items):
            row = case_idx // cols
            col = case_idx % cols
            ax = fig.add_subplot(sub[row, col])
            if first_ax is None:
                first_ax = ax
            _draw_configuration(
                ax,
                labels,
                corner_order,
                n_classes,
                colour=colour,
                linestyle=linestyle,
                title=str(tuple(labels)),
            )
        total_slots = rows * cols
        for blank_idx in range(len(items), total_slots):
            row = blank_idx // cols
            col = blank_idx % cols
            fig.add_subplot(sub[row, col]).axis("off")
        if first_ax:
            bbox = first_ax.get_position(fig)
            fig.text(
                bbox.x0,
                bbox.y1 + 0.015,
                f"{label} (cases={len(items)})",
                color=colour,
                weight="semibold",
                fontsize=12,
                ha="left",
                va="bottom",
            )


def _split_solution_classes(tuples: list[tuple[int, int, int, int]]) -> tuple[list[tuple[int, int, int, int]], list[tuple[int, int, int, int]]]:
    odd_cases = []
    other_cases = []
    for tup in tuples:
        counts = Counter(tup)
        if 3 in counts.values():
            odd_cases.append(tup)
        else:
            other_cases.append(tup)
    return odd_cases, other_cases


def _build_sections(gt_tuples, answer_tuples, record):
    sections: list[tuple[str, list[tuple[int, int, int, int]], str, str]] = []
    if gt_tuples:
        odd, others = _split_solution_classes(gt_tuples)
        if odd:
            sections.append(("Ground truth – odd corner", odd, COLOURS["truth"], "-"))
        if others:
            sections.append(("Ground truth – alternation/pairs", others, COLOURS["truth"], "-"))
    if answer_tuples:
        sections.append((get_answer_label(record, default="Model answers"), answer_tuples, COLOURS["answer"], "--"))
    return [s for s in sections if s[1]]


def _render_topology_enumeration(
    record: Mapping[str, Any],
    answer: Any,
    detail: bool,
    *,
    show: bool | None = None,
) -> plt.Figure:
    datagen_args = record.get("datagen_args", {})
    corner_order = tuple(datagen_args.get("corner_order", CANONICAL_CORNER_ORDER))
    n_classes = int(datagen_args.get("n_classes", 2))

    gt_tuples = [tuple(int(x) for x in cfg) for cfg in record.get("ground_truth", [])]
    parsed_answers, _ = _parse_topology_answer(answer) if answer is not None else (None, [])
    answer_tuples = parsed_answers or []

    sections = _build_sections(gt_tuples, answer_tuples, record)
    if not sections:
        sections = [("Ground truth", gt_tuples or [], COLOURS["truth"], "-")]

    layouts, height_units, total_rows = _compute_layout(sections)
    fig_height = 2.5 * total_rows + 1.5
    max_cases = max((len(items) for _, items, _, _ in sections), default=1)
    fig_width = max(6.5, 3.2 * min(3, max_cases))
    fig = plt.figure(figsize=(fig_width, fig_height))
    fig.suptitle("Topology Enumeration", fontsize=15, weight="bold")
    fig.patch.set_facecolor("white")

    if sections and layouts:
        _render_sections(fig, sections, corner_order, n_classes, layouts=layouts, height_units=height_units)
    else:
        ax = fig.add_subplot(111)
        ax.axis("off")
        ax.text(0.5, 0.5, "No configurations available.", ha="center", va="center", color=COLOURS["failure_text"])

    fig.text(
        0.5,
        0.04,
        f"Corner order (prompt): {corner_order} • n_classes={n_classes}",
        ha="center",
        va="center",
        fontsize=10,
        color=COLOURS["annotation"],
    )

    return fig


register_renderer("topology_enumeration", _render_topology_enumeration)
