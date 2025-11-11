#!/usr/bin/env python3
"""Render the seven canonical n=2 topology-enumeration cases in one figure."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from visual_geometry_bench.datagen.topology_enumeration import get_solutions
from visual_geometry_bench.datagen.utils import CANONICAL_CORNER_ORDER

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "data" / "figures" / "topology_enumeration" / "n2_all_cases.png"

CORNER_COORDS = {
    "bottom-left": (0.1, 0.1),
    "bottom-right": (0.9, 0.1),
    "top-right": (0.9, 0.9),
    "top-left": (0.1, 0.9),
}
EDGE_COLOR = "#111827"
POINT_COLOR = "#2563EB"


def _draw_case(ax: plt.Axes, labels: tuple[int, int, int, int]) -> None:
    ax.set_aspect("equal")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.plot([0.05, 0.95, 0.95, 0.05, 0.05], [0.05, 0.05, 0.95, 0.95, 0.05], color=EDGE_COLOR, linewidth=1.5)

    for corner, label in zip(CANONICAL_CORNER_ORDER, labels, strict=True):
        x, y = CORNER_COORDS[corner]
        ax.scatter(x, y, s=220, color=POINT_COLOR, edgecolors="white", linewidths=2)
        ax.text(x, y, str(label), ha="center", va="center", color="white", fontsize=13, weight="bold")

    differing_edges = []
    for idx in range(4):
        if labels[idx] != labels[(idx + 1) % 4]:
            differing_edges.append(idx)

    midpoints = [
        (0.5, 0.05),  # bottom
        (0.95, 0.5),  # right
        (0.5, 0.95),  # top
        (0.05, 0.5),  # left
    ]

    if len(differing_edges) == 2:
        i, j = differing_edges
        xs = [midpoints[i][0], midpoints[j][0]]
        ys = [midpoints[i][1], midpoints[j][1]]
        ax.plot(xs, ys, color=EDGE_COLOR, linewidth=2.3)
    elif len(differing_edges) == 4:
        ax.plot([0.1, 0.9], [0.1, 0.9], color=EDGE_COLOR, linewidth=2.0)
        ax.plot([0.1, 0.9], [0.9, 0.1], color=EDGE_COLOR, linewidth=2.0)
    else:
        pass


def render(output: Path) -> None:
    cases = get_solutions(2, CANONICAL_CORNER_ORDER)
    fig, axes = plt.subplots(2, 4, figsize=(12, 6))
    axes = axes.flatten()
    for idx, labels in enumerate(cases):
        _draw_case(axes[idx], labels)
        axes[idx].set_title(f"Case {idx + 1}: {labels}", fontsize=11, pad=8)
    for idx in range(len(cases), len(axes)):
        axes[idx].axis("off")
    fig.suptitle("Topology Enumeration · n = 2 cases", fontsize=18, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220)
    plt.close(fig)
    print(f"Wrote {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    render(args.output)


if __name__ == "__main__":
    main()
