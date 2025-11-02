"""Tests for two-segment datagen utilities."""

import pytest

from visual_geometry_bench.datagen.two_segments import generate_dataset_record
from visual_geometry_bench.verification.two_segments import classify_segments


_SAMPLE_CASES = {
    "ts_four_triangles": (
        {"triangle": 4},
        (
            ((0.0, 0.0), (1.0, 1.0)),
            ((0.0, 1.0), (1.0, 0.0)),
        ),
    ),
    "ts_three_triangles": (
        {"triangle": 3},
        (
            ((0.0, 0.0), (0.25, 1.0)),
            ((0.0, 0.0), (1.0, 1.0)),
        ),
    ),
    "ts_three_triangles_one_quadrilateral": (
        {"triangle": 3, "quadrilateral": 1},
        (
            ((0.0, 0.0), (0.25, 1.0)),
            ((0.0, 1.0), (1.0, 0.0)),
        ),
    ),
    "ts_three_triangles_one_pentagon": (
        {"triangle": 3, "pentagon": 1},
        (
            ((0.0, 0.0), (0.25, 1.0)),
            ((0.0, 1.0), (0.25, 0.0)),
        ),
    ),
    "ts_two_triangles_two_quadrilaterals": (
        {"triangle": 2, "quadrilateral": 2},
        (
            ((0.0, 0.0), (0.25, 1.0)),
            ((0.0, 0.25), (1.0, 0.0)),
        ),
    ),
    "ts_two_triangles_one_quadrilateral": (
        {"triangle": 2, "quadrilateral": 1},
        (
            ((0.0, 0.0), (0.25, 1.0)),
            ((0.0, 0.0), (0.5, 1.0)),
        ),
    ),
    "ts_two_triangles_one_pentagon": (
        {"triangle": 2, "pentagon": 1},
        (
            ((0.0, 0.0), (0.25, 1.0)),
            ((0.25, 0.0), (1.0, 0.25)),
        ),
    ),
    "ts_two_triangles_one_hexagon": (
        {"triangle": 2, "hexagon": 1},
        (
            ((0.0, 0.25), (0.25, 0.0)),
            ((0.0, 0.5), (0.25, 1.0)),
        ),
    ),
    "ts_two_triangles_two_pentagons": (
        {"triangle": 2, "pentagon": 2},
        (
            ((0.0, 0.25), (1.0, 0.5)),
            ((0.0, 0.5), (1.0, 0.25)),
        ),
    ),
    "ts_one_triangle_one_quadrilateral_one_pentagon": (
        {"triangle": 1, "quadrilateral": 1, "pentagon": 1},
        (
            ((0.0, 0.25), (0.25, 0.0)),
            ((0.0, 0.5), (0.5, 0.0)),
        ),
    ),
    "ts_one_triangle_three_quadrilaterals": (
        {"triangle": 1, "quadrilateral": 3},
        (
            ((0.0, 0.0), (0.25, 1.0)),
            ((0.0, 0.25), (1.0, 0.25)),
        ),
    ),
    "ts_three_quadrilaterals": (
        {"quadrilateral": 3},
        (
            ((0.0, 0.25), (1.0, 0.25)),
            ((0.0, 0.5), (1.0, 0.5)),
        ),
    ),
    "ts_four_quadrilaterals": (
        {"quadrilateral": 4},
        (
            ((0.0, 0.25), (1.0, 0.25)),
            ((0.25, 0.0), (0.25, 1.0)),
        ),
    ),
}


def test_generate_dataset_record_structure():
    counts, _ = _SAMPLE_CASES["ts_one_triangle_one_quadrilateral_one_pentagon"]
    datagen_args = {"counts": counts}
    record = generate_dataset_record(datagen_args=datagen_args, tags=["two_segments"])

    assert record["metadata"]["problem_type"] == "two_segments"
    assert record["metadata"]["tags"] == ["two_segments"]
    assert record["datagen_args"]["square"] == "unit"
    assert record["datagen_args"]["corners"] == [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]

    gt_counts = {item["shape"]: item["count"] for item in record["ground_truth"]}
    assert gt_counts == {shape: int(total) for shape, total in counts.items()}


def test_generate_dataset_record_requires_counts():
    with pytest.raises(AssertionError):
        generate_dataset_record(datagen_args={})


def test_random_square_respects_seed():
    counts = {"triangle": 4}
    record_a = generate_dataset_record({"counts": counts, "square": "random", "square_seed": 123})
    record_b = generate_dataset_record({"counts": counts, "square": "random", "square_seed": 123})
    assert record_a["datagen_args"]["square"] == "random"
    assert record_a["datagen_args"]["corners"] == record_b["datagen_args"]["corners"]


def test_explicit_square_corners_preserved():
    counts = {"triangle": 4}
    corners = [[0.0, 0.0], [2.0, 0.0], [2.0, 2.0], [0.0, 2.0]]
    record = generate_dataset_record({"counts": counts, "square": corners})
    assert record["datagen_args"]["square"] == "explicit"
    assert record["datagen_args"]["corners"] == corners


@pytest.mark.parametrize("case_id", sorted(_SAMPLE_CASES.keys()))
def test_classify_segments_matches_expected_counts(case_id):
    counts, segments = _SAMPLE_CASES[case_id]
    measured = classify_segments(segments)
    assert measured == counts
