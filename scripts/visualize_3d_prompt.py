#!/usr/bin/env python3
"""Generate a 3D prompt and visualise voxels, highlighting custom axis cycles."""

from __future__ import annotations

import argparse
import random

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from treelib import Tree

from visual_geometry_bench.datagen.half_subdivision_neighbours import (
    Dimension,
    _build_subdivision,
    _prepare_case,
)


def voxel_faces(x0, y0, z0, x1, y1, z1):
    """Return the 6 faces of a voxel as 3D polygons."""
    vertices = np.array([
        [x0, y0, z0],
        [x1, y0, z0],
        [x1, y1, z0],
        [x0, y1, z0],
        [x0, y0, z1],
        [x1, y0, z1],
        [x1, y1, z1],
        [x0, y1, z1],
    ])
    faces = [
        [vertices[0], vertices[1], vertices[5], vertices[4]],  # x = x0
        [vertices[2], vertices[3], vertices[7], vertices[6]],  # x = x1
        [vertices[0], vertices[3], vertices[7], vertices[4]],  # y = y0
        [vertices[1], vertices[2], vertices[6], vertices[5]],  # y = y1
        [vertices[0], vertices[1], vertices[2], vertices[3]],  # z = z0
        [vertices[4], vertices[5], vertices[6], vertices[7]],  # z = z1
    ]
    return faces


def plot_voxels(target, neighbours, all_leaves, *, axis_cycle_text: str, metadata: dict):
    """Plot target, neighbours, and other voxels in 3D with axis cycle information."""

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    title_lines = ["3D Half-Subdivision Voxels (rotatable)", f"Axis cycle: {axis_cycle_text}"]
    ax.set_title("\n".join(title_lines))

    # Plot all leaves in light gray
    for leaf in all_leaves:
        faces = voxel_faces(leaf.x0, leaf.y0, leaf.z0, leaf.x1, leaf.y1, leaf.z1)
        poly = Poly3DCollection(faces, alpha=0.1, facecolor="lightgray", edgecolor="gray")
        ax.add_collection3d(poly)

    # Plot neighbours in blue
    for leaf in neighbours:
        faces = voxel_faces(leaf.x0, leaf.y0, leaf.z0, leaf.x1, leaf.y1, leaf.z1)
        poly = Poly3DCollection(faces, alpha=0.4, facecolor="cornflowerblue", edgecolor="blue")
        ax.add_collection3d(poly)

    # Plot target in orange
    faces = voxel_faces(target.x0, target.y0, target.z0, target.x1, target.y1, target.z1)
    poly = Poly3DCollection(faces, alpha=0.6, facecolor="orange", edgecolor="darkorange")
    ax.add_collection3d(poly)

    # Set equal aspect and limits
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_zlim(0, 1)
    ax.set_box_aspect([1, 1, 1])

    plt.tight_layout()
    plt.show()


def _parse_axis_cycle(axis_cycle: str | None) -> list[str] | None:
    if not axis_cycle:
        return None
    parsed = [axis.strip() for axis in axis_cycle.split(",") if axis.strip()]
    return parsed or None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Visualise a 3D half-subdivision prompt with configurable axis cycles.",
    )
    parser.add_argument("--max-depth", type=int, default=6, help="Maximum subdivision depth (default: 6)")
    parser.add_argument("--min-depth", type=int, default=3, help="Minimum subdivision depth (default: 3)")
    parser.add_argument("--split-prob", type=float, default=0.7, help="Probability of splitting a node (default: 0.7)")
    parser.add_argument("--seed", type=int, default=7, help="Random seed (default: 7)")
    parser.add_argument(
        "--axis-cycle",
        type=str,
        default=None,
        help="Comma-separated axis cycle, e.g. 'y,z,z,x,y'. Defaults to dimension's cycle.",
    )
    parser.add_argument(
        "--dimension",
        type=str,
        default="3D",
        choices=["3D"],
        help="Spatial dimension (currently 3D only).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    cli_args = parse_args()
    axis_cycle = _parse_axis_cycle(cli_args.axis_cycle)

    datagen_args = {
        "max_depth": cli_args.max_depth,
        "min_depth": cli_args.min_depth,
        "split_prob": cli_args.split_prob,
        "seed": cli_args.seed,
        "dimension": cli_args.dimension,
    }
    if axis_cycle:
        datagen_args["axis_cycle"] = axis_cycle

    tree_text, target, neighbours, runtime = _prepare_case(datagen_args)

    axis_cycle_runtime = runtime.get("axis_cycle", [])
    if not axis_cycle_runtime:
        axis_cycle_runtime = ["x", "y", "z"]
    axis_cycle_text = " → ".join(axis_cycle_runtime) + " (repeating)"

    dim_name = runtime.get("dimension", "3D").upper()
    dim = Dimension.D3 if dim_name == "3D" else Dimension.D2
    if dim != Dimension.D3:
        raise SystemExit("This visualiser currently supports 3D subdivisions only.")

    rng = random.Random(runtime["seed"])
    tree = Tree()
    all_leaves = _build_subdivision(
        tree=tree,
        parent_id=None,
        label="",
        x0=0.0,
        y0=0.0,
        z0=0.0,
        x1=1.0,
        y1=1.0,
        z1=1.0,
        depth=0,
        max_depth=cli_args.max_depth,
        min_depth=cli_args.min_depth,
        split_prob=cli_args.split_prob,
        axis_cycle=tuple(axis_cycle_runtime),
        dim=dim,
        rng=rng,
    )

    print("Generated 3D prompt with configurable axis cycle:")
    print(tree_text)
    print(f"\nTarget leaf: {target.display_label()}")
    print(f"Neighbours ({len(neighbours)}): {[leaf.display_label() for leaf in neighbours]}")
    print(f"Axis cycle: {axis_cycle_text}")

    plot_voxels(target, neighbours, all_leaves, axis_cycle_text=axis_cycle_text, metadata=runtime)
