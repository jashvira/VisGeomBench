"""Topology edge task renderer."""

from __future__ import annotations

import ast
import math
import re
from collections.abc import Iterable, Mapping
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

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


def _render_topology_edge(
    record: Mapping[str, Any],
    answer: Any,
    detail: bool,
    *,
    show: bool | None = None,
) -> plt.Figure:
    _ = show
    datagen_args = record.get("datagen_args", {})
    cases = datagen_args.get("cases", [])
    corner_order = datagen_args.get("corner_order", _DEFAULT_CORNER_ORDER)
    edge_order = datagen_args.get("edge_order", _DEFAULT_EDGE_ORDER)
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
        ground_truth.append([])
    while len(parsed_answer) < num_cases:
        parsed_answer.append([])

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

        _draw_edge_connections(
            ax,
            gt_connections,
            COLOURS["truth"],
            "Ground truth",
            edge_centers,
            offset=1.0,
        )

        _draw_edge_connections(
            ax,
            ans_connections,
            COLOURS["answer"],
            "Model answer",
            edge_centers,
            offset=-1.0,
        )

        if idx == 0 and (gt_connections or ans_connections):
            handles, labels = ax.get_legend_handles_labels()
            if handles:
                ax.legend(loc="upper left", fontsize=9, framealpha=0.9)

    for idx in range(num_cases, len(axes)):
        axes[idx].axis("off")

    return fig


register_renderer("topology_edge_tasks", _render_topology_edge)
