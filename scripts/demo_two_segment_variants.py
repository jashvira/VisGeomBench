from __future__ import annotations

import math
from typing import Mapping, Tuple

import matplotlib.pyplot as plt

from visual_geometry_bench.verification.two_segments import classify_segments

Point = Tuple[float, float]
Segment = Tuple[Point, Point]


EXAMPLES: list[tuple[str, tuple[Segment, Segment]]] = [
    (
        "diagonals",
        (
            ((0.0, 0.0), (1.0, 1.0)),
            ((0.0, 1.0), (1.0, 0.0)),
        ),
    ),
    (
        "tri_quad_mix",
        (
            ((0.0, 0.0), (0.25, 1.0)),
            ((0.0, 1.0), (1.0, 0.0)),
        ),
    ),
    (
        "two_tri_two_quads",
        (
            ((0.0, 0.0), (0.25, 1.0)),
            ((0.0, 0.25), (1.0, 0.0)),
        ),
    ),
    (
        "triangles_plus_pentagon",
        (
            ((0.0, 0.0), (0.25, 1.0)),
            ((0.25, 0.0), (1.0, 0.25)),
        ),
    ),
    (
        "triangle_quad_pentagon",
        (
            ((0.0, 0.25), (0.25, 0.0)),
            ((0.0, 0.5), (0.5, 0.0)),
        ),
    ),
    (
        "hexagon_mix",
        (
            ((0.0, 0.25), (0.25, 1.0)),
            ((0.0, 0.5), (0.5, 1.0)),
        ),
    ),
    (
        "quad_grid",
        (
            ((0.0, 0.25), (1.0, 0.25)),
            ((0.25, 0.0), (0.25, 1.0)),
        ),
    ),
    (
        "pentagon_pair",
        (
            ((0.0, 0.25), (1.0, 0.5)),
            ((0.0, 0.5), (1.0, 0.25)),
        ),
    ),
]


_SHAPE_ORDER = ("triangle", "quadrilateral", "pentagon", "hexagon")


def _format_counts(counts: Mapping[str, int]) -> str:
    lines = [
        f"{shape}: {counts[shape]}"
        for shape in _SHAPE_ORDER
        if shape in counts
    ]
    return "\n".join(lines)


def draw_example(ax, title: str, segments: tuple[Segment, Segment]) -> None:
    ax.set_title(title)

    frame_x = [0, 1, 1, 0, 0]
    frame_y = [0, 0, 1, 1, 0]
    ax.plot(frame_x, frame_y, color="black", linewidth=1.5)

    for (x0, y0), (x1, y1) in segments:
        ax.plot([x0, x1], [y0, y1], color="red", linewidth=2)

    counts = classify_segments(segments)
    label = _format_counts(counts)
    ax.text(
        0.5,
        0.5,
        label,
        ha="center",
        va="center",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.75),
    )

    ax.set_aspect("equal", "box")
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.axis("off")

    print(f"{title}: {counts}")


def main() -> None:
    cols = 4
    rows = math.ceil(len(EXAMPLES) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(3 * cols, 3 * rows))

    axes_flat = list(axes.flat) if hasattr(axes, "flat") else [axes]

    for ax, (title, segments) in zip(axes_flat, EXAMPLES):
        draw_example(ax, title, segments)

    for ax in axes_flat[len(EXAMPLES) :]:
        ax.axis("off")

    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
