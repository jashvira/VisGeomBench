"""Tests for topology edge tasks verification."""

import pytest

from visual_geometry_bench.datagen.topology_edge_tasks import generate_dataset_record
from visual_geometry_bench.verification.topology_edge_tasks import verify_topology_edge_tasks


@pytest.fixture
def record_enumerate_edges():
    """Fixture for enumerate_edges subtask."""
    return generate_dataset_record(
        datagen_args={
            "subtask": "enumerate_edges",
            "corner_order": ("bottom-left", "bottom-right", "top-right", "top-left"),
            "edge_order": ("bottom", "right", "top", "left"),
            "cases": [3, 8, 12],  # IDs from CASE_REGISTRY
        }
    )


@pytest.fixture
def record_classify_behaviour():
    """Fixture for classify_behaviour subtask."""
    return generate_dataset_record(
        datagen_args={
            "subtask": "classify_behaviour",
            "cases": [13, 6, 9],  # IDs from CASE_REGISTRY
        }
    )


# enumerate_edges pass cases


def test_enumerate_exact_match(record_enumerate_edges):
    """Exact match passes for enumerate_edges."""
    output = "[[[1, 3]], [[0, 2]], [[0, 3], [1, 2]]]"
    assert verify_topology_edge_tasks(output, record_enumerate_edges)


def test_enumerate_empty_case(record_enumerate_edges):
    """Empty edge list for homogeneous square."""
    record = generate_dataset_record(
        datagen_args={
            "subtask": "enumerate_edges",
            "cases": [0],  # ID from CASE_REGISTRY
        }
    )
    output = "[[]]"
    assert verify_topology_edge_tasks(output, record)


# classify_behaviour pass cases


def test_classify_exact_match(record_classify_behaviour):
    """Exact match passes for classify_behaviour."""
    output = '["three domains meeting", "ambiguous", "known behaviour"]'
    assert verify_topology_edge_tasks(output, record_classify_behaviour)


def test_classify_single_case():
    """Single classification case."""
    record = generate_dataset_record(
        datagen_args={
            "subtask": "classify_behaviour",
            "cases": [13],  # ID from CASE_REGISTRY
        }
    )
    output = '["three domains meeting"]'
    assert verify_topology_edge_tasks(output, record)


def test_python_literal_format(record_classify_behaviour):
    """Python literal lists with single quotes are accepted."""
    output = "['three domains meeting', 'ambiguous', 'known behaviour']"
    assert verify_topology_edge_tasks(output, record_classify_behaviour)


# Parse failure cases


def test_parse_failure_invalid_json(record_enumerate_edges):
    """Invalid JSON fails."""
    assert not verify_topology_edge_tasks("not valid json", record_enumerate_edges)


def test_parse_failure_not_list(record_enumerate_edges):
    """JSON object instead of list fails."""
    output = '{"a": [[1, 3]]}'
    assert not verify_topology_edge_tasks(output, record_enumerate_edges)


# Length mismatch cases


def test_length_mismatch_too_short(record_enumerate_edges):
    """Too few answers fails."""
    output = "[[[1, 3]], [[0, 2]]]"  # Missing third case
    assert not verify_topology_edge_tasks(output, record_enumerate_edges)


def test_length_mismatch_too_long(record_classify_behaviour):
    """Too many answers fails."""
    output = '["three domains meeting", "ambiguous", "known behaviour", "ambiguous"]'
    assert not verify_topology_edge_tasks(output, record_classify_behaviour)


# enumerate_edges format validation


def test_enumerate_not_list_of_lists(record_enumerate_edges):
    """Each element must be a list."""
    output = '[[[1, 3]], "invalid", [[0, 1]]]'
    assert not verify_topology_edge_tasks(output, record_enumerate_edges)


def test_enumerate_invalid_pair_format(record_enumerate_edges):
    """Pairs must be 2-element lists."""
    output = "[[[1, 3]], [[0, 2, 1]], [[0, 1]]]"  # 3-element pair
    assert not verify_topology_edge_tasks(output, record_enumerate_edges)


def test_enumerate_non_integer_indices(record_enumerate_edges):
    """Pair elements must be integers."""
    output = '[[[1, 3]], [[0, "2"]], [[0, 1]]]'
    assert not verify_topology_edge_tasks(output, record_enumerate_edges)


def test_enumerate_unsorted_pair(record_enumerate_edges):
    """Pairs must be sorted (i < j)."""
    output = "[[[3, 1]], [[0, 2]], [[0, 1]]]"  # [3, 1] should be [1, 3]
    assert not verify_topology_edge_tasks(output, record_enumerate_edges)


def test_enumerate_unordered_list_allowed(record_enumerate_edges):
    """Ordering of pairs list is not enforced; content equality matters only."""
    output = "[[[1, 3]], [[0, 2]], [[1, 2], [0, 3]]]"  # Last case out of order
    assert verify_topology_edge_tasks(output, record_enumerate_edges)


def test_enumerate_equal_indices_rejected(record_enumerate_edges):
    """Pairs with i == j are invalid."""
    output = "[[[1, 1]], [[0, 2]], [[0, 1]]]"
    assert not verify_topology_edge_tasks(output, record_enumerate_edges)


# classify_behaviour format validation


def test_classify_not_string(record_classify_behaviour):
    """Labels must be strings."""
    output = '["three domains meeting", 123, "known behaviour"]'
    assert not verify_topology_edge_tasks(output, record_classify_behaviour)


def test_classify_invalid_label(record_classify_behaviour):
    """Labels must be one of the valid options."""
    output = '["three domains meeting", "unknown", "known behaviour"]'
    assert not verify_topology_edge_tasks(output, record_classify_behaviour)


def test_classify_case_sensitive(record_classify_behaviour):
    """Labels are case-sensitive."""
    output = '["three domains meeting", "Ambiguous", "known behaviour"]'
    assert not verify_topology_edge_tasks(output, record_classify_behaviour)


def test_classify_no_whitespace_variation(record_classify_behaviour):
    """Labels must match exactly (no extra whitespace)."""
    output = '["three domains meeting", " ambiguous ", "known behaviour"]'
    assert not verify_topology_edge_tasks(output, record_classify_behaviour)




# return_diff mode tests


def test_diff_parse_failure(record_enumerate_edges):
    """Diff mode reports parse failure."""
    result = verify_topology_edge_tasks("invalid", record_enumerate_edges, return_diff=True)
    assert not result["passed"]
    assert "parse_failure" in result["errors"]
    assert result["missing"] == []


def test_diff_length_mismatch(record_enumerate_edges):
    """Diff mode reports length mismatch."""
    result = verify_topology_edge_tasks("[[[1, 3]]]", record_enumerate_edges, return_diff=True)
    assert not result["passed"]
    assert any("length_mismatch" in err for err in result["errors"])


def test_diff_format_errors(record_enumerate_edges):
    """Diff mode collects all format errors."""
    output = '[[[3, 1]], "not_list", [[0, 2, 3]]]'
    result = verify_topology_edge_tasks(output, record_enumerate_edges, return_diff=True)
    assert not result["passed"]
    assert len(result["errors"]) == 3


def test_diff_mismatches(record_classify_behaviour):
    """Diff mode reports mismatches in missing list."""
    output = '["known behaviour", "ambiguous", "ambiguous"]'
    result = verify_topology_edge_tasks(output, record_classify_behaviour, return_diff=True)
    assert not result["passed"]
    assert len(result["missing"]) == 2
    assert 0 in result["missing"]  # First position (expected "three domains meeting")
    assert 2 in result["missing"]  # Third position (expected "known behaviour")


def test_diff_success(record_enumerate_edges):
    """Diff mode shows success for correct answer."""
    output = "[[[1, 3]], [[0, 2]], [[0, 3], [1, 2]]]"
    result = verify_topology_edge_tasks(output, record_enumerate_edges, return_diff=True)
    assert result["passed"]
    assert result["errors"] == []
    assert result["missing"] == []

