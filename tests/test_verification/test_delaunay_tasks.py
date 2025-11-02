"""Tests for Delaunay triangulation verification."""

import pytest

from visual_geometry_bench.datagen.delaunay_tasks import generate_dataset_record
from visual_geometry_bench.verification.delaunay_tasks import verify_delaunay_triangulation


@pytest.fixture
def record_small():
    """Fixture for small triangulation (8 points)."""
    return generate_dataset_record(
        datagen_args={"num_points": 8, "seed": 42}
    )


@pytest.fixture
def record_medium():
    """Fixture for medium triangulation (12 points)."""
    return generate_dataset_record(
        datagen_args={"num_points": 12, "seed": 123}
    )


# Pass cases


def test_exact_match(record_small):
    """Exact match with ground truth passes."""
    gt = record_small["ground_truth"]
    output = str(gt)
    assert verify_delaunay_triangulation(output, record_small)


def test_exact_match_json_format(record_small):
    """JSON-formatted output passes."""
    import json
    gt = record_small["ground_truth"]
    output = json.dumps(gt)
    assert verify_delaunay_triangulation(output, record_small)


def test_unsorted_triangles_canonicalised(record_small):
    """Unsorted triangles are canonicalised before comparison."""
    gt = record_small["ground_truth"]
    # Reverse order of triangles
    output = str(list(reversed(gt)))
    assert verify_delaunay_triangulation(output, record_small)


def test_unsorted_indices_within_triangle(record_small):
    """Unsorted indices within triangles are canonicalised."""
    gt = record_small["ground_truth"]
    # Reverse each triangle's indices
    scrambled = [[tri[2], tri[0], tri[1]] for tri in gt]
    output = str(scrambled)
    assert verify_delaunay_triangulation(output, record_small)


def test_both_unsorted(record_small):
    """Both triangle order and indices unsorted are canonicalised."""
    gt = record_small["ground_truth"]
    scrambled = [[tri[2], tri[0], tri[1]] for tri in reversed(gt)]
    output = str(scrambled)
    assert verify_delaunay_triangulation(output, record_small)


# Parse failure cases


def test_parse_failure_invalid_json(record_small):
    """Invalid JSON/Python literal fails."""
    assert not verify_delaunay_triangulation("not valid json", record_small)


def test_parse_failure_not_list(record_small):
    """Non-list output fails."""
    output = '{"triangles": [[0, 1, 2]]}'
    assert not verify_delaunay_triangulation(output, record_small)


def test_parse_failure_string(record_small):
    """String output fails."""
    assert not verify_delaunay_triangulation('"some string"', record_small)


# Format validation failures


def test_format_triangle_not_list(record_small):
    """Triangle as tuple instead of list fails."""
    output = "[(0, 1, 2), [1, 2, 3]]"
    assert not verify_delaunay_triangulation(output, record_small)


def test_format_triangle_wrong_length(record_small):
    """Triangle with wrong number of indices fails."""
    output = "[[0, 1], [1, 2, 3]]"
    assert not verify_delaunay_triangulation(output, record_small)


def test_format_invalid_index_type(record_small):
    """Non-integer indices fail."""
    output = "[[0, 1, 2.5], [1, 2, 3]]"
    assert not verify_delaunay_triangulation(output, record_small)


def test_format_negative_index(record_small):
    """Negative indices fail."""
    output = "[[0, 1, -1], [1, 2, 3]]"
    assert not verify_delaunay_triangulation(output, record_small)


# Content mismatch cases


def test_missing_triangle(record_small):
    """Missing triangle fails."""
    gt = record_small["ground_truth"]
    output = str(gt[:-1])  # Drop last triangle
    assert not verify_delaunay_triangulation(output, record_small)


def test_extra_triangle(record_small):
    """Extra triangle fails."""
    gt = record_small["ground_truth"]
    extra = gt + [[0, 1, 2]]
    output = str(extra)
    assert not verify_delaunay_triangulation(output, record_small)


def test_wrong_triangle(record_small):
    """Incorrect triangle fails."""
    gt = record_small["ground_truth"]
    if len(gt) > 0:
        wrong = gt.copy()
        wrong[0] = [0, 1, 2]  # Arbitrary replacement
        output = str(wrong)
        result = verify_delaunay_triangulation(output, record_small)
        # Only fails if [0,1,2] wasn't already in ground truth
        if [0, 1, 2] not in gt:
            assert not result


def test_empty_output_fails(record_small):
    """Empty triangulation fails when ground truth is non-empty."""
    output = "[]"
    result = verify_delaunay_triangulation(output, record_small)
    # Only fails if ground truth is non-empty
    if len(record_small["ground_truth"]) > 0:
        assert not result


# Diagnostic mode tests


def test_diff_mode_exact_match(record_small):
    """Diff mode returns passed=True for exact match."""
    gt = record_small["ground_truth"]
    output = str(gt)
    result = verify_delaunay_triangulation(output, record_small, return_diff=True)
    
    assert isinstance(result, dict)
    assert result["passed"] is True
    assert result["missing"] == []
    assert result["extra"] == []
    assert result["errors"] == []


def test_diff_mode_parse_failure(record_small):
    """Diff mode reports parse failure."""
    result = verify_delaunay_triangulation(
        "invalid", record_small, return_diff=True
    )
    
    assert isinstance(result, dict)
    assert result["passed"] is False
    assert "parse_failure" in result["errors"]


def test_diff_mode_missing_triangle(record_small):
    """Diff mode reports missing triangles."""
    gt = record_small["ground_truth"]
    if len(gt) > 1:
        output = str(gt[:-1])  # Drop last triangle
        result = verify_delaunay_triangulation(
            output, record_small, return_diff=True
        )
        
        assert isinstance(result, dict)
        assert result["passed"] is False
        assert len(result["missing"]) == 1
        assert result["missing"][0] == gt[-1]
        assert result["extra"] == []


def test_diff_mode_extra_triangle(record_small):
    """Diff mode reports extra triangles."""
    gt = record_small["ground_truth"]
    extra_tri = [0, 1, 2]
    if extra_tri not in gt:
        extra = gt + [extra_tri]
        output = str(extra)
        result = verify_delaunay_triangulation(
            output, record_small, return_diff=True
        )
        
        assert isinstance(result, dict)
        assert result["passed"] is False
        assert result["missing"] == []
        assert extra_tri in result["extra"]


def test_diff_mode_format_error(record_small):
    """Diff mode reports format validation errors."""
    output = "[[0, 1]]"  # Wrong length
    result = verify_delaunay_triangulation(
        output, record_small, return_diff=True
    )
    
    assert isinstance(result, dict)
    assert result["passed"] is False
    assert len(result["errors"]) > 0
    assert "wrong_length" in result["errors"][0]


# Edge cases


def test_single_triangle():
    """Single triangle (3 points) verifies correctly."""
    record = generate_dataset_record(
        datagen_args={"num_points": 3, "seed": 999}
    )
    gt = record["ground_truth"]
    output = str(gt)
    assert verify_delaunay_triangulation(output, record)
    assert len(gt) == 1
    assert len(gt[0]) == 3


def test_deterministic_verification(record_medium):
    """Verification is deterministic."""
    gt = record_medium["ground_truth"]
    output = str(gt)
    
    result1 = verify_delaunay_triangulation(output, record_medium)
    result2 = verify_delaunay_triangulation(output, record_medium)
    assert result1 == result2
    
    diff1 = verify_delaunay_triangulation(output, record_medium, return_diff=True)
    diff2 = verify_delaunay_triangulation(output, record_medium, return_diff=True)
    assert diff1 == diff2
