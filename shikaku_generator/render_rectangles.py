#!/usr/bin/env python3
"""Render Rectangles puzzle solutions to image files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402


def normalise_name(raw: str) -> str:
    return raw.replace("/", "_").replace(":", "-").replace(" ", "_")


def render_puzzle(record: dict, output_path: Path) -> None:
    width = record["width"]
    height = record["height"]
    numbers: List[List[int]] = record["numbers"]
    rectangles: List[dict] = record.get("solution_rectangles", [])

    cell_size = 0.8
    margin = 0.5
    fig_w = width * cell_size + 2 * margin
    fig_h = height * cell_size + 2 * margin
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    ax.set_xlim(-margin, width + margin)
    ax.set_ylim(height + margin, -margin)
    ax.set_aspect("equal")
    ax.axis("off")

    if rectangles:
        cmap = plt.get_cmap("tab20", max(len(rectangles), 1))
        for rect in rectangles:
            colour = cmap(rect["id"] % cmap.N)
            ax.add_patch(
                Rectangle(
                    (rect["left"], rect["top"]),
                    rect["width"],
                    rect["height"],
                    facecolor=colour,
                    edgecolor="black",
                    linewidth=2.5,
                    alpha=0.25,
                )
            )

    for y in range(height + 1):
        ax.plot([0, width], [y, y], color="#999", linewidth=0.5, solid_capstyle="round")
    for x in range(width + 1):
        ax.plot([x, x], [0, height], color="#999", linewidth=0.5, solid_capstyle="round")

    for r in range(height):
        for c in range(width):
            val = numbers[r][c]
            if val:
                ax.text(
                    c + 0.5,
                    r + 0.5,
                    str(val),
                    ha="center",
                    va="center",
                    fontsize=max(10, 200 // max(width, height)),
                    color="black",
                    fontweight="bold",
                    family="monospace",
                )

    title_text = f"{width}×{height}  [{len(rectangles)} rects]"
    ax.text(
        width / 2,
        -0.25,
        title_text,
        ha="center",
        va="top",
        fontsize=9,
        color="#333",
    )

    fig.savefig(output_path, dpi=150, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "json_path",
        nargs="?",
        default="shikaku_generator/generated/rectangles.json",
        help="Path to rectangles.json dataset",
    )
    parser.add_argument(
        "--output-dir",
        default="shikaku_generator/generated/solutions",
        help="Directory to place rendered images",
    )
    args = parser.parse_args()

    json_path = Path(args.json_path).resolve()
    if not json_path.exists():
        raise SystemExit(f"Dataset not found: {json_path}")

    records = json.loads(json_path.read_text())
    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    for idx, record in enumerate(records):
        stem = f"{idx:03d}_{normalise_name(record['id'])}"
        output_path = out_dir / f"{stem}.png"
        render_puzzle(record, output_path)

    print(f"Rendered {len(records)} puzzles into {out_dir}")


if __name__ == "__main__":
    main()
