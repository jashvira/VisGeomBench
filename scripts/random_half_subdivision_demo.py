from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from typing import Iterator, Optional

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle
from treelib import Tree


@dataclass(slots=True, eq=False)
class Node:
    x0: float
    y0: float
    x1: float
    y1: float
    depth: int
    label: str
    axis: Optional[str]
    split: Optional[float]
    child0: Optional["Node"] = None
    child1: Optional["Node"] = None
    parent: Optional["Node"] = None

    @property
    def is_leaf(self) -> bool:
        return self.child0 is None and self.child1 is None


def _axis_for_depth(depth: int, start_axis: str) -> str:
    if start_axis not in {"x", "y"}:
        raise ValueError("start_axis must be 'x' or 'y'")
    if start_axis == "x":
        return "x" if depth % 2 == 0 else "y"
    return "y" if depth % 2 == 0 else "x"


def build_half_subdivision(
    *,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    depth: int,
    max_depth: int,
    label: str,
    start_axis: str,
    rng: random.Random,
    p_split: float,
    min_depth: int = 0,
) -> Node:
    if depth == max_depth or (depth >= min_depth and rng.random() >= p_split):
        return Node(x0, y0, x1, y1, depth, label, None, None)

    axis = _axis_for_depth(depth, start_axis)
    if axis == "x":
        split = (x0 + x1) * 0.5
        child0 = build_half_subdivision(
            x0=x0,
            y0=y0,
            x1=split,
            y1=y1,
            depth=depth + 1,
            max_depth=max_depth,
            label=label + "0",
            start_axis=start_axis,
            rng=rng,
            p_split=p_split,
            min_depth=min_depth,
        )
        child1 = build_half_subdivision(
            x0=split,
            y0=y0,
            x1=x1,
            y1=y1,
            depth=depth + 1,
            max_depth=max_depth,
            label=label + "1",
            start_axis=start_axis,
            rng=rng,
            p_split=p_split,
            min_depth=min_depth,
        )
    else:
        split = (y0 + y1) * 0.5
        child0 = build_half_subdivision(
            x0=x0,
            y0=split,
            x1=x1,
            y1=y1,
            depth=depth + 1,
            max_depth=max_depth,
            label=label + "0",
            start_axis=start_axis,
            rng=rng,
            p_split=p_split,
            min_depth=min_depth,
        )
        child1 = build_half_subdivision(
            x0=x0,
            y0=y0,
            x1=x1,
            y1=split,
            depth=depth + 1,
            max_depth=max_depth,
            label=label + "1",
            start_axis=start_axis,
            rng=rng,
            p_split=p_split,
            min_depth=min_depth,
        )
    node = Node(
        x0,
        y0,
        x1,
        y1,
        depth,
        label,
        axis,
        split,
        child0,
        child1,
    )
    if child0 is not None:
        child0.parent = node
    if child1 is not None:
        child1.parent = node
    return node


def iter_leaves(node: Node) -> Iterator[Node]:
    if node.is_leaf:
        yield node
        return
    assert node.child0 is not None and node.child1 is not None
    yield from iter_leaves(node.child0)
    yield from iter_leaves(node.child1)


def _node_tag(node: Node) -> str:
    return node.label if node.label else '""'


def _sibling_across_boundary(node: Node, side: str) -> Optional[Node]:
    current = node
    while current.parent is not None:
        parent = current.parent
        if parent.axis == "x":
            if side == "RIGHT" and parent.child0 is current:
                return parent.child1
            if side == "LEFT" and parent.child1 is current:
                return parent.child0
        elif parent.axis == "y":
            if side == "TOP" and parent.child0 is current:
                return parent.child1
            if side == "BOTTOM" and parent.child1 is current:
                return parent.child0
        current = parent
    return None


def _collect_touching(
    node: Node,
    side: str,
    slab: tuple[float, float],
    acc: list[Node],
    seen: set[int],
) -> None:
    if slab[0] >= slab[1]:
        return
    if node.is_leaf:
        node_id = id(node)
        if node_id not in seen:
            seen.add(node_id)
            acc.append(node)
        return

    if side in {"LEFT", "RIGHT"}:
        if node.axis == "x":
            child = node.child0 if side == "RIGHT" else node.child1
            assert child is not None
            _collect_touching(child, side, slab, acc, seen)
        else:
            for child in (node.child0, node.child1):
                if child is None:
                    continue
                child_slab = (
                    max(slab[0], child.y0),
                    min(slab[1], child.y1),
                )
                _collect_touching(child, side, child_slab, acc, seen)
    else:  # TOP or BOTTOM
        if node.axis == "y":
            child = node.child0 if side == "TOP" else node.child1
            assert child is not None
            _collect_touching(child, side, slab, acc, seen)
        else:
            for child in (node.child0, node.child1):
                if child is None:
                    continue
                child_slab = (
                    max(slab[0], child.x0),
                    min(slab[1], child.x1),
                )
                _collect_touching(child, side, child_slab, acc, seen)


def neighbouring_leaves(target: Node) -> list[Node]:
    neighbours: list[Node] = []
    seen: set[int] = set()
    for side in ("LEFT", "RIGHT", "BOTTOM", "TOP"):
        sibling = _sibling_across_boundary(target, side)
        if sibling is None:
            continue
        slab = (
            (target.y0, target.y1)
            if side in {"LEFT", "RIGHT"}
            else (target.x0, target.x1)
        )
        _collect_touching(sibling, side, slab, neighbours, seen)
    return neighbours


def to_treelib(root: Node) -> Tree:
    tree = Tree()
    tree.create_node(tag=_node_tag(root), identifier=id(root), data=root)

    def _recurse(current: Node) -> None:
        for child in (current.child0, current.child1):
            if child is None:
                continue
            tree.create_node(tag=_node_tag(child), identifier=id(child), parent=id(current), data=child)
            _recurse(child)

    _recurse(root)
    return tree


def plot_subdivision(
    root: Node,
    ax: Axes,
    *,
    target: Optional[Node] = None,
    neighbours: Optional[list[Node]] = None,
) -> None:
    leaves = list(iter_leaves(root))
    neighbour_ids = {id(n) for n in neighbours} if neighbours else set()
    target_id = id(target) if target is not None else None
    for idx, leaf in enumerate(leaves):
        if target_id is not None and id(leaf) == target_id:
            facecolor = "#ffcccc"
        elif id(leaf) in neighbour_ids:
            facecolor = "#ccffcc"
        else:
            facecolor = "none"
        rect = Rectangle(
            (leaf.x0, leaf.y0),
            leaf.x1 - leaf.x0,
            leaf.y1 - leaf.y0,
            facecolor=facecolor,
            edgecolor="black",
            linewidth=1.2,
        )
        ax.add_patch(rect)
        ax.text(
            (leaf.x0 + leaf.x1) / 2,
            (leaf.y0 + leaf.y1) / 2,
            leaf.label or '""',
            ha="center",
            va="center",
            fontsize=8,
        )

    ax.set_aspect("equal", "box")
    ax.set_xlim(root.x0, root.x1)
    ax.set_ylim(root.y0, root.y1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Alternating half subdivision (leaf labels as 0/1 paths)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Visualise an alternating half-subdivision up to depth 5."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed for the random generator to reproduce a specific subdivision.",
    )
    parser.add_argument(
        "--start-axis",
        choices=["x", "y"],
        default="x",
        help="Axis used for the root split; axes alternate from there (default: x).",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=5,
        help="Maximum depth of the tree (default: 5).",
    )
    parser.add_argument(
        "--split-prob",
        type=float,
        default=0.7,
        help="Probability of splitting a node before reaching max depth (default: 0.7).",
    )
    parser.add_argument(
        "--min-depth",
        type=int,
        default=0,
        help="Force splitting until this depth (default: 0).",
    )
    parser.add_argument(
        "--no-tree",
        action="store_true",
        help="Skip printing the textual tree with treelib.",
    )
    parser.add_argument(
        "--target-label",
        type=str,
        default=None,
        help="Leaf label to inspect for neighbours (default: first leaf encountered).",
    )
    args = parser.parse_args()

    rng = random.Random(args.seed)
    root = build_half_subdivision(
        x0=0.0,
        y0=0.0,
        x1=1.0,
        y1=1.0,
        depth=0,
        max_depth=args.max_depth,
        label="",
        start_axis=args.start_axis,
        rng=rng,
        p_split=args.split_prob,
        min_depth=args.min_depth,
    )

    if not args.no_tree:
        treelib_tree = to_treelib(root)
        treelib_tree.show()

    leaves = list(iter_leaves(root))
    if not leaves:
        raise RuntimeError("Subdivision produced no leaves")

    meta_notice: Optional[str] = None
    if args.target_label is None:
        target_leaf = leaves[0]
    else:
        matching = [leaf for leaf in leaves if leaf.label == args.target_label]
        if matching:
            target_leaf = matching[0]
        else:
            prefix_matches = [leaf for leaf in leaves if leaf.label.startswith(args.target_label)]
            if prefix_matches:
                target_leaf = prefix_matches[0]
                meta_notice = (
                    f"Label '{args.target_label}' is an internal node; "
                    f"using descendant leaf '{target_leaf.label}'."
                )
            else:
                target_leaf = leaves[0]
                meta_notice = (
                    f"Label '{args.target_label}' not found; defaulting to leaf '{target_leaf.label}'."
                )

    neighbours = neighbouring_leaves(target_leaf)
    label_fmt = target_leaf.label if target_leaf.label else '""'
    neighbour_labels = [n.label if n.label else '""' for n in neighbours]
    if meta_notice is not None:
        print(meta_notice)
    print(f"Target leaf {label_fmt} spans x=[{target_leaf.x0:.3f}, {target_leaf.x1:.3f}], y=[{target_leaf.y0:.3f}, {target_leaf.y1:.3f}]")
    if neighbour_labels:
        print("Neighbouring leaves:", ", ".join(neighbour_labels))
    else:
        print("No neighbouring leaves (touches boundary on all sides).")

    fig, ax = plt.subplots(figsize=(6, 6))
    plot_subdivision(root, ax, target=target_leaf, neighbours=neighbours)
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
