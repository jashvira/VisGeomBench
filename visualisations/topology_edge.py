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
    corner_order_raw = datagen_args.get("corner_order", _DEFAULT_CORNER_ORDER)
    edge_order_raw = datagen_args.get("edge_order", _DEFAULT_EDGE_ORDER)
    corner_order_tuple = tuple(corner_order_raw)
    edge_order_tuple = tuple(edge_order_raw)
    corner_order_display = list(corner_order_tuple)
    edge_order_display = list(edge_order_tuple)
    subtask = datagen_args.get("subtask", "enumerate_edges")
    model_label = get_answer_label(record, default="Model answers")
    render_truth = should_render_truth(record)
    render_answers = should_render_answers(record)
    if not render_truth and not render_answers:
        render_truth = True

    resolved_cases = _resolved_cases_from_args(datagen_args, corner_order_tuple)
    cases: list[tuple[int, int, int, int]] = list(resolved_cases or [])
    is_classify = subtask == "classify_behaviour"
    ground_truth_raw = record.get("ground_truth") or []
    ground_truth = list(ground_truth_raw) if isinstance(ground_truth_raw, list) else [ground_truth_raw]

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

    def _padded(seq: list[Any], fill: Any) -> list[Any]:
        if len(seq) >= num_cases:
            return list(seq)
        return list(seq) + [fill] * (num_cases - len(seq))

    default_case = (0, 0, 0, 0)
    default_gt = "" if is_classify else []
    default_ans = "" if is_classify else []

    cases = _padded(cases, default_case)
    ground_truth = _padded(ground_truth, default_gt)
    parsed_answer = _padded(parsed_answer, default_ans)

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
        f"Corner order: {corner_order_tuple} • "
        f"Edge order: {edge_order_tuple}"
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

    try:
        datagen_edge_index_map(edge_order_tuple)
    except ValueError:
        edge_order_tuple = tuple(_DEFAULT_EDGE_ORDER)
        datagen_edge_index_map(edge_order_tuple)

    legend_entries: dict[str, Any] = {}

    behaviours_gt: list[str | None] = [None] * num_cases
    answer_labels: list[str | None] = [None] * num_cases
    if is_classify:
        for idx in range(num_cases):
            label = None
            if idx < len(ground_truth) and isinstance(ground_truth[idx], str):
                label = ground_truth[idx]
            if label is None and idx < len(cases):
                label = _behaviour_for_config(cases[idx], corner_order_tuple)
            behaviours_gt[idx] = label

            ans_raw = parsed_answer[idx]
            coerced = None
            if isinstance(ans_raw, str):
                coerced = ans_raw.strip() or None
            elif isinstance(ans_raw, (list, tuple)) and ans_raw:
                head = ans_raw[0]
                if isinstance(head, str):
                    coerced = head.strip() or None
            elif ans_raw not in (None, ""):
                coerced = str(ans_raw).strip() or None
            answer_labels[idx] = coerced

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
            corner_order_display,
            edge_order_display,
            title_text,
        )

        if render_truth:
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

        if render_answers and not is_classify:
            _draw_edge_connections(
                ax,
                ans_connections,
                COLOURS["answer"],
                model_label,
                edge_centers,
                offset=-1.0,
                line_kwargs={
                    "linestyle": (0, (5, 3)),
                    "dash_capstyle": "round",
                    "dash_joinstyle": "round",
                },
            )

        if is_classify and render_answers:
            ans_label = answer_labels[idx] or "(no answer)"
            ax.text(
                0.5,
                -0.12,
                f"Model: {ans_label}",
                transform=ax.transAxes,
                ha="center",
                va="top",
                fontsize=10,
                color=COLOURS["answer"],
            )

        handles, labels = ax.get_legend_handles_labels()
        for handle, label in zip(handles, labels, strict=False):
            if label and label not in legend_entries:
                legend_entries[label] = handle

    for idx in range(num_cases, len(axes)):
        axes[idx].axis("off")

    if legend_entries and (not is_classify or len(legend_entries) > 1):
        legend_handles = list(legend_entries.values())
        legend_labels = list(legend_entries.keys())
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
