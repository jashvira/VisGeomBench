"""Topology enumeration renderer."""

from __future__ import annotations

import ast
import math
from collections import Counter
from typing import Any, Mapping, Sequence

import matplotlib.pyplot as plt

from visual_geometry_bench.datagen.utils import (
    CANONICAL_CORNER_ORDER,
    corner_order_permutation,
)

from .render import (
    get_answer_label,
    register_renderer,
    should_render_answers,
    should_render_truth,
)
from .styles import COLOURS
from .topology_common import (
    _DEFAULT_CORNER_ORDER,
    _DEFAULT_EDGE_ORDER,
    _draw_square_with_labels,
)

CENTER_POINT = (0.5, 0.5)
EDGE_MIDPOINTS = [
    (0.5, 0.0),  # bottom
    (1.0, 0.5),  # right
    (0.5, 1.0),  # top
    (0.0, 0.5),  # left
]


def _parse_topology_answer(answer: Any) -> tuple[list[tuple[int, int, int, int]] | None, list[str]]:
    errors: list[str] = []

    if isinstance(answer, str):
        try:
            raw = ast.literal_eval(answer)
        except (ValueError, SyntaxError):
            errors.append("Could not parse answer string as Python literal.")
            return None, errors
    elif isinstance(answer, Sequence) and not isinstance(answer, (str, bytes)):
        raw = list(answer)
    else:
        errors.append(f"Unsupported answer type: {type(answer).__name__}")
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
            tuples.append(tuple(int(val) for val in item))
        except (TypeError, ValueError):
            errors.append(f"Entry {idx} contains non-integer values: {item!r}")
            return None, errors
    return tuples, errors


def _canonical_tuple(labels: Sequence[int], corner_order: Sequence[str]) -> tuple[int, int, int, int]:
    perm = corner_order_permutation(corner_order)
    return tuple(labels[perm[i]] for i in range(4))


def _segments_two_classes(canonical_labels: Sequence[int]) -> list[list[tuple[float, float]]]:
    counts = Counter(canonical_labels)
    if len(counts) != 2:
        return []

    # Determine which edges have differing labels (marching squares)
    diff_edges: list[int] = []
    for edge_idx in range(4):
        a = canonical_labels[edge_idx]
        b = canonical_labels[(edge_idx + 1) % 4]
        if a != b:
            diff_edges.append(edge_idx)

    if len(diff_edges) == 2:
        return [[EDGE_MIDPOINTS[diff_edges[0]], EDGE_MIDPOINTS[diff_edges[1]]]]
    if len(diff_edges) == 4:
        return [
            [EDGE_MIDPOINTS[diff_edges[0]], EDGE_MIDPOINTS[diff_edges[2]]],
            [EDGE_MIDPOINTS[diff_edges[1]], EDGE_MIDPOINTS[diff_edges[3]]],
        ]
    return []


def _segments_three_classes(canonical_labels: Sequence[int]) -> list[list[tuple[float, float]]]:
    segments: list[list[tuple[float, float]]] = []
    diff_edges = []
    for edge_idx in range(4):
        a = canonical_labels[edge_idx]
        b = canonical_labels[(edge_idx + 1) % 4]
        if a != b:
            diff_edges.append(edge_idx)
    for edge_idx in diff_edges:
        mid = EDGE_MIDPOINTS[edge_idx]
        segments.append([CENTER_POINT, mid])
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
    _draw_square_with_labels(
        ax,
        labels,
        corner_order,
        _DEFAULT_EDGE_ORDER,
        title=title,
    )
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
    ax.set_xlim(-0.35, 1.35)
    ax.set_ylim(-0.35, 1.35)


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
        sub = gs_outer[idx].subgridspec(rows, cols, hspace=0.45, wspace=0.45)
        section_axes: list[plt.Axes] = []
        for case_idx, labels in enumerate(items):
            row = case_idx // cols
            col = case_idx % cols
            ax = fig.add_subplot(sub[row, col])
            section_axes.append(ax)
            _draw_configuration(
                ax,
                labels,
                corner_order,
                n_classes,
                colour=colour,
                linestyle=linestyle,
                title=f"Case {case_idx + 1}: {tuple(labels)}",
            )
        total_slots = rows * cols
        for blank_idx in range(len(items), total_slots):
            row = blank_idx // cols
            col = blank_idx % cols
            fig.add_subplot(sub[row, col]).axis("off")
        # Intentionally omit section-level text labels to keep the canvas uncluttered.


def _build_sections(
    record: Mapping[str, Any],
    gt_tuples: list[tuple[int, int, int, int]],
    answer_tuples: list[tuple[int, int, int, int]],
):
    sections: list[tuple[str, list[tuple[int, int, int, int]], str, str]] = []
    if should_render_truth(record) and gt_tuples:
        sections.append(("Ground truth", gt_tuples, COLOURS["truth"], "-"))
    if should_render_answers(record) and answer_tuples:
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
    corner_order = tuple(datagen_args.get("corner_order", _DEFAULT_CORNER_ORDER))
    n_classes = int(datagen_args.get("n_classes", 2))

    gt_tuples = [tuple(int(x) for x in cfg) for cfg in record.get("ground_truth", [])]
    answer_tuples: list[tuple[int, int, int, int]] = []
    if should_render_answers(record):
        parsed_answers, _ = _parse_topology_answer(answer)
        if parsed_answers:
            answer_tuples = parsed_answers

    sections = _build_sections(record, gt_tuples, answer_tuples)
    if not sections:
        fallback_label = "Ground truth" if should_render_truth(record) else get_answer_label(record, default="Model answers")
        fallback_colour = COLOURS["truth"] if should_render_truth(record) else COLOURS["answer"]
        fallback_cases = gt_tuples if should_render_truth(record) else answer_tuples
        sections = [(fallback_label, fallback_cases or [], fallback_colour, "-")]

    layouts, height_units, total_rows = _compute_layout(sections)
    fig_height = 2.5 * total_rows + 1.5
    max_cases = max((len(items) for _, items, _, _ in sections), default=1)
    fig_width = max(6.5, 3.2 * min(3, max_cases))
    fig = plt.figure(figsize=(fig_width, fig_height))
    fig.suptitle("Topology Enumeration", fontsize=15, weight="bold", y=0.97)
    fig.subplots_adjust(top=0.85, bottom=0.12)
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
