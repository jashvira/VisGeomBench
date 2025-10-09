"""Tests for topology enumeration verification."""

import pytest

from visual_geometry_bench.datagen.topology_enumeration import generate_dataset_record
from visual_geometry_bench.verification import verify_topology_enumeration


@pytest.fixture
def record_n2():
    return generate_dataset_record(
        datagen_args={"n_classes": 2, "corner_order": ["bottom-left", "bottom-right", "top-right", "top-left"]}
    )


@pytest.fixture
def record_n3():
    return generate_dataset_record(
        datagen_args={"n_classes": 3, "corner_order": ["bottom-left", "bottom-right", "top-right", "top-left"]}
    )


def test_exact_match(record_n2):
    """Exact match passes."""
    output = "[(1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1), (0, 0, 1, 1), (0, 1, 1, 0), (0, 1, 0, 1)]"
    assert verify_topology_enumeration(output, record_n2)


def test_list_order_invariant(record_n2):
    """List order doesn't matter."""
    output = "[(0, 1, 0, 1), (0, 1, 1, 0), (0, 0, 1, 1), (0, 0, 0, 1), (0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0)]"
    assert verify_topology_enumeration(output, record_n2)


def test_no_duplicates_allowed(record_n2):
    """Duplicates change length and must fail under exact-match semantics."""
    output = "[(1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1), (0, 0, 1, 1), (0, 1, 1, 0), (0, 1, 0, 1), (1, 0, 0, 0)]"
    assert not verify_topology_enumeration(output, record_n2)


def test_canonical_equivalence(record_n2):
    """Canonically equivalent tuples pass."""
    output = "[(0, 1, 1, 1), (1, 0, 1, 1), (1, 1, 0, 1), (1, 1, 1, 0), (1, 1, 0, 0), (1, 0, 0, 1), (1, 0, 1, 0)]"
    assert verify_topology_enumeration(output, record_n2)


def test_parse_failure(record_n2):
    """Invalid syntax fails."""
    assert not verify_topology_enumeration("not a list", record_n2)


def test_wrong_format(record_n2):
    """Wrong format fails."""
    assert not verify_topology_enumeration("[(0, 1, 0)]", record_n2)  # Wrong length
    assert not verify_topology_enumeration("[[0, 1, 0, 0]]", record_n2)  # Lists not tuples


def test_length_mismatch(record_n2):
    """Length mismatch fails."""
    output = "[(0, 1, 0, 0), (1, 0, 0, 0)]"
    assert not verify_topology_enumeration(output, record_n2)


def test_label_set_mismatch(record_n3):
    """Wrong label set fails."""
    output = "[(0, 0, 1, 1), (0, 0, 1, 1), (0, 0, 1, 1), (0, 0, 1, 1)]"  # Missing label 2
    result = verify_topology_enumeration(output, record_n3, return_diff=True)
    assert not result["passed"]
    assert 2 in result["details"]["label_set_diff"]["missing_labels"]


def test_range_validation(record_n2):
    """Out-of-range values fail."""
    output = "[(2, 0, 0, 0)]"
    assert not verify_topology_enumeration(output, record_n2)


def test_missing_tuples(record_n2):
    """Missing tuples detected in diff."""
    output = "[(1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0)]"
    result = verify_topology_enumeration(output, record_n2, return_diff=True)
    assert not result["passed"]
    assert len(result["missing"]) == 4
    assert [0, 0, 0, 1] in result["missing"]


def test_diff_diagnostics(record_n2):
    """Diff mode provides full diagnostics."""
    output = "[(0, 1, 0, 0)]"
    result = verify_topology_enumeration(output, record_n2, return_diff=True)
    assert not result["passed"]
    assert "length_mismatch" in result["details"]
    assert result["details"]["length_mismatch"]["expected"] == 7
    assert len(result["missing"]) == 6

