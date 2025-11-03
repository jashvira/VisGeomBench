"""Dataset generation for topology edge tasks (dict-driven, 2–3 classes).

This module generates evaluation problems asking models to either enumerate edge
connections or classify topological behaviour for square corner configurations.

Two subtasks (selected via ``datagen_args.subtask``):

1. **enumerate_edges**: For two-class guaranteed cases only. Outputs the
   guaranteed edge connections as integer index pairs following a provided
   edge-index convention (``edge_order``). Cases must be from the guaranteed
   behaviour class; ambiguous or triple junction cases are invalid and will
   raise assertions.

2. **classify_behaviour**: For two- or three-class cases. Labels each case as
   one of {known behaviour, three domains meeting, ambiguous}. No edge joining
   is requested for triple junction cases.

Corner order (``corner_order``) and edge index order (``edge_order``) are
configurable per record for question variety. Internally, all inputs are permuted
to canonical corner order and relabelled via first-occurrence (1-based) before
looking up hardcoded canonical truth dictionaries.

Canonical forms:
- Corner order: (bottom-left, bottom-right, top-right, top-left)
- Edge order: (bottom, right, top, left) with indices (0, 1, 2, 3)
- Labels: first-occurrence 1-based relabelling (e.g., (7,5,7,3) → (1,2,1,3))
"""

from __future__ import annotations

from visual_geometry_bench.datagen.utils import (
    CANONICAL_CORNER_ORDER,
    canonicalize_first_occurrence,
    compute_content_hash,
    corner_order_permutation,
    permute_config,
    validate_corner_order,
)

# Canonical edge order used by canonical dictionaries (indices 0..3)
_CANONICAL_EDGE_ORDER = ("bottom", "right", "top", "left")


def _edge_index_map(edge_order: tuple[str, str, str, str]) -> dict[str, int]:
    """Validate edge_order and return edge name to index mapping.

    Args:
        edge_order: 4-tuple defining index convention for edges

    Returns:
        Dictionary mapping each edge name to its positional index (0-3)

    Raises:
        ValueError: If edge_order is not a valid permutation of edge names
    """
    if (
        not isinstance(edge_order, tuple)
        or len(edge_order) != 4
        or set(edge_order) != {"bottom", "right", "top", "left"}
    ):
        raise ValueError(
            "edge_order must be a permutation of ('bottom','right','top','left')"
        )
    return {name: idx for idx, name in enumerate(edge_order)}


def _reindex_pairs_from_canonical(
    pairs_canon: list[list[int]], edge_order: tuple[str, str, str, str]
) -> list[list[int]]:
    """Reindex edge pairs from canonical indices into the provided edge_order.

    Canonical indices use (0=bottom, 1=right, 2=top, 3=left). This function
    converts them to the indices defined by edge_order, normalises each pair
    to [i, j] with i < j, and sorts the list lexicographically.

    Args:
        pairs_canon: List of 2-element lists with canonical edge indices
        edge_order: Target edge order defining new indices

    Returns:
        List of reindexed pairs [[i, j], ...] with i < j, sorted ascending
    """
    name_for_canon_index = {i: n for i, n in enumerate(_CANONICAL_EDGE_ORDER)}
    name_to_out_index = _edge_index_map(edge_order)

    reindexed: list[list[int]] = []
    for i, j in pairs_canon:
        a_name = name_for_canon_index[i]
        b_name = name_for_canon_index[j]
        ai = name_to_out_index[a_name]
        bj = name_to_out_index[b_name]
        u, v = (ai, bj) if ai < bj else (bj, ai)
        reindexed.append([u, v])
    reindexed.sort()
    return reindexed


# Behaviour classification lookup (canonical first-occurrence 1-based keys).
# Maps each canonical corner configuration to its topological behaviour class:
# - "known behaviour": deterministic edge-connection behaviour
# - "ambiguous": multiple valid realisations exist
# - "three domains meeting": three classes meet at a point (3-class only)
CLASS_DICT: dict[tuple[int, int, int, int], str] = {
    (1, 1, 1, 1): "known behaviour",
    (1, 1, 1, 2): "known behaviour",
    (1, 1, 2, 1): "known behaviour",
    (1, 1, 2, 2): "known behaviour",
    (1, 1, 2, 3): "three domains meeting",
    (1, 2, 1, 1): "known behaviour",
    (1, 2, 1, 2): "ambiguous",
    (1, 2, 1, 3): "known behaviour",
    (1, 2, 2, 1): "known behaviour",
    (1, 2, 2, 2): "known behaviour",
    (1, 2, 2, 3): "three domains meeting",
    (1, 2, 3, 1): "three domains meeting",
    (1, 2, 3, 2): "known behaviour",
    (1, 2, 3, 3): "three domains meeting",
    (1, 2, 3, 4): "ambiguous",
}


# Edge connection pairs for 2-class known behaviour configurations.
# Keys are canonical first-occurrence 1-based corner configs; values are lists
# of edge-index pairs using canonical indices (0=bottom, 1=right, 2=top, 3=left).
# Each pair [i, j] is normalised with i < j; lists are sorted lexicographically.
QUAD_EDGE_DICT: dict[tuple[int, int, int, int], list[list[int]]] = {
    (1, 1, 1, 1): [],
    (1, 1, 1, 2): [[2, 3]],
    (1, 1, 2, 1): [[1, 2]],
    (1, 1, 2, 2): [[1, 3]],
    (1, 2, 1, 1): [[0, 1]],
    (1, 2, 2, 1): [[0, 2]],
    (1, 2, 2, 2): [[0, 3]],
    (1, 2, 1, 3): [[0, 1], [2, 3]],
    (1, 2, 3, 2): [[1, 2], [0, 3]],
}


# Standard registry of canonical corner configs keyed by integer IDs (0..14).
# Each value is a 4-tuple in canonical corner order with first-occurrence
# 1-based relabelling.
CASE_REGISTRY: dict[int, tuple[int, int, int, int]] = {
    0: (1, 1, 1, 1),
    1: (1, 1, 1, 2),
    2: (1, 1, 2, 1),
    3: (1, 1, 2, 2),
    4: (1, 1, 2, 3),
    5: (1, 2, 1, 1),
    6: (1, 2, 1, 2),
    7: (1, 2, 1, 3),
    8: (1, 2, 2, 1),
    9: (1, 2, 2, 2),
    10: (1, 2, 2, 3),
    11: (1, 2, 3, 1),
    12: (1, 2, 3, 2),
    13: (1, 2, 3, 3),
    14: (1, 2, 3, 4),
}


def _inverse_perm(perm: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    """Compute the inverse of a 4-permutation.

    inv[p[i]] = i.
    """
    inv = [0, 0, 0, 0]
    for i, p in enumerate(perm):
        inv[p] = i
    return tuple(inv)  # type: ignore[return-value]


def _resolve_cases(
    cases: list, corner_order: tuple[str, str, str, str]
) -> list[dict]:
    """Resolve cases into a list of {id, config} using CASE_REGISTRY when needed.

    Accepts either:
    - list of integers (IDs into CASE_REGISTRY)
    - list of {id, config} dicts (already concrete)

    The config returned is expressed in the provided corner_order.
    """
    resolved: list[dict] = []
    perm = corner_order_permutation(corner_order)
    inv = _inverse_perm(perm)

    for item in cases:
        if isinstance(item, dict):
            # Assume already in provided order
            cid = item["id"]
            cfg = tuple(item["config"])  # type: ignore[assignment]
            resolved.append({"id": cid, "config": list(cfg)})
        else:
            # Treat as integer ID into registry
            cid = int(item)
            assert (
                cid in CASE_REGISTRY
            ), f"unknown case id {cid}; not in CASE_REGISTRY"
            cfg_canon = CASE_REGISTRY[cid]
            # Convert canonical-order config into provided corner_order for display
            cfg_in_order = permute_config(cfg_canon, inv)
            resolved.append({"id": cid, "config": list(cfg_in_order)})

    return resolved


def _validate_datagen_args(datagen_args: dict) -> tuple[str, tuple[str, str, str, str]]:
    """Extract and validate common datagen_args parameters.

    Args:
        datagen_args: Dictionary with at least 'subtask' and optional 'corner_order'

    Returns:
        Tuple of (subtask, corner_order) after validation

    Raises:
        AssertionError: If subtask is invalid
        ValueError: If corner_order is invalid
    """
    subtask = datagen_args.get("subtask")
    assert subtask in {"enumerate_edges", "classify_behaviour"}, "invalid subtask"
    corner_order = validate_corner_order(
        datagen_args.get("corner_order", CANONICAL_CORNER_ORDER)
    )
    return subtask, corner_order


def make_prompt(datagen_args: dict) -> str:
    """Generate a concise, natural-language prompt for the specified subtask.

    Only include information necessary for the model to answer correctly.
    """
    subtask, corner_order = _validate_datagen_args(datagen_args)

    lines: list[str] = []

    # Common header for both subtasks
    lines.append("Squares (each tuple lists the four corner labels; integers denote distinct classes):")
    resolved_cases = _resolve_cases(datagen_args.get("cases", []), corner_order)
    for c in resolved_cases:
        lines.append(f"{tuple(c['config'])}")
    lines.append("")
    lines.append(f"You are given unit squares with corners labelled in {corner_order} order.")

    if subtask == "enumerate_edges":
        edge_order = tuple(
            datagen_args.get("edge_order", _CANONICAL_EDGE_ORDER)
        )  # type: ignore[assignment]
        _edge_index_map(edge_order)  # validate

        # Build mapping representation like "bottom=0, right=1, top=2, left=3"
        edge_map_repr = ", ".join(f"{name}={idx}" for idx, name in enumerate(edge_order))

        lines.extend([
            f"Edges are indexed: {edge_map_repr}.",
            "",
            "For each square above (in the same order), list which edges are guaranteed to connect.",
            "Return a list where each element is a list of sorted [i,j] pairs (i < j).",
            "If no edges are deterministically guaranteed (including ambiguous cases), return [] for that square.",
        ])
    else:  # classify_behaviour
        lines.extend([
            "",
            "Classify each square's topological behaviour (in the same order) as one of: 'known behaviour', 'three domains meeting', or 'ambiguous'.",
            "Definitions: 'known behaviour' = deterministic edge connections can be made; 'three domains meeting' = deterministic edge connections where three distinct classes meet at a point; 'ambiguous' = multiple valid topologies could exist.",
            "Return a list of exact label strings.",
        ])
    return "\n".join(lines)


def get_solutions(datagen_args: dict) -> list:
    """Compute ground truth as the exact list the model should output.

    For enumerate_edges: list of lists of [i,j] pairs (one per case).
    For classify_behaviour: list of label strings (one per case).

    Args:
        datagen_args: Dictionary with keys:
            - subtask: "enumerate_edges" | "classify_behaviour"
            - cases: list[int] (IDs into CASE_REGISTRY)
            - corner_order (optional): corner reading order
            - edge_order (optional): edge index convention (enumerate_edges only)

    Returns:
        List matching the model's expected output format, in the same order as cases.

    Raises:
        AssertionError: If subtask is invalid, cases are malformed, or
                        enumerate_edges receives non-guaranteed cases
    """
    subtask, corner_order = _validate_datagen_args(datagen_args)

    cases = _resolve_cases(datagen_args.get("cases", []), corner_order)

    results: list = []

    # Validate and prepare edge order if needed
    if subtask == "enumerate_edges":
        edge_order = tuple(
            datagen_args.get("edge_order", _CANONICAL_EDGE_ORDER)
        )  # type: ignore[assignment]
        _edge_index_map(edge_order)  # validate
    else:
        edge_order = _CANONICAL_EDGE_ORDER

    for case in cases:
        cfg_in = tuple(case["config"])  # user-specified order
        assert len(cfg_in) == 4, "config must have 4 integers"

        # Permute to canonical corner order, then 1-based canonical relabel
        perm = corner_order_permutation(corner_order)
        cfg_canon_order = permute_config(cfg_in, perm)
        cfg_canon = canonicalize_first_occurrence(cfg_canon_order, start_label=1)

        # Behaviour from CLASS_DICT
        assert (
            cfg_canon in CLASS_DICT
        ), f"unsupported canonical config {cfg_canon} (not in CLASS_DICT)"
        behaviour = CLASS_DICT[cfg_canon]

        if subtask == "enumerate_edges":
            # Disallow triple-junction cases; allow known and ambiguous.
            assert (
                behaviour != "three domains meeting"
            ), f"enumerate_edges does not accept 'three domains meeting' cases: {cfg_canon}"

            if behaviour == "known behaviour":
                # Known deterministic behaviour: use QUAD_EDGE_DICT (may be empty for (1,1,1,1)).
                assert (
                    cfg_canon in QUAD_EDGE_DICT
                ), f"missing edge mapping for {cfg_canon} in QUAD_EDGE_DICT"
                pairs_canon = QUAD_EDGE_DICT[cfg_canon]
                pairs_out = _reindex_pairs_from_canonical(pairs_canon, edge_order)
                results.append(pairs_out)
            else:
                # Ambiguous behaviour: no guaranteed connections → empty list.
                results.append([])
        else:
            results.append(behaviour)

    return results


def generate_dataset_record(
    datagen_args: dict,
    *,
    record_id: str | None = None,
    tags: list[str] | None = None,
    difficulty: str | None = None,
) -> dict:
    """Generate a complete evaluation record for topology edge tasks.

    Produces a dataset record containing prompt, ground truth, metadata, and
    generation arguments. The record ID is content-addressed by default.

    Args:
        datagen_args: Dictionary with required keys:
            - subtask: "enumerate_edges" | "classify_behaviour"
            - cases: list[int] (IDs into CASE_REGISTRY)
          Optional keys:
            - corner_order: permutation of canonical corners
            - edge_order: permutation of edge names (enumerate_edges only)
        record_id: Optional custom ID (otherwise content-addressed hash)
        tags: List of tags for categorisation
        difficulty: Difficulty level string

    Returns:
        Dictionary with keys:
            - id: str (record identifier)
            - prompt: str (problem statement)
            - ground_truth: list (model's expected answer format)
            - metadata: dict (problem_type, tags, difficulty)
            - datagen_args: dict (reproducibility arguments)

    Raises:
        AssertionError: If datagen_args is missing required keys or malformed
    """
    assert isinstance(datagen_args, dict)
    assert "subtask" in datagen_args, "datagen_args missing 'subtask'"
    assert "cases" in datagen_args, "datagen_args missing 'cases'"

    prompt = make_prompt(datagen_args)
    ground_truth = get_solutions(datagen_args)

    rid = record_id or compute_content_hash(
        problem_type="topology_edge_tasks",
        datagen_args=datagen_args,
        prompt=prompt,
        ground_truth=ground_truth,
        hash_name="sha1",
        prefix_len=8,
    )

    metadata = {
        "problem_type": "topology_edge_tasks",
        "tags": list(set(tags or [])),
        "difficulty": difficulty or "",
    }

    return {
        "id": rid,
        "prompt": prompt,
        "ground_truth": ground_truth,
        "metadata": metadata,
        "datagen_args": datagen_args,
    }


