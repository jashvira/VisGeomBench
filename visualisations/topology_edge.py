"""Topology edge task renderer."""

from __future__ import annotations

import ast
import math
import re
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from visual_geometry_bench.datagen.topology_edge_tasks import (
    CLASS_DICT,
    QUAD_EDGE_DICT,
    TRIPLE_EDGE_DICT,
    _CANONICAL_EDGE_ORDER,
    _edge_index_map as datagen_edge_index_map,
    _reindex_pairs_from_canonical as datagen_reindex_pairs,
    _resolve_cases as datagen_resolve_cases,
)
from visual_geometry_bench.datagen.utils import (
    canonicalize_first_occurrence,
    corner_order_permutation,
    permute_config,
)

from .render import register_renderer
from .styles import COLOURS
from .topology_common import (
    _DEFAULT_CORNER_ORDER,
    _DEFAULT_EDGE_ORDER,
    _draw_edge_connections,
    _draw_square_with_labels,
)

_PROMPT_TUPLE_PATTERN = re.compile(r"\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)")


def _extract_cases_from_prompt(prompt: str) -> list[tuple[int, int, int, int]]:
    matches = _PROMPT_TUPLE_PATTERN.findall(prompt or "")
    return [tuple(map(int, m)) for m in matches]


def _resolved_cases_from_args(
    datagen_args: Mapping[str, Any],
    corner_order: Sequence[str],
) -> list[tuple[int, int, int, int]] | None:
    """Resolve cases via datagen helper to avoid duplicate logic."""
    cases_arg = datagen_args.get("cases")
    if not isinstance(cases_arg, Sequence):
        return None
    try:
        resolved = datagen_resolve_cases(cases_arg, tuple(corner_order))
    except Exception:
        return None
    configs: list[tuple[int, int, int, int]] = []
    for item in resolved:
        cfg = item.get("config")
        if not isinstance(cfg, Sequence) or len(cfg) != 4:
            return None
        configs.append(tuple(int(v) for v in cfg))
    return configs


def _canonical_key(
    config: Sequence[int],
    corner_order: Sequence[str],
) -> tuple[int, int, int, int] | None:
    try:
        perm = corner_order_permutation(corner_order)
    except ValueError:
        return None
    cfg_canon_order = permute_config(tuple(config), perm)
    return canonicalize_first_occurrence(cfg_canon_order, start_label=1)


def _behaviour_for_config(
    config: Sequence[int],
    corner_order: Sequence[str],
) -> str | None:
    key = _canonical_key(config, corner_order)
    if key is None:
        return None
    return CLASS_DICT.get(key)


def _known_behaviour_edges(
    config: Sequence[int],
    corner_order: Sequence[str],
    edge_order: Sequence[str],
) -> list[list[int]]:
    key = _canonical_key(config, corner_order)
    if key is None:
        return []
    pairs_canon = QUAD_EDGE_DICT.get(key)
    if not pairs_canon:
        return []
    try:
        return datagen_reindex_pairs(pairs_canon, edge_order)
    except ValueError:
        return []


def _three_domain_edge_indices(
    config: Sequence[int],
    corner_order: Sequence[str],
    edge_order: Sequence[str],
) -> list[int]:
    key = _canonical_key(config, corner_order)
    if key is None:
        return []
    edge_names = TRIPLE_EDGE_DICT.get(key)
    if not edge_names:
        return []
    try:
        name_to_index = datagen_edge_index_map(edge_order)
    except ValueError:
        name_to_index = datagen_edge_index_map(_CANONICAL_EDGE_ORDER)
    return [name_to_index[name] for name in edge_names if name in name_to_index]


def _draw_triple_spokes(
    ax: plt.Axes,
    edge_centers: Sequence[tuple[float, float]],
    edge_indices: Sequence[int],
    color: str,
) -> None:
    """Draw radial spokes from edge centers to the square centre."""
    if not edge_indices:
        return

    center = np.array([0.5, 0.5])
    for idx, edge_idx in enumerate(edge_indices):
        if edge_idx < 0 or edge_idx >= len(edge_centers):
            continue
        target = np.array(edge_centers[edge_idx])
        ax.plot(
            [center[0], target[0]],
            [center[1], target[1]],
            color=color,
            linewidth=2.6,
            alpha=0.9,
            solid_capstyle="round",
            label="Ground truth" if idx == 0 else "",
            zorder=2,
        )


def _render_topology_edge(
    record: Mapping[str, Any],
    answer: Any,
    detail: bool,
    *,
    show: bool | None = None,
) -> plt.Figure:
    _ = show
    datagen_args = record.get("datagen_args", {})
    corner_order = datagen_args.get("corner_order", _DEFAULT_CORNER_ORDER)
    edge_order = datagen_args.get("edge_order", _DEFAULT_EDGE_ORDER)
    subtask = datagen_args.get("subtask", "enumerate_edges")

    resolved_cases = _resolved_cases_from_args(datagen_args, corner_order)
    cases: list[tuple[int, int, int, int]] = list(resolved_cases or [])
    corner_order = datagen_args.get("corner_order", _DEFAULT_CORNER_ORDER)
    is_classify = subtask == "classify_behaviour"
    ground_truth = record.get("ground_truth") or []

    if not cases or not all(isinstance(c, (list, tuple)) and len(c) >= 4 for c in cases):
        prompt = record.get("prompt", "")
        extracted_cases = _extract_cases_from_prompt(prompt)
        if extracted_cases:
            cases = extracted_cases
        else:
            cases = [tuple([0, 0, 0, 0])]

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

    num_cases = max(len(cases), len(ground_truth), len(parsed_answer))
    while len(cases) < num_cases:
        cases.append(tuple([0, 0, 0, 0]))
    while len(ground_truth) < num_cases:
        ground_truth.append("" if is_classify else [])
    while len(parsed_answer) < num_cases:
        parsed_answer.append("" if is_classify else [])

    ncols = min(3, max(1, num_cases))
    nrows = math.ceil(num_cases / ncols)

    fig, axes = plt.subplots(nrows, ncols, figsize=(4.2 * ncols, 4.2 * nrows))
    fig.suptitle(
        "Topology Edge • Guaranteed edge connections",
        fontsize=15,
        weight="bold",
        y=0.98,
    )
    fig.subplots_adjust(top=0.84, bottom=0.12)
    fig.patch.set_facecolor("white")

    config_caption = (
        f"Corner order: {tuple(corner_order)} • "
        f"Edge order: {tuple(edge_order)}"
    )
    fig.text(
        0.5,
        0.05,
        config_caption,
        ha="center",
        va="center",
        fontsize=10,
        color=COLOURS["annotation"],
    )

    if num_cases == 1:
        axes = np.array([axes])
    axes = axes.flatten()

    edge_order_tuple = tuple(edge_order)
    try:
        datagen_edge_index_map(edge_order_tuple)
    except ValueError:
        edge_order_tuple = tuple(_DEFAULT_EDGE_ORDER)
        datagen_edge_index_map(edge_order_tuple)

    corner_order_tuple = tuple(corner_order)
    legend_handles: list[Any] | None = None
    legend_labels: list[str] | None = None

    behaviours_gt: list[str | None] = [None] * num_cases
    if is_classify:
        for idx in range(num_cases):
            label = None
            if idx < len(ground_truth) and isinstance(ground_truth[idx], str):
                label = ground_truth[idx]
            if label is None and idx < len(cases):
                label = _behaviour_for_config(cases[idx], corner_order_tuple)
            behaviours_gt[idx] = label

    for idx in range(num_cases):
        ax = axes[idx]
        case_labels = cases[idx]
        triple_spokes: list[int] = []
        if is_classify:
            gt_label = behaviours_gt[idx]
            gt_connections = (
                _known_behaviour_edges(case_labels, corner_order_tuple, edge_order_tuple)
                if gt_label and gt_label.strip().lower() == "known behaviour"
                else []
            )
            ans_connections: list[Any] = []
            if gt_label and gt_label.strip().lower() == "three domains meeting":
                triple_spokes = _three_domain_edge_indices(
                    case_labels,
                    corner_order_tuple,
                    edge_order_tuple,
                )
        else:
            gt_connections = ground_truth[idx] if idx < len(ground_truth) else []
            ans_connections = parsed_answer[idx] if idx < len(parsed_answer) else []

        if is_classify:
            title_label = behaviours_gt[idx] or "unknown"
            title_text = f"{title_label}\nSquare {idx + 1}: {tuple(case_labels)}"
        else:
            title_text = f"Square {idx + 1}: {tuple(case_labels)}"

        edge_centers = _draw_square_with_labels(
            ax,
            case_labels,
            corner_order,
            edge_order,
            title_text,
        )

        _draw_edge_connections(
            ax,
            gt_connections,
            COLOURS["truth"],
            "Ground truth",
            edge_centers,
            offset=1.0,
            line_kwargs={"solid_capstyle": "round"},
        )

        if triple_spokes:
            _draw_triple_spokes(ax, edge_centers, triple_spokes, COLOURS["truth"])

        if not is_classify:
            _draw_edge_connections(
                ax,
                ans_connections,
                COLOURS["answer"],
                "Model answers",
                edge_centers,
                offset=-1.0,
                line_kwargs={
                    "linestyle": (0, (5, 3)),
                    "dash_capstyle": "round",
                    "dash_joinstyle": "round",
                },
            )

        if legend_handles is None:
            handles, labels = ax.get_legend_handles_labels()
            if handles:
                legend_handles = handles
                legend_labels = labels

    for idx in range(num_cases, len(axes)):
        axes[idx].axis("off")

    if legend_handles and (not is_classify or len(legend_handles) > 1):
        fig.legend(
            legend_handles,
            legend_labels,
            loc="upper center",
            bbox_to_anchor=(0.5, 0.91),
            ncol=len(legend_handles),
            fontsize=10,
            framealpha=0.95,
        )

    return fig


register_renderer("topology_edge_tasks", _render_topology_edge)
