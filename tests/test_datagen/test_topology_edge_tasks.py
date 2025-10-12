"""Tests for topology_edge_tasks datagen.

Validates edge enumeration reindexing, behaviour classification labels, and
basic record structure (including prompt format expectations).
"""
from visual_geometry_bench.datagen.topology_edge_tasks import (
    generate_dataset_record,
    get_solutions,
)


def test_enumerate_edges_guaranteed_pairs_and_reindex():
    """Edge enumeration returns correct pairs and honours edge index order."""
    args = {
        "subtask": "enumerate_edges",
        "corner_order": ("bottom-left","bottom-right","top-right","top-left"),
        "edge_order": ("bottom","right","top","left"),
        "cases": [3, 8, 12],  # IDs from CASE_REGISTRY
    }
    sol = get_solutions(args)
    # Solution is now a list in same order as cases
    assert sol[0] == [[1,3]]  # case 3: (1,1,2,2) → right-left
    assert sol[1] == [[0,2]]  # case 8: (1,2,2,1) → bottom-top
    # case 12: (1,2,3,2) → right-top, bottom-left
    assert sorted(sol[2]) == [[0,3],[1,2]]  # case 12


def test_classify_behaviour_labels():
    """Classification labels match expected canonical-case mappings."""
    args = {
        "subtask": "classify_behaviour",
        "cases": [13, 6, 9],  # IDs from CASE_REGISTRY
    }
    sol = get_solutions(args)
    # Solution is now a list in same order as cases
    assert sol[0] == "three domains meeting"  # case 13
    assert sol[1] == "ambiguous"  # case 6
    assert sol[2] == "known behaviour"  # case 9


def test_generate_record_structure():
    """Record includes required keys and prompt lists cases before instructions."""
    args = {
        "subtask": "enumerate_edges",
        "cases": [3],  # ID from CASE_REGISTRY
    }
    rec = generate_dataset_record(args)
    assert set(rec.keys()) >= {"id","prompt","ground_truth","metadata","datagen_args"}
    assert "topology_edge_tasks" in rec["metadata"]["problem_type"]
    # Prompt should list cases first
    non_empty = [ln for ln in rec["prompt"].splitlines() if ln.strip()]
    assert non_empty[0].startswith("Squares (")

