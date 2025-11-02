"""Tests for convex hull ordering task generation."""

import json

import numpy as np
import pytest
from scipy.spatial import ConvexHull as SciPyConvexHull

from visual_geometry_bench.datagen.convex_hull_tasks import (
    _compute_convex_hull,
    _gen_convex_points,
    _hull_to_canonical_indices,
    _to_points,
    generate_dataset_record,
    get_solutions,
    make_prompt,
)


class TestPointGeneration:
    """Test random point generation."""

    @pytest.mark.parametrize(
        "num_points,seed",
        [(5, 42), (10, 123), (50, 99)],
    )
    def test_gen_convex_points_shape_and_bounds(self, num_points, seed):
        """Generated points have correct count and lie in [0,1)² and are finite."""
        points = _gen_convex_points(num_points=num_points, random_seed=seed)
        assert len(points) == num_points
        for x, y in points:
            assert 0.0 <= x < 1.0
            assert 0.0 <= y < 1.0
            assert np.isfinite(x)
            assert np.isfinite(y)

    def test_gen_convex_points_deterministic_by_seed(self):
        points1 = _gen_convex_points(num_points=10, random_seed=123)
        points2 = _gen_convex_points(num_points=10, random_seed=123)
        assert points1 == points2

    def test_gen_convex_points_varies_with_seed(self):
        assert _gen_convex_points(10, 1) != _gen_convex_points(10, 2)


class TestToPoints:
    """Test _to_points argument parsing and determinism."""

    @pytest.mark.parametrize("args,ok", [
        ({"num_points": 5, "seed": 42}, True),
        ({"num_points": 10, "seed": 123}, True),
    ])
    def test_to_points_valid_args(self, args, ok):
        points = _to_points(args)
        assert len(points) == args["num_points"]

    def test_to_points_deterministic(self):
        args = {"num_points": 10, "seed": 123}
        assert _to_points(args) == _to_points(args)

    @pytest.mark.parametrize("bad_args,exc,regex", [
        ({"seed": 42}, KeyError, None),
        ({"num_points": 5}, KeyError, None),
        ({"num_points": 2, "seed": 42}, ValueError, "convex sampling requires num_points >= 3"),
        ({"num_points": 0, "seed": 42}, ValueError, "convex sampling requires num_points >= 3"),
    ])
    def test_to_points_invalid_args(self, bad_args, exc, regex):
        with pytest.raises(exc, match=regex):
            _to_points(bad_args)


class TestComputeConvexHull:
    """Test convex hull computation."""

    @pytest.mark.parametrize(
        "points,expected_len",
        [
            ([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)], 4),
            ([(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)], 3),
            ([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.5, 0.5)], 4),
        ],
    )
    def test_compute_convex_hull_valid_cases(self, points, expected_len):
        hull = _compute_convex_hull(points)
        assert hull is not None
        assert isinstance(hull, SciPyConvexHull)
        assert len(hull.vertices) == expected_len

    @pytest.mark.parametrize(
        "points",
        [
            [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)],
            [(0.0, 0.0), (1.0, 0.0), (0.5, 1e-15)],
        ],
    )
    def test_compute_convex_hull_degenerate_returns_none(self, points):
        hull = _compute_convex_hull(points)
        assert hull is None


class TestHullToCanonicalIndices:
    """Test canonical index rotation."""

    @pytest.mark.parametrize(
        "points",
        [
            np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]),
            np.array([[0.5, 0.5], [0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]),
            np.array([[1.0, 0.0], [0.0, 0.0], [0.0, 1.0], [1.0, 1.0]]),
        ],
    )
    def test_hull_to_canonical_indices(self, points):
        hull = SciPyConvexHull(points)
        canonical = _hull_to_canonical_indices(hull)
        assert canonical[0] == min(canonical)
        assert set(canonical) == set(hull.vertices.tolist())


class TestMakePrompt:
    """Test prompt generation."""

    def test_make_prompt_contains_required_text_and_points(self):
        datagen_args = {"num_points": 4, "seed": 42}
        points = _to_points(datagen_args)
        prompt = make_prompt(datagen_args)

        # Structure/phrases
        for phrase in [
            "2D points",
            "indices correspond to the order shown",
            "convex hull vertices",
            "counterclockwise order",
            "smallest index",
            "Python list of integers only",
        ]:
            assert phrase in prompt

        # Point coordinates appear
        for x, y in points:
            assert str(float(x)) in prompt
            assert str(float(y)) in prompt

    def test_make_prompt_deterministic(self):
        args = {"num_points": 5, "seed": 999}
        assert make_prompt(args) == make_prompt(args)


class TestGetSolutions:
    """Test solution computation."""

    def test_get_solutions_basic_properties(self):
        datagen_args = {"num_points": 20, "seed": 123}
        solutions = get_solutions(datagen_args)
        assert isinstance(solutions, list)
        assert all(isinstance(idx, int) for idx in solutions)
        assert solutions[0] == min(solutions)
        assert len(solutions) == len(set(solutions))
        assert all(0 <= idx < datagen_args["num_points"] for idx in solutions)
        assert len(solutions) >= 3


class TestGenerateDatasetRecord:
    """Test dataset record generation."""

    def test_generate_dataset_record_basics_and_metadata(self):
        datagen_args = {"num_points": 10, "seed": 42}
        record = generate_dataset_record(
            datagen_args=datagen_args,
            tags=["geometry", "convex_hull", "geometry"],
            difficulty="medium",
            requires_visual=True,
        )

        # Structure
        for key in ["id", "prompt", "ground_truth", "metadata", "datagen_args"]:
            assert key in record

        # Metadata
        assert record["metadata"]["problem_type"] == "convex_hull_ordering"
        assert set(record["metadata"]["tags"]) == {"geometry", "convex_hull"}
        assert record["metadata"]["difficulty"] == "medium"
        assert record["metadata"]["requires_visual"] is True

        # Datagen args preserved
        assert record["datagen_args"] == datagen_args

        # Ground truth is list of ints
        assert isinstance(record["ground_truth"], list)
        assert all(isinstance(idx, int) for idx in record["ground_truth"])

    def test_generate_dataset_record_serialization_and_id_stability(self):
        args = {"num_points": 8, "seed": 123}
        rec1 = generate_dataset_record(datagen_args=args, tags=["test"])
        rec2 = generate_dataset_record(datagen_args=args, tags=["test"])

        # Deterministic ID
        assert rec1["id"] == rec2["id"]
        assert len(rec1["id"]) == 8

        # JSON-serializable and round-trips
        parsed = json.loads(json.dumps(rec1, ensure_ascii=False))
        assert parsed["id"] == rec1["id"]
        assert parsed["ground_truth"] == rec1["ground_truth"]

    def test_generate_dataset_record_missing_args_raise(self):
        with pytest.raises(AssertionError, match="must include 'num_points' and 'seed'"):
            generate_dataset_record(datagen_args={"seed": 42})
        with pytest.raises(AssertionError, match="must include 'num_points' and 'seed'"):
            generate_dataset_record(datagen_args={"num_points": 10})

    def test_generate_dataset_record_custom_id_and_defaults(self):
        datagen_args = {"num_points": 5, "seed": 42}
        custom_id = "custom_test_id_123"
        record = generate_dataset_record(datagen_args=datagen_args, record_id=custom_id)
        assert record["id"] == custom_id

        record_default = generate_dataset_record(datagen_args=datagen_args)
        assert record_default["metadata"]["tags"] == []
        assert record_default["metadata"]["difficulty"] == ""
        assert record_default["metadata"]["requires_visual"] is True

