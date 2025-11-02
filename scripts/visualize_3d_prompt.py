#!/usr/bin/env python3
"""Generate a 3D prompt and visualize the voxels with matplotlib (rotatable)."""

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import Axes3D

from visual_geometry_bench.datagen.half_subdivision_neighbours import _prepare_case, Dimension


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


def plot_voxels(target, neighbours, all_leaves):
    """Plot target, neighbours, and other voxels in 3D."""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("3D Half-Subdivision Voxels (rotatable)")

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


if __name__ == "__main__":
    args = {
        "max_depth": 6,
        "min_depth": 3,
        "split_prob": 0.7,
        "seed": 7,
        "dimension": "3D",
    }
    tree_text, target, neighbours, runtime = _prepare_case(args)
    # Rebuild all leaves for visualization
    rng = __import__("random").Random(args["seed"])
    from visual_geometry_bench.datagen.half_subdivision_neighbours import _build_subdivision, Tree
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
        max_depth=args["max_depth"],
        min_depth=args["min_depth"],
        split_prob=args["split_prob"],
        start_axis="x",
        dim=Dimension.D3,
        rng=rng,
    )
    print("Generated 3D prompt (target highlighted orange, neighbours blue):")
    print(tree_text)
    print(f"\nTarget leaf: {target.display_label()}")
    print(f"Neighbours ({len(neighbours)}): {[leaf.display_label() for leaf in neighbours]}")
    plot_voxels(target, neighbours, all_leaves)
