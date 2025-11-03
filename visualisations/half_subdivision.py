"""Half subdivision neighbours task renderer."""

from __future__ import annotations

import ast
from collections.abc import Iterable, Mapping
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from visual_geometry_bench.datagen.half_subdivision_neighbours import (
    Dimension,
    Leaf,
    _build_subdivision,
)

from .render import register_renderer
from .styles import COLOURS


def _reconstruct_leaves(datagen_args: Mapping[str, Any]) -> list[Leaf]:
    """Reconstruct all leaf geometries from the stored tree parameters."""
    dim = Dimension.D2 if datagen_args.get("dim") == "D2" else Dimension.D3
    max_depth = int(datagen_args.get("max_depth", 6))
    min_depth = int(datagen_args.get("min_depth", 3))
    split_prob = float(datagen_args.get("split_prob", 0.7))
    start_axis = datagen_args.get("start_axis", "x")
    tree_seed = int(datagen_args.get("tree_seed", 0))

    rng = __import__("random").Random(tree_seed)
    from treelib import Tree

    tree = Tree()
    leaves = _build_subdivision(
        tree=tree,
        parent_id=None,
        label="",
        x0=0.0,
        y0=0.0,
        x1=1.0,
        y1=1.0,
        z0=0.0,
        z1=1.0,
        depth=0,
        max_depth=max_depth,
        min_depth=min_depth,
        split_prob=split_prob,
        start_axis=start_axis,
        dim=dim,
        rng=rng,
    )
    return leaves


def _draw_leaves(ax: plt.Axes, leaves: list[Leaf], *, highlight: set[str] | None = None, color: str = COLOURS["reference"]) -> None:
    for leaf in leaves:
        edgecolor = COLOURS["answer"] if highlight and leaf.label in highlight else color
        linewidth = 2.5 if highlight and leaf.label in highlight else 1.2
        rect = plt.Rectangle((leaf.x0, leaf.y0), leaf.x1 - leaf.x0, leaf.y1 - leaf.y0, fill=False, edgecolor=edgecolor, linewidth=linewidth, zorder=2)
        ax.add_patch(rect)
        if leaf.label:
            is_highlighted = highlight and leaf.label in highlight
            ax.text(
                (leaf.x0 + leaf.x1) / 2,
                (leaf.y0 + leaf.y1) / 2,
                leaf.label,
                ha="center",
                va="center",
                fontsize=10 if is_highlighted else 8,
                color="black" if is_highlighted else COLOURS["annotation"],
                weight="bold" if is_highlighted else "normal",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0.9) if is_highlighted else None,
            )


def _format_neighbour_set(neighbours: list[str]) -> str:
    if not neighbours:
        return "(none)"
    return ", ".join(sorted(neighbours))


def _coerce_string_list(answer: Any) -> list[str] | None:
    raw = answer
    if isinstance(raw, str):
        try:
            raw = ast.literal_eval(raw)
        except (ValueError, SyntaxError):
            return None
    if not isinstance(raw, Iterable):
        return None
    result = []
    for item in raw:
        if not isinstance(item, str):
            return None
        result.append(item)
    return result if result else None


def _render_half_subdivision(record: Mapping[str, Any], answer: Any, detail: bool) -> plt.Figure:
    datagen_args = record.get("datagen_args", {})
    leaves = _reconstruct_leaves(datagen_args)
    target_label = datagen_args.get("target_leaf", "")
    ground_truth = record.get("ground_truth", [])

    fig = plt.figure(figsize=(14, 7))
    fig.suptitle("half_subdivision_neighbours", fontsize=15, weight="bold")
    fig.patch.set_facecolor("white")
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 2], hspace=0.35, wspace=0.25)

    # Left column: textual info (GT and Answer)
    ax_gt = fig.add_subplot(gs[0, 0])
    ax_gt.set_axis_off()
    ax_gt.set_xlim(0, 1)
    ax_gt.set_ylim(0, 1)
    ax_gt.set_title("Ground truth", fontsize=13, weight="semibold", pad=10)
    gt_text = _format_neighbour_set(ground_truth)
    ax_gt.text(0.5, 0.5, gt_text, ha="center", va="center", fontsize=12, color=COLOURS["truth"],
               bbox=dict(boxstyle="round,pad=0.8", facecolor="white", edgecolor="#DDDDDD", linewidth=1.5))

    ax_ans = fig.add_subplot(gs[1, 0])
    ax_ans.set_axis_off()
    ax_ans.set_xlim(0, 1)
    ax_ans.set_ylim(0, 1)
    ax_ans.set_title("Answer", fontsize=13, weight="semibold", pad=10)
    parsed_answer = _coerce_string_list(answer)
    if parsed_answer is None:
        ans_text = "Invalid answer"
        ans_color = COLOURS["answer"]
    else:
        ans_text = _format_neighbour_set(parsed_answer)
        ans_color = COLOURS["answer"]
    ax_ans.text(0.5, 0.5, ans_text, ha="center", va="center", fontsize=12, color=ans_color,
                bbox=dict(boxstyle="round,pad=0.8", facecolor="white", edgecolor="#DDDDDD", linewidth=1.5))

    # Right column: spatial view (2D only for now)
    ax_spatial = fig.add_subplot(gs[:, 1])
    ax_spatial.set_title("Spatial view (2D)", fontsize=13, weight="semibold", pad=10)
    ax_spatial.set_aspect("equal")
    ax_spatial.set_xlim(-0.05, 1.05)
    ax_spatial.set_ylim(-0.05, 1.05)
    ax_spatial.grid(True, linestyle="--", linewidth=0.3, alpha=0.3, color="#CCCCCC")
    ax_spatial.set_facecolor("#FAFAFA")

    # Highlight target and answer neighbours
    highlight_set = set()
    if target_label:
        highlight_set.add(target_label)
    if parsed_answer:
        highlight_set.update(parsed_answer)

    _draw_leaves(ax_spatial, leaves, highlight=highlight_set)

    return fig


register_renderer("half_subdivision_neighbours", _render_half_subdivision)
