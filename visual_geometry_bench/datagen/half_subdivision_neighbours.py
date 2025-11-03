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
    """Enumeration of supported spatial dimensions for half subdivisions."""

    D2 = 2
    D3 = 3


@dataclass(frozen=True)
class Leaf:
    """Axis-aligned leaf cell with normalised label and bounding box."""

    label: str
    x0: float
    y0: float
    x1: float
    y1: float
    z0: float = 0.0
    z1: float = 1.0

    def display_label(self) -> str:
        """Return label formatting empty strings as '""'."""

        return self.label if self.label else '""'


def _axis_for_depth(depth: int, axis_cycle: Sequence[str]) -> str:
    """Return the axis to split on at the given depth using the configured cycle."""

    if not axis_cycle:
        raise ValueError("axis_cycle must contain at least one axis")
    return axis_cycle[depth % len(axis_cycle)]


def _resolve_axis_cycle(
    dim: Dimension,
    *,
    axis_cycle: Sequence[str] | None,
    start_axis: str | None,
) -> tuple[str, ...]:
    """Determine the axis cycle for the subdivision based on inputs and dimension."""

    allowed_axes = {"x", "y"} if dim == Dimension.D2 else {"x", "y", "z"}
    default_cycle = ("x", "y") if dim == Dimension.D2 else ("x", "y", "z")

    # Case 1: Custom axis cycle provided
    if axis_cycle is not None:
        if isinstance(axis_cycle, (str, bytes)):
            raise ValueError("axis_cycle must be a sequence of axis names, not a string")
        
        if not hasattr(axis_cycle, '__iter__'):
            raise ValueError("axis_cycle must be an iterable sequence")
        
        normalised_cycle = [str(axis).lower() for axis in axis_cycle]
        
        if not normalised_cycle:
            raise ValueError("axis_cycle must contain at least one axis")
        
        invalid_axes = [axis for axis in normalised_cycle if axis not in allowed_axes]
        if invalid_axes:
            raise ValueError(
                f"axis_cycle contains invalid axes {invalid_axes} for dimension {dim.name}. "
                f"Allowed: {sorted(allowed_axes)}"
            )
        
        return tuple(normalised_cycle)
    
    # Case 2: Use default cycle, optionally rotated by start_axis
    if start_axis is None:
        return default_cycle
    
    start = start_axis.lower()
    if start not in allowed_axes:
        raise ValueError(
            f"start_axis '{start}' is not valid for dimension {dim.name}. "
            f"Allowed: {sorted(allowed_axes)}"
        )
    
    if start not in default_cycle:
        raise ValueError(
            f"start_axis '{start}' is not in the default cycle {default_cycle} for dimension {dim.name}"
        )
    
    index = default_cycle.index(start)
    return default_cycle[index:] + default_cycle[:index]


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
    axis_cycle: tuple[str, ...],
    dim: Dimension,
    rng: random.Random,
) -> list[Leaf]:
    """Recursively split the current cell, populating tree nodes and leaves."""

    node_id = label if label else "__root__"
    if tree.root is None:
        tree.create_node(tag=Leaf(label, x0, y0, x1, y1, z0, z1).display_label(), identifier=node_id)
    else:
        tree.create_node(tag=Leaf(label, x0, y0, x1, y1, z0, z1).display_label(), identifier=node_id, parent=parent_id)

    if depth == max_depth or (depth >= min_depth and rng.random() >= split_prob):
        return [Leaf(label, x0, y0, x1, y1, z0, z1)]

    axis = _axis_for_depth(depth, axis_cycle)
    
    # Define axis-specific coordinate modifications
    axis_params = {
        "x": {"lo": "x0", "hi": "x1"},
        "y": {"lo": "y0", "hi": "y1"},
        "z": {"lo": "z0", "hi": "z1"},
    }
    
    if axis not in axis_params:
        raise ValueError(f"Invalid axis '{axis}'. Must be 'x', 'y', or 'z'")
    
    params = axis_params[axis]
    bounds = {"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z0": z0, "z1": z1}
    lo_key, hi_key = params["lo"], params["hi"]
    mid = 0.5 * (bounds[lo_key] + bounds[hi_key])
    
    # Common recursion parameters
    recurse_args = {
        "tree": tree,
        "parent_id": node_id,
        "depth": depth + 1,
        "max_depth": max_depth,
        "min_depth": min_depth,
        "split_prob": split_prob,
        "axis_cycle": axis_cycle,
        "dim": dim,
        "rng": rng,
    }
    
    leaves: list[Leaf] = []
    
    # Child 0: lower half along split axis
    bounds_0 = {**bounds, hi_key: mid}
    leaves.extend(_build_subdivision(label=label + "0", **bounds_0, **recurse_args))
    
    # Child 1: upper half along split axis
    bounds_1 = {**bounds, lo_key: mid}
    leaves.extend(_build_subdivision(label=label + "1", **bounds_1, **recurse_args))
    
    return leaves


def _overlap(lo1: float, hi1: float, lo2: float, hi2: float) -> bool:
    """Return True when open intervals overlap beyond the floating tolerance."""

    return max(lo1, lo2) < min(hi1, hi2) - _EPS


def _are_adjacent(a: Leaf, b: Leaf, dim: Dimension) -> bool:
    """Return True when two leaves share a face in the chosen dimension.

    Two rectangles (D2) are adjacent if they touch along an edge of non-zero
    length within the floating tolerance ``_EPS`` along one axis while their
    extents overlap on the orthogonal axis. In 3-D we extend the rule to
    cuboids with 6-connectivity: faces coincide (within ``_EPS``) on one axis
    and their projections overlap on the remaining two axes.
    """
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
    """Strip whitespace and map empty sentinel labels to canonical form."""

    if label is None:
        return None
    label = label.strip()
    return "" if label in {"", '""'} else label


def _prepare_case(datagen_args: dict) -> tuple[str, Leaf, list[Leaf], dict]:
    """Build a deterministic subdivision and return tree text, target, neighbours, runtime."""

    if not isinstance(datagen_args, dict):
        raise TypeError("datagen_args must be a dictionary")

    # Extract and validate required parameters
    if "max_depth" not in datagen_args:
        raise ValueError("datagen_args missing required field 'max_depth'")
    if "seed" not in datagen_args:
        raise ValueError("datagen_args missing required field 'seed'")
    if "split_prob" not in datagen_args:
        raise ValueError("datagen_args missing required field 'split_prob'")
    
    max_depth = int(datagen_args["max_depth"])
    seed = int(datagen_args["seed"])
    split_prob = float(datagen_args["split_prob"])

    # Parse dimension
    dim_name = str(datagen_args.get("dimension", "2D")).upper()
    if dim_name == "2D":
        dim = Dimension.D2
    elif dim_name == "3D":
        dim = Dimension.D3
    else:
        raise ValueError(f"Invalid dimension '{dim_name}'. Must be '2D' or '3D'")

    min_depth = int(datagen_args.get("min_depth", 0))
    start_axis = datagen_args.get("start_axis")
    axis_cycle = _resolve_axis_cycle(
        dim,
        axis_cycle=datagen_args.get("axis_cycle"),
        start_axis=start_axis,
    )
    target_label = _normalise_label(datagen_args.get("target_label"))

    if max_depth < 0 or min_depth < 0:
        raise ValueError("depth values must be non-negative")
    if split_prob < 0.0 or split_prob > 1.0:
        raise ValueError("split_prob must be within [0, 1]")
    if min_depth > max_depth:
        raise ValueError("min_depth cannot exceed max_depth")
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

    if not leaves:
        raise RuntimeError("subdivision produced no leaves")

    leaves_by_label = {leaf.label: leaf for leaf in leaves}

    if target_label is None:
        target = rng.choice(leaves)
    elif target_label not in leaves_by_label:
        available = sorted(leaves_by_label.keys())[:10]  # Show first 10 for context
        raise ValueError(
            f"target_label '{target_label}' is not a leaf in this subdivision. "
            f"Available leaves (first 10): {available}"
        )
    else:
        target = leaves_by_label[target_label]

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
        "start_axis": axis_cycle[0],
        "axis_cycle": list(axis_cycle),
        "dimension": dim_name,
        **({"target_label": target.display_label()} if target_label is not None else {}),
    }

    return treelib_text, target, neighbours, runtime_info


_2D_PROMPT_TEMPLATE = """You are given a binary tree describing an axis-aligned half subdivision of the unit square.

Each node splits its parent cell into two children by bisecting along axes in the repeating cycle {axis_cycle_text}.

Here is the subdivision tree:

```
{tree_text}
```

Target leaf: {target_label}

Before presenting the final list, begin your response with <thinking>...</thinking> containing your full chain of thought or reasoning for your answer.
List every leaf that shares a boundary segment with the target. Return the labels as a comma-separated list of strings (quotes optional)."""


_3D_PROMPT_TEMPLATE = """You are given a binary tree describing an axis-aligned half subdivision of the unit cube.

Each node splits its parent cell into two children by bisecting along axes in the repeating cycle {axis_cycle_text}.

Here is the subdivision tree:

```
{tree_text}
```

Target leaf: {target_label}

Before presenting the final list, begin your response with <thinking>...</thinking> containing your full chain of thought or reasoning for your answer.
List every leaf that shares a face with the target voxel. Return the labels as a comma-separated list of strings (quotes optional)."""


def _format_prompt(tree_text: str, target: Leaf, dim: Dimension, axis_cycle: Sequence[str]) -> str:
    """Render the user-facing prompt for the given subdivision and dimension."""

    template = _3D_PROMPT_TEMPLATE if dim == Dimension.D3 else _2D_PROMPT_TEMPLATE
    axis_cycle_text = " → ".join(axis_cycle)
    return template.format(
        tree_text=tree_text.rstrip(),
        target_label=target.display_label(),
        axis_cycle_text=f"{axis_cycle_text} (repeating)",
    )


def _canonical_labels(leaves: Iterable[Leaf]) -> list[str]:
    """Extract display labels for a collection of leaves in stable order."""

    return [leaf.display_label() for leaf in leaves]


def make_prompt(datagen_args: dict) -> str:
    """Generate a prompt matching the provided half-subdivision configuration."""

    tree_text, target, _, runtime = _prepare_case(datagen_args)
    dim_name = runtime["dimension"]
    dim = Dimension.D2 if dim_name == "2D" else Dimension.D3 if dim_name == "3D" else Dimension[dim_name]
    axis_cycle = tuple(runtime.get("axis_cycle", []))
    if not axis_cycle:
        axis_cycle = ("x", "y") if dim == Dimension.D2 else ("x", "y", "z")
    return _format_prompt(tree_text, target, dim, axis_cycle)


def get_solutions(datagen_args: dict) -> list[str]:
    """Return the canonical neighbour labels for the configured subdivision."""

    tree_text, target, neighbours, runtime = _prepare_case(datagen_args)
    _ = tree_text, target, runtime  # unused beyond deterministic generation
    return _canonical_labels(neighbours)


def generate_dataset_record(
    datagen_args: dict,
    *,
    record_id: str | None = None,
    tags: Sequence[str] | None = None,
    difficulty: str | None = None,
) -> dict:
    """Assemble a dataset record with prompt, neighbours, and metadata.

    Args:
        datagen_args: Data generator arguments.
        record_id: Record ID (optional).
        tags: Record tags (optional).
        difficulty: Record difficulty (optional).

    Returns:
        dict: The generated dataset record.
    """

    tree_text, target, neighbours, runtime_info = _prepare_case(datagen_args)
    dim_name = runtime_info["dimension"]
    dim = Dimension.D2 if dim_name == "2D" else Dimension.D3 if dim_name == "3D" else Dimension[dim_name]

    axis_cycle = tuple(runtime_info.get("axis_cycle", []))
    if not axis_cycle:
        axis_cycle = ("x", "y") if dim == Dimension.D2 else ("x", "y", "z")

    prompt = _format_prompt(tree_text, target, dim, axis_cycle)
    ground_truth = _canonical_labels(neighbours)

    metadata = {"problem_type": "half_subdivision_neighbours"}
    if tags:
        metadata["tags"] = list(tags)
    if difficulty:
        metadata["difficulty"] = difficulty

    stored_datagen_args = {**datagen_args}
    stored_datagen_args["axis_cycle"] = list(axis_cycle)

    content_id = record_id or compute_content_hash(
        problem_type="half_subdivision_neighbours",
        datagen_args=stored_datagen_args,
        prompt=prompt,
        ground_truth=ground_truth,
    )

    return {
        "id": content_id,
        "prompt": prompt,
        "ground_truth": ground_truth,
        "metadata": metadata,
        "datagen_args": stored_datagen_args,
        "runtime": {
            "target_label": target.display_label(),
            "neighbour_count": len(ground_truth),
            **runtime_info,
        },
    }
