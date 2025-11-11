#!/usr/bin/env python3
"""Generate topology-enumeration illustrations from the curated config.

Produces:
  • Summary per n (text + example boundary)
  • Per-tuple figure showing corner labels and one plausible interior interface
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt

from visual_geometry_bench.datagen.topology_enumeration import get_solutions

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "topology_enumeration_curated.toml"
OUTPUT_DIR = REPO_ROOT / "data" / "figures" / "topology_enumeration"

CANONICAL_ORDER = ("bottom-left", "bottom-right", "top-right", "top-left")
CORNER_COORDS = {
    "bottom-left": (0.1, 0.1),
    "bottom-right": (0.9, 0.1),
    "top-right": (0.9, 0.9),
    "top-left": (0.1, 0.9),
}

CLASS_COLOURS = {0: "#4C78A8", 1: "#F58518", 2: "#54A24B"}
TEXT_COLOUR = "#111827"


def _load_config(path: Path):
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    configs: list[dict] = []
    for task in data.get("task", []):
        for entry in task.get("datagen_args_grid", []):
            configs.append(entry)
    return configs


def _square_axes(fig: plt.Figure) -> plt.Axes:
    ax = fig.add_subplot(111)
    ax.set_aspect("equal")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor("#FAFBFF")
    ax.plot([0.05, 0.95, 0.95, 0.05, 0.05], [0.05, 0.05, 0.95, 0.95, 0.05], color="#4B5563", linewidth=1.5)
    return ax


def _draw_corners(ax: plt.Axes, corner_order: tuple[str, ...], labels: tuple[int, int, int, int]) -> None:
    for corner, label in zip(corner_order, labels, strict=True):
        x, y = CORNER_COORDS[corner]
        ax.scatter(
            x,
            y,
            s=220,
            color=CLASS_COLOURS.get(label, "#9CA3AF"),
            edgecolors="white",
            linewidths=2,
            zorder=3,
        )
        ax.text(x, y, str(label), ha="center", va="center", fontsize=13, color="white", weight="bold", zorder=4)


def _midpoint(p1, p2):
    return ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)


def _interface_two_classes(corner_order: tuple[str, ...], labels: tuple[int, int, int, int]):
    """Return list of line segments (each segment = sequence of points)."""
    coord_map = {corner: CORNER_COORDS[corner] for corner in corner_order}
    canonical = {corner_order[i]: labels[i] for i in range(4)}
    arr = [canonical[name] for name in CANONICAL_ORDER]

    from collections import Counter

    counts = Counter(arr)
    center = (0.5, 0.5)
    lines: list[list[tuple[float, float]]] = []

    if 3 in counts.values():  # single odd corner
        odd_label = next(label for label, count in counts.items() if count == 1)
        odd_idx = arr.index(odd_label)
        odd_corner = CANONICAL_ORDER[odd_idx]
        opp_corner = CANONICAL_ORDER[(odd_idx + 2) % 4]
        mid = _midpoint(CORNER_COORDS[odd_corner], CORNER_COORDS[opp_corner])
        lines.append([CORNER_COORDS[odd_corner], center, mid])
        return lines

    # two corners each — determine arrangement
    label0 = arr[0]
    idxs = [i for i, val in enumerate(arr) if val == label0]
    pair = frozenset({idxs[0], idxs[1]})
    adj_map = {
        frozenset({0, 1}): "horizontal",
        frozenset({1, 2}): "vertical",
        frozenset({2, 3}): "horizontal",
        frozenset({3, 0}): "vertical",
    }
    if pair in adj_map:
        if adj_map[pair] == "horizontal":
            lines.append([(0.1, 0.5), (0.9, 0.5)])
        else:
            lines.append([(0.5, 0.1), (0.5, 0.9)])
    else:
        lines.append([(0.1, 0.1), (0.9, 0.9)])
        lines.append([(0.9, 0.1), (0.1, 0.9)])
    return lines


def _interface_three_classes(corner_order: tuple[str, ...], labels: tuple[int, int, int, int]):
    anchors: dict[int, list[tuple[float, float]]] = {}
    for corner, label in zip(corner_order, labels, strict=True):
        anchors.setdefault(label, []).append(CORNER_COORDS[corner])
    lines: list[list[tuple[float, float]]] = []
    center = (0.5, 0.5)
    for pts in anchors.values():
        avg = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
        lines.append([center, avg])
    return lines


def _render_case(n_classes: int, corner_order: tuple[str, ...], labels: tuple[int, int, int, int], path: Path) -> None:
    fig = plt.figure(figsize=(4.6, 4.6))
    ax = _square_axes(fig)
    _draw_corners(ax, corner_order, labels)
    if n_classes == 2:
        lines = _interface_two_classes(corner_order, labels)
    else:
        lines = _interface_three_classes(corner_order, labels)
    for line in lines:
        xs, ys = zip(*line)
        ax.plot(xs, ys, color=TEXT_COLOUR, linewidth=2.5, alpha=0.9)
    ax.set_title(f"{corner_order} · {labels}", fontsize=10, pad=10)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)
    print(f"[case] {path}")


def _render_summary(n_classes: int, configs: list[tuple[tuple[str, ...], list[tuple[int, int, int, int]]]], path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": (1.4, 1)})
    fig.suptitle(f"Topology Enumeration · n = {n_classes}", fontsize=16, weight="bold")
    text_ax, sq_ax = axes
    text_ax.axis("off")
    sections: list[str] = []
    for corner_order, tuples in configs:
        header = f"Corner order: {corner_order}\n" + "\n".join(f"  {t}" for t in tuples)
        sections.append(header)
    text_ax.text(0, 1, "\n\n".join(sections), ha="left", va="top", fontsize=10.5, family="monospace", color=TEXT_COLOUR)
    _draw_corners(sq_ax, CANONICAL_ORDER, configs[0][1][0] if configs and configs[0][1] else (0, 1, 0, 1))
    if n_classes == 2:
        for line in _interface_two_classes(CANONICAL_ORDER, configs[0][1][0]):
            xs, ys = zip(*line)
            sq_ax.plot(xs, ys, color=TEXT_COLOUR, linewidth=2.3)
    else:
        for line in _interface_three_classes(CANONICAL_ORDER, configs[0][1][0]):
            xs, ys = zip(*line)
            sq_ax.plot(xs, ys, color=TEXT_COLOUR, linewidth=2.3)
    sq_ax.set_title("Example boundary", fontsize=11)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"[summary] {path}")


def slugify(obj: Iterable[str]) -> str:
    return "_".join(part.lower().replace(" ", "-") for part in obj)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument(
        "--mode",
        choices=("all", "summary", "cases"),
        default="all",
        help="Which figures to produce",
    )
    args = parser.parse_args()

    configs = _load_config(args.config)
    grouped: dict[int, list[tuple[tuple[str, ...], list[tuple[int, int, int, int]]]]] = {}
    for cfg in configs:
        corner_order = tuple(cfg["corner_order"])
        n_classes = int(cfg["n_classes"])
        tuples = get_solutions(n_classes, corner_order)
        grouped.setdefault(n_classes, []).append((corner_order, tuples))

    for n_classes, entries in grouped.items():
        if args.mode in ("all", "summary"):
            summary_path = args.output_dir / f"topology_enumeration_n{n_classes}_summary.png"
            _render_summary(n_classes, entries, summary_path)
        if args.mode in ("all", "cases"):
            for corner_order, tuples in entries:
                order_slug = slugify(corner_order)
                for idx, tup in enumerate(tuples, start=1):
                    fname = f"n{n_classes}_{order_slug}_case{idx:02d}.png"
                    out_path = args.output_dir / "cases" / fname
                    _render_case(n_classes, corner_order, tup, out_path)


if __name__ == "__main__":
    main()
