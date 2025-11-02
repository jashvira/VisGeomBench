from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Sequence

from treelib import Tree

from visual_geometry_bench.datagen.utils import compute_content_hash

__all__ = [
    "make_prompt",
    "get_solutions",
    "generate_dataset_record",
]

_EPS = 1e-9


class Dimension(Enum):
    D2 = 2
    D3 = 3


@dataclass(frozen=True, slots=True)
class Leaf:
    label: str
    x0: float
    y0: float
    x1: float
    y1: float
    z0: float = 0.0
    z1: float = 1.0

    def display_label(self) -> str:
        return self.label if self.label else '""'


def _axis_for_depth(depth: int, start_axis: str, dim: Dimension) -> str:
    if start_axis not in {"x", "y", "z"}:
        raise ValueError("start_axis must be 'x', 'y', or 'z'")
    if dim == Dimension.D2:
        return "x" if depth % 2 == 0 else "y"
    if dim == Dimension.D3:
        return ["x", "y", "z"][depth % 3]
    raise ValueError("Unsupported dimension")


def _build_subdivision(
    *,
    tree: Tree,
    parent_id: str | None,
    label: str,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    z0: float = 0.0,
    z1: float = 1.0,
    depth: int,
    max_depth: int,
    min_depth: int,
    split_prob: float,
    start_axis: str,
    dim: Dimension,
    rng: random.Random,
) -> list[Leaf]:
    node_id = label if label else "__root__"
    if tree.root is None:
        tree.create_node(tag=Leaf(label, x0, y0, x1, y1, z0, z1).display_label(), identifier=node_id)
    else:
        tree.create_node(tag=Leaf(label, x0, y0, x1, y1, z0, z1).display_label(), identifier=node_id, parent=parent_id)

    if depth == max_depth or (depth >= min_depth and rng.random() >= split_prob):
        return [Leaf(label, x0, y0, x1, y1, z0, z1)]

    axis = _axis_for_depth(depth, start_axis, dim)
    leaves: list[Leaf] = []

    if axis == "x":
        mid = 0.5 * (x0 + x1)
        leaves.extend(
            _build_subdivision(
                tree=tree,
                parent_id=node_id,
                label=label + "0",
                x0=x0,
                y0=y0,
                x1=mid,
                y1=y1,
                z0=z0,
                z1=z1,
                depth=depth + 1,
                max_depth=max_depth,
                min_depth=min_depth,
                split_prob=split_prob,
                start_axis=start_axis,
                dim=dim,
                rng=rng,
            )
        )
        leaves.extend(
            _build_subdivision(
                tree=tree,
                parent_id=node_id,
                label=label + "1",
                x0=mid,
                y0=y0,
                x1=x1,
                y1=y1,
                z0=z0,
                z1=z1,
                depth=depth + 1,
                max_depth=max_depth,
                min_depth=min_depth,
                split_prob=split_prob,
                start_axis=start_axis,
                dim=dim,
                rng=rng,
            )
        )
    elif axis == "y":
        mid = 0.5 * (y0 + y1)
        leaves.extend(
            _build_subdivision(
                tree=tree,
                parent_id=node_id,
                label=label + "0",
                x0=x0,
                y0=mid,
                x1=x1,
                y1=y1,
                z0=z0,
                z1=z1,
                depth=depth + 1,
                max_depth=max_depth,
                min_depth=min_depth,
                split_prob=split_prob,
                start_axis=start_axis,
                dim=dim,
                rng=rng,
            )
        )
        leaves.extend(
            _build_subdivision(
                tree=tree,
                parent_id=node_id,
                label=label + "1",
                x0=x0,
                y0=y0,
                x1=x1,
                y1=mid,
                z0=z0,
                z1=z1,
                depth=depth + 1,
                max_depth=max_depth,
                min_depth=min_depth,
                split_prob=split_prob,
                start_axis=start_axis,
                dim=dim,
                rng=rng,
            )
        )
    else:  # axis == "z" (3D only)
        mid = 0.5 * (z0 + z1)
        leaves.extend(
            _build_subdivision(
                tree=tree,
                parent_id=node_id,
                label=label + "0",
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
                z0=z0,
                z1=mid,
                depth=depth + 1,
                max_depth=max_depth,
                min_depth=min_depth,
                split_prob=split_prob,
                start_axis=start_axis,
                dim=dim,
                rng=rng,
            )
        )
        leaves.extend(
            _build_subdivision(
                tree=tree,
                parent_id=node_id,
                label=label + "1",
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
                z0=mid,
                z1=z1,
                depth=depth + 1,
                max_depth=max_depth,
                min_depth=min_depth,
                split_prob=split_prob,
                start_axis=start_axis,
                dim=dim,
                rng=rng,
            )
        )

    return leaves


def _overlap(lo1: float, hi1: float, lo2: float, hi2: float) -> bool:
    return max(lo1, lo2) < min(hi1, hi2) - _EPS


def _are_adjacent(a: Leaf, b: Leaf, dim: Dimension) -> bool:
    if dim == Dimension.D2:
        if abs(a.x1 - b.x0) < _EPS or abs(a.x0 - b.x1) < _EPS:
            return _overlap(a.y0, a.y1, b.y0, b.y1)
        if abs(a.y1 - b.y0) < _EPS or abs(a.y0 - b.y1) < _EPS:
            return _overlap(a.x0, a.x1, b.x0, b.x1)
        return False
    elif dim == Dimension.D3:
        # 6-connectivity (face adjacency)
        if abs(a.x1 - b.x0) < _EPS or abs(a.x0 - b.x1) < _EPS:
            return _overlap(a.y0, a.y1, b.y0, b.y1) and _overlap(a.z0, a.z1, b.z0, b.z1)
        if abs(a.y1 - b.y0) < _EPS or abs(a.y0 - b.y1) < _EPS:
            return _overlap(a.x0, a.x1, b.x0, b.x1) and _overlap(a.z0, a.z1, b.z0, b.z1)
        if abs(a.z1 - b.z0) < _EPS or abs(a.z0 - b.z1) < _EPS:
            return _overlap(a.x0, a.x1, b.x0, b.x1) and _overlap(a.y0, a.y1, b.y0, b.y1)
        return False
    else:
        raise ValueError("Unsupported dimension")


def _normalise_label(label: str | None) -> str | None:
    if label is None:
        return None
    label = label.strip()
    return "" if label in {"", '""'} else label


def _prepare_case(datagen_args: dict) -> tuple[str, Leaf, list[Leaf], dict]:
    if not isinstance(datagen_args, dict):
        raise TypeError("datagen_args must be a dictionary")

    try:
        max_depth = int(datagen_args["max_depth"])
        seed = int(datagen_args["seed"])
        split_prob = float(datagen_args["split_prob"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("datagen_args must include max_depth:int, seed:int, split_prob:float") from exc

    min_depth = int(datagen_args.get("min_depth", 0))
    start_axis = str(datagen_args.get("start_axis", "x"))
    target_label = _normalise_label(datagen_args.get("target_label"))
    dim_name = str(datagen_args.get("dimension", "2D")).upper()
    dim = Dimension.D2 if dim_name == "2D" else Dimension.D3 if dim_name == "3D" else Dimension[dim_name]

    if max_depth < 0 or min_depth < 0:
        raise ValueError("depth values must be non-negative")
    if split_prob < 0.0 or split_prob > 1.0:
        raise ValueError("split_prob must be within [0, 1]")
    if min_depth > max_depth:
        raise ValueError("min_depth cannot exceed max_depth")
    if dim == Dimension.D3 and start_axis not in {"x", "y", "z"}:
        raise ValueError("start_axis must be 'x', 'y', or 'z' for 3D")

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
        start_axis=start_axis,
        dim=dim,
        rng=rng,
        **bounds,
    )

    if not leaves:
        raise RuntimeError("subdivision produced no leaves")

    leaves_by_label = {leaf.label: leaf for leaf in leaves}

    if target_label is None:
        target = rng.choice(leaves)
    else:
        try:
            target = leaves_by_label[target_label]
        except KeyError as exc:
            raise ValueError(f"target_label '{target_label}' is not a leaf") from exc

    neighbours = sorted(
        (leaf for leaf in leaves if leaf is not target and _are_adjacent(leaf, target, dim)),
        key=lambda leaf: leaf.label,
    )

    treelib_text = tree.show(stdout=False)

    runtime_info = {
        "max_depth": max_depth,
        "min_depth": min_depth,
        "split_prob": split_prob,
        "seed": seed,
        "start_axis": start_axis,
        "dimension": dim_name,
        **({"target_label": target.display_label()} if target_label is not None else {}),
    }

    return treelib_text, target, neighbours, runtime_info


_2D_PROMPT_TEMPLATE = """You are given a binary tree describing an alternating axis-aligned half subdivision of the unit square.

Each node splits its parent cell into two children by bisecting along either the x-axis or y-axis.

Here is the subdivision tree:

```
{tree_text}
```

Target leaf: {target_label}

Before presenting the final list, begin your response with <thinking>...</thinking> containing your full chain of thought or reasoning for your answer.
List every leaf that shares a boundary segment with the target. Return the labels as a comma-separated list of strings (quotes optional)."""


_3D_PROMPT_TEMPLATE = """You are given a binary tree describing an alternating axis-aligned half subdivision of the unit cube.

Each node splits its parent cell into two children by bisecting along the x, y, or z axis in cyclic order.
The axis cycle follows x → y → z repeatedly as you go down the tree.

Here is the subdivision tree:

```
{tree_text}
```

Target leaf: {target_label}

Before presenting the final list, begin your response with <thinking>...</thinking> containing your full chain of thought or reasoning for your answer.
List every leaf that shares a face with the target voxel. Return the labels as a comma-separated list of strings (quotes optional)."""


def _format_prompt(tree_text: str, target: Leaf, dim: Dimension) -> str:
    template = _3D_PROMPT_TEMPLATE if dim == Dimension.D3 else _2D_PROMPT_TEMPLATE
    return template.format(tree_text=tree_text.rstrip(), target_label=target.display_label())


def _canonical_labels(leaves: Iterable[Leaf]) -> list[str]:
    return [leaf.display_label() for leaf in leaves]


def make_prompt(datagen_args: dict) -> str:
    tree_text, target, _, runtime = _prepare_case(datagen_args)
    dim_name = runtime["dimension"]
    dim = Dimension.D2 if dim_name == "2D" else Dimension.D3 if dim_name == "3D" else Dimension[dim_name]
    return _format_prompt(tree_text, target, dim)


def get_solutions(datagen_args: dict) -> list[str]:
    tree_text, target, neighbours, runtime = _prepare_case(datagen_args)
    _ = tree_text, target, runtime  # unused beyond deterministic generation
    return _canonical_labels(neighbours)


def generate_dataset_record(
    datagen_args: dict,
    *,
    record_id: str | None = None,
    tags: Sequence[str] | None = None,
    difficulty: str | None = None,
    requires_visual: bool = False,
) -> dict:
    tree_text, target, neighbours, runtime_info = _prepare_case(datagen_args)
    dim_name = runtime_info["dimension"]
    dim = Dimension.D2 if dim_name == "2D" else Dimension.D3 if dim_name == "3D" else Dimension[dim_name]

    prompt = _format_prompt(tree_text, target, dim)
    ground_truth = _canonical_labels(neighbours)

    metadata = {
        "problem_type": "half_subdivision_neighbours",
        "requires_visual": requires_visual,
    }
    if tags:
        metadata["tags"] = list(tags)
    if difficulty:
        metadata["difficulty"] = difficulty

    content_id = record_id or compute_content_hash(
        problem_type="half_subdivision_neighbours",
        datagen_args={**datagen_args},
        prompt=prompt,
        ground_truth=ground_truth,
    )

    return {
        "id": content_id,
        "prompt": prompt,
        "ground_truth": ground_truth,
        "metadata": metadata,
        "datagen_args": {**datagen_args},
        "runtime": {
            "target_label": target.display_label(),
            "neighbour_count": len(ground_truth),
            **runtime_info,
        },
    }
