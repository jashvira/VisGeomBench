"""Ad-hoc visualisation for unique Delaunay point sets."""

from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Delaunay

from .points import unique_delaunay_points


def plot_delaunay(points: np.ndarray, *, ax: plt.Axes | None = None) -> plt.Axes:
    """Plot points and their Delaunay triangulation."""
    if ax is None:
        _, ax = plt.subplots()

    tri = Delaunay(points)
    ax.triplot(points[:, 0], points[:, 1], tri.simplices, color="tab:blue", lw=0.8)
    ax.scatter(points[:, 0], points[:, 1], color="tab:red", zorder=3)

    for idx, (x, y) in enumerate(points):
        ax.text(x, y, f" {idx}", fontsize=9, va="bottom", ha="left")

    ax.set_aspect("equal", adjustable="box")
    ax.set_title("Unique Delaunay triangulation")
    return ax


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("n", type=int, help="number of points (>=3)")
    parser.add_argument("--seed", type=int, default=None, help="RNG seed")
    parser.add_argument(
        "--box",
        type=float,
        nargs=2,
        default=(0.0, 1.0),
        metavar=("LO", "HI"),
        help="inclusive bounds for both axes",
    )
    parser.add_argument("--eps", type=float, default=1e-12, help="tolerance for degeneracy checks")
    args = parser.parse_args()

    points = unique_delaunay_points(args.n, box=tuple(args.box), seed=args.seed, eps=args.eps)
    ax = plot_delaunay(points)
    ax.set_xlim(args.box)
    ax.set_ylim(args.box)
    plt.show()


if __name__ == "__main__":  # pragma: no cover
    main()
