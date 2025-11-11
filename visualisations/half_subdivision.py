"""Half subdivision neighbours task renderer."""

from __future__ import annotations

import ast
import random
from collections.abc import Iterable, Mapping
from typing import Any

import numpy as np
from treelib import Tree
import matplotlib.pyplot as plt
from matplotlib.backend_bases import PickEvent
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from visual_geometry_bench.datagen.half_subdivision_neighbours import (
    Dimension,
    Leaf,
    _build_subdivision,
    _prepare_case,
)

from .render import get_answer_label, register_renderer
from .styles import COLOURS


def _generate_case(
    datagen_args: Mapping[str, Any],
) -> tuple[list[Leaf], Dimension, tuple[str, ...], str, list[str]]:
    """Resolve subdivision details using the canonical datagen helper."""

    args = dict(datagen_args)
    tree_text, target_leaf, neighbour_leaves, runtime = _prepare_case(args)
    _ = tree_text  # textual tree not currently displayed, but generation stays in sync

    dim_key = str(runtime.get("dimension", "2D")).upper()
    if dim_key in {"2D", "D2"}:
        dim = Dimension.D2
    elif dim_key in {"3D", "D3"}:
        dim = Dimension.D3
    else:
        raise ValueError(f"Unsupported dimension '{dim_key}' in runtime info")

    axis_cycle_raw = runtime.get("axis_cycle", [])
    if not axis_cycle_raw:
        axis_cycle_raw = ["x", "y"] if dim == Dimension.D2 else ["x", "y", "z"]
    axis_cycle = tuple(str(axis).lower() for axis in axis_cycle_raw)
    allowed_axes = {"x", "y"} if dim == Dimension.D2 else {"x", "y", "z"}
    invalid_axes = [axis for axis in axis_cycle if axis not in allowed_axes]
    if invalid_axes:
        raise ValueError(
            f"axis_cycle contains invalid axes {invalid_axes} for dimension {dim.name}. "
            f"Allowed: {sorted(allowed_axes)}"
        )

    max_depth = int(runtime.get("max_depth", args.get("max_depth", 6)))
    min_depth = int(runtime.get("min_depth", args.get("min_depth", 3)))
    split_prob = float(runtime.get("split_prob", args.get("split_prob", 0.7)))
    seed = int(runtime.get("seed", args.get("seed", 0)))

    rng = random.Random(seed)

    tree = Tree()
    bounds = {"x0": 0.0, "y0": 0.0, "x1": 1.0, "y1": 1.0}
    if dim == Dimension.D3:
        bounds.update({"z0": 0.0, "z1": 1.0})

    leaves = _build_subdivision(
        tree=tree,
        parent_id=None,
        label="",
        depth=0,
        max_depth=max_depth,
        min_depth=min_depth,
        split_prob=split_prob,
        axis_cycle=axis_cycle,
        dim=dim,
        rng=rng,
        **bounds,
    )

    target_label = target_leaf.label or ""
    neighbour_labels = [leaf.label or "" for leaf in neighbour_leaves]

    return leaves, dim, axis_cycle, target_label, neighbour_labels


def _draw_leaves(
    ax: plt.Axes,
    leaves: list[Leaf],
    *,
    target_label: str | None = None,
    ground_truth_labels: Iterable[str] | None = None,
    model_answer_labels: Iterable[str] | None = None,
    correct_labels: Iterable[str] | None = None,
    missed_labels: Iterable[str] | None = None,
    extra_labels: Iterable[str] | None = None,
    base_colour: str = COLOURS["annotation"],
) -> list[plt.Artist]:
    """Outline all leaves, with explicit colours for target/correct/missed/extra cells."""

    gt_set = {(label or "") for label in (ground_truth_labels or []) if isinstance(label, str)}
    model_set = {(label or "") for label in (model_answer_labels or []) if isinstance(label, str)}
    correct_set = {(label or "") for label in (correct_labels or []) if isinstance(label, str)}
    missed_set = {(label or "") for label in (missed_labels or []) if isinstance(label, str)}
    extra_set = {(label or "") for label in (extra_labels or []) if isinstance(label, str)}
    target = (target_label or "") if target_label is not None else None

    artists: list[plt.Artist] = []

    for leaf in leaves:
        edgecolor = base_colour
        linewidth = 1.2
        zorder = 1.5

        label_key = leaf.label or ""

        if target is not None and label_key == target:
            edgecolor = COLOURS["reference"]
            linewidth = 2.8
            zorder = 3
        elif label_key in correct_set:
            edgecolor = COLOURS["correct_neighbour"]
            linewidth = 2.4
            zorder = 2.7
        elif label_key in missed_set:
            edgecolor = COLOURS["missed_vertex"]
            linewidth = 2.3
            zorder = 2.6
        elif label_key in extra_set:
            edgecolor = COLOURS["extra_vertex"]
            linewidth = 2.2
            zorder = 2.4
        elif label_key in gt_set:
            edgecolor = COLOURS["partial"]
            linewidth = 2.2
            zorder = 2.5
        elif label_key in model_set:
            edgecolor = COLOURS["answer"]
            linewidth = 2.0
            zorder = 2.2

        rect = plt.Rectangle(
            (leaf.x0, leaf.y0),
            leaf.x1 - leaf.x0,
            leaf.y1 - leaf.y0,
            fill=False,
            edgecolor=edgecolor,
            linewidth=linewidth,
            zorder=zorder,
        )
        rect.set_gid(leaf.label if leaf.label else '""')
        rect.set_picker(True)
        ax.add_patch(rect)
        artists.append(rect)

    return artists


def _voxel_faces(leaf: Leaf) -> list[np.ndarray]:
    vertices = np.array(
        [
            [leaf.x0, leaf.y0, leaf.z0],
            [leaf.x1, leaf.y0, leaf.z0],
            [leaf.x1, leaf.y1, leaf.z0],
            [leaf.x0, leaf.y1, leaf.z0],
            [leaf.x0, leaf.y0, leaf.z1],
            [leaf.x1, leaf.y0, leaf.z1],
            [leaf.x1, leaf.y1, leaf.z1],
            [leaf.x0, leaf.y1, leaf.z1],
        ],
        dtype=float,
    )
    # Create a list of vertices for each face of the voxel
    # The order of vertices determines the orientation of the face
    # The faces are defined clockwise when viewed from the outside
    return [
        vertices[[0, 1, 5, 4]],  # Face parallel to X-axis at X=x0
        vertices[[2, 3, 7, 6]],  # Face parallel to X-axis at X=x1
        vertices[[0, 3, 7, 4]],  # Face parallel to Y-axis at Y=y0
        vertices[[1, 2, 6, 5]],  # Face parallel to Y-axis at Y=y1
        vertices[[0, 1, 2, 3]],  # Face parallel to Z-axis at Z=z0
        vertices[[4, 5, 6, 7]],  # Face parallel to Z-axis at Z=z1
    ]


def _draw_voxels(
    ax,
    leaves: list[Leaf],
    *,
    target_label: str | None,
    ground_truth_labels: Iterable[str] | None,
    model_answer_labels: Iterable[str] | None,
    correct_labels: Iterable[str] | None,
    missed_labels: Iterable[str] | None,
    extra_labels: Iterable[str] | None,
    axis_cycle: tuple[str, ...],
) -> list[Poly3DCollection]:
    gt_set = {(label or "") for label in (ground_truth_labels or []) if isinstance(label, str)}
    model_set = {(label or "") for label in (model_answer_labels or []) if isinstance(label, str)}
    correct_set = {(label or "") for label in (correct_labels or []) if isinstance(label, str)}
    missed_set = {(label or "") for label in (missed_labels or []) if isinstance(label, str)}
    extra_set = {(label or "") for label in (extra_labels or []) if isinstance(label, str)}
    target = (target_label or "") if target_label is not None else None

    artists: list[Poly3DCollection] = []

    for leaf in leaves:
        facecolor = "#E0E0E0"
        edgecolor = "#B0B0B0"
        alpha = 0.12

        label_key = leaf.label or ""

        if target is not None and label_key == target:
            facecolor = COLOURS["reference"]
            edgecolor = COLOURS["reference"]
            alpha = 0.45
        elif label_key in correct_set:
            facecolor = COLOURS["correct_neighbour"]
            edgecolor = COLOURS["correct_neighbour"]
            alpha = 0.4
        elif label_key in missed_set:
            facecolor = COLOURS["missed_vertex"]
            edgecolor = COLOURS["missed_vertex"]
            alpha = 0.4
        elif label_key in extra_set:
            facecolor = COLOURS["extra_vertex"]
            edgecolor = COLOURS["extra_vertex"]
            alpha = 0.35
        elif label_key in gt_set:
            facecolor = COLOURS["partial"]
            edgecolor = COLOURS["partial"]
            alpha = 0.35
        elif label_key in model_set:
            facecolor = COLOURS["answer"]
            edgecolor = COLOURS["answer"]
            alpha = 0.3

        poly = Poly3DCollection(
            _voxel_faces(leaf),
            facecolor=facecolor,
            edgecolor=edgecolor,
            linewidths=1.2,
            alpha=alpha,
        )
        poly.set_gid(leaf.label if leaf.label else '""')
        poly.set_picker(True)
        ax.add_collection3d(poly)
        artists.append(poly)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_zlim(0, 1)
    ax.set_box_aspect((1, 1, 1))
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_facecolor("#F5F5F5")
    ax.grid(False)
    axis_cycle_text = " → ".join(axis_cycle) if axis_cycle else ""
    if axis_cycle_text:
        ax.set_title(
            "Spatial view (3D)\nAxis cycle: " + axis_cycle_text + " (repeating)",
            fontsize=13,
            weight="semibold",
            pad=22,
        )
    else:
        ax.set_title("Spatial view (3D)", fontsize=13, weight="semibold", pad=22)

    return artists


def _enable_leaf_click(fig: plt.Figure, artists: Iterable[plt.Artist]) -> None:
    artists = list(artists)
    if not artists:
        return

    info_text = fig.text(
        0.5,
        0.02,
        "Click any cell to display its label",
        ha="center",
        va="bottom",
        fontsize=10,
        color=COLOURS["annotation"],
        alpha=0.85,
    )

    def _on_pick(event: PickEvent) -> None:
        artist = getattr(event, "artist", None)
        label = artist.get_gid() if hasattr(artist, "get_gid") else None
        if label is None:
            return
        info_text.set_text(f"Selected leaf: {label}")
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect("pick_event", _on_pick)


def _format_label_lines(labels: list[str]) -> list[str]:
    if not labels:
        return []
    lines: list[str] = []
    for label in sorted(labels):
        safe = label if label else '""'
        lines.append(f"• {safe}")
    return lines


def _add_highlight_legend(
    ax: plt.Axes,
    *,
    has_ground_truth: bool,
    has_model_answer: bool,
    has_correct: bool = False,
    has_missed: bool = False,
    has_extra: bool = False,
    location: str = "upper right",
    bbox_anchor: tuple[float, float] | None = None,
    model_label: str | None = None,
) -> None:
    handles = [
        Patch(
            facecolor="white",
            edgecolor=COLOURS["reference"],
            linewidth=2.2,
            label="Target",
        ),
    ]
    if has_correct:
        handles.append(
            Patch(
                facecolor="white",
                edgecolor=COLOURS["correct_neighbour"],
                linewidth=2.2,
                label="Correct neighbour",
            )
        )
    elif has_ground_truth:
        handles.append(
            Patch(
                facecolor="white",
                edgecolor=COLOURS["partial"],
                linewidth=2.2,
                label="Ground truth neighbour",
            )
        )
    if has_missed:
        handles.append(
            Patch(
                facecolor="white",
                edgecolor=COLOURS["missed_vertex"],
                linewidth=2.0,
                label="Missed neighbour",
            )
        )
    if has_extra:
        extra_label = "Extra neighbour"
        handles.append(
            Patch(
                facecolor="white",
                edgecolor=COLOURS["extra_vertex"],
                linewidth=2.0,
                label=extra_label,
            )
        )
    elif has_model_answer and not has_correct:
        neighbour_label = f"{model_label} neighbour" if model_label else "Model answer neighbour"
        handles.append(
            Patch(
                facecolor="white",
                edgecolor=COLOURS["answer"],
                linewidth=2.0,
                label=neighbour_label,
            )
        )
    legend_kwargs = {
        "handles": handles,
        "loc": location,
        "frameon": False,
        "fontsize": 10,
        "handlelength": 1.8,
        "borderaxespad": 0.6,
    }
    if bbox_anchor is not None:
        legend_kwargs["bbox_to_anchor"] = bbox_anchor

    ax.legend(**legend_kwargs)


def _render_text_block(
    ax: plt.Axes,
    *,
    title: str,
    lines: list[str],
    empty_message: str,
    colour: str,
) -> None:
    ax.set_axis_off()
    ax.set_title(title, fontsize=13, weight="semibold", pad=10)

    if not lines:
        text = empty_message
    else:
        text = "\n".join(lines)

    ax.text(
        0.04,
        0.96,
        text,
        ha="left",
        va="top",
        fontsize=11,
        color=colour,
        family="monospace",
        bbox=dict(boxstyle="round,pad=0.45", facecolor="white", edgecolor="#DDDDDD", linewidth=1.2),
        transform=ax.transAxes,
    )


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


def _render_half_subdivision(
    record: Mapping[str, Any],
    answer: Any,
    detail: bool,
    *,
    show: bool | None = None,
) -> plt.Figure:
    datagen_args = record.get("datagen_args", {})
    leaves, dim, axis_cycle, default_target, default_ground = _generate_case(datagen_args)
    model_label = get_answer_label(record, default="Model answer")

    target_label_raw = datagen_args.get("target_leaf")
    target_label = target_label_raw if isinstance(target_label_raw, str) else None
    if target_label is None:
        target_label = default_target

    ground_truth_raw = record.get("ground_truth")
    explicit_ground_truth: list[str] | None = None
    if isinstance(ground_truth_raw, list) and all(isinstance(item, str) for item in ground_truth_raw):
        explicit_ground_truth = ground_truth_raw
    ground_truth_labels = explicit_ground_truth if explicit_ground_truth else default_ground

    fig = plt.figure(figsize=(14, 7))
    fig.suptitle("Half Subdivision Neighbours", fontsize=15, weight="bold", y=0.985)
    fig.patch.set_facecolor("white")
    fig.subplots_adjust(top=0.84)
    target_display = target_label if target_label else '""'
    fig.text(
        0.5,
        0.93,
        f"Target leaf: {target_display}",
        ha="center",
        va="top",
        fontsize=13,
        color=COLOURS["reference"],
        weight="semibold",
    )
    parsed_answer = _coerce_string_list(answer)
    model_answer_labels: list[str] = parsed_answer if isinstance(parsed_answer, list) else []
    has_answer = bool(model_answer_labels)

    highlight_labels_text: list[str] = list(ground_truth_labels)
    highlight_labels_draw: list[str] = [] if has_answer else list(ground_truth_labels)

    gt_set = {label for label in ground_truth_labels if isinstance(label, str)}
    answer_set = {label for label in model_answer_labels if isinstance(label, str)}
    correct_labels = sorted(gt_set & answer_set) if has_answer else []
    missed_labels = sorted(gt_set - answer_set) if has_answer else []
    extra_labels = sorted(answer_set - gt_set) if has_answer else []
    has_errors = bool(missed_labels or extra_labels)
    show_model_answer = detail and has_answer

    model_labels_for_render = model_answer_labels if has_answer else []
    correct_for_render = correct_labels if has_answer else []
    missed_for_render = missed_labels if has_answer else []
    extra_for_render = extra_labels if has_answer else []
    text_rows = 2 if show_model_answer else 1
    gs = fig.add_gridspec(text_rows, 2, width_ratios=[1, 2], hspace=0.35, wspace=0.25)

    # Left column: textual info
    ax_gt = fig.add_subplot(gs[0, 0])
    gt_text_colour = COLOURS["correct_neighbour"] if has_answer else COLOURS["truth"]
    _render_text_block(
        ax_gt,
        title="Ground truth",
        lines=_format_label_lines(highlight_labels_text),
        empty_message="(none)",
        colour=gt_text_colour,
    )

    if show_model_answer:
        ax_ans = fig.add_subplot(gs[1, 0])
        _render_text_block(
            ax_ans,
            title=model_label,
            lines=_format_label_lines(model_answer_labels),
            empty_message="(none)",
            colour=COLOURS["answer"],
        )
    interactive_artists: list[plt.Artist] = []

    if dim == Dimension.D3:
        ax_spatial = fig.add_subplot(gs[:, 1], projection="3d")
        interactive_artists.extend(
            _draw_voxels(
                ax_spatial,
                leaves,
                target_label=target_label,
                ground_truth_labels=highlight_labels_draw,
                model_answer_labels=model_labels_for_render,
                correct_labels=correct_for_render,
                missed_labels=missed_for_render,
                extra_labels=extra_for_render,
                axis_cycle=axis_cycle,
            )
        )
        ax_spatial.view_init(elev=24, azim=-60)
        _add_highlight_legend(
            ax_spatial,
            has_ground_truth=bool(highlight_labels_draw),
            has_model_answer=bool(model_labels_for_render),
            has_correct=bool(correct_for_render),
            has_missed=bool(missed_for_render),
            has_extra=bool(extra_for_render),
            location="upper left",
            bbox_anchor=(1.02, 1.0),
            model_label=model_label,
        )
    else:
        ax_spatial = fig.add_subplot(gs[:, 1])
        axis_cycle_text = " → ".join(axis_cycle) if axis_cycle else ""
        title = "Spatial view (2D)"
        if axis_cycle_text:
            title += "\nAxis cycle: " + axis_cycle_text + " (repeating)"
        ax_spatial.set_title(title, fontsize=13, weight="semibold", pad=22)
        ax_spatial.set_aspect("equal")
        ax_spatial.set_xlim(-0.05, 1.05)
        ax_spatial.set_ylim(-0.05, 1.05)
        ax_spatial.grid(True, linestyle="--", linewidth=0.3, alpha=0.3, color="#CCCCCC")
        ax_spatial.set_facecolor("#FAFAFA")
        interactive_artists.extend(
            _draw_leaves(
                ax_spatial,
                leaves,
                target_label=target_label,
                ground_truth_labels=highlight_labels_draw,
                model_answer_labels=model_labels_for_render,
                correct_labels=correct_for_render,
                missed_labels=missed_for_render,
                extra_labels=extra_for_render,
            )
        )
        _add_highlight_legend(
            ax_spatial,
            has_ground_truth=bool(highlight_labels_draw),
            has_model_answer=bool(model_labels_for_render),
            has_correct=bool(correct_for_render),
            has_missed=bool(missed_for_render),
            has_extra=bool(extra_for_render),
            location="upper left",
            bbox_anchor=(1.02, 1.0),
            model_label=model_label,
        )

    _enable_leaf_click(fig, interactive_artists)

    backend = plt.get_backend().lower()
    non_interactive_markers = {"agg", "cairoagg", "pdf", "pgf", "svg", "template"}
    default_show = not any(marker in backend for marker in non_interactive_markers) and "inline" not in backend
    should_show = show if show is not None else default_show
    if should_show:
        plt.show()

    return fig


register_renderer("half_subdivision_neighbours", _render_half_subdivision)
