"""Tests for Delaunay triangulation task generation."""

import json

import numpy as np
import pytest
from scipy.spatial import Delaunay as SciPyDelaunay

from visual_geometry_bench.datagen.delaunay_tasks import (
    _compute_delaunay_triangulation,
    _to_points,
    generate_dataset_record,
    get_solutions,
    make_prompt,
    sample_unique_delaunay_points,
)


class TestPointSampling:
    """Test general-position point sampling."""

    @pytest.mark.parametrize(
        "n,seed",
        [(8, 42), (12, 123), (20, 99)],
    )
    def test_sample_unique_delaunay_points_shape_and_bounds(self, n, seed):
        """Sampled points have correct count, lie in [0,1)², and are finite."""
        pts = sample_unique_delaunay_points(n, seed=seed)
        assert pts.shape == (n, 2)
        assert np.all((pts >= 0.0) & (pts < 1.0))
        assert np.all(np.isfinite(pts))

    def test_sample_unique_delaunay_points_deterministic(self):
        """Same seed produces identical point sets."""
        pts1 = sample_unique_delaunay_points(10, seed=123)
        pts2 = sample_unique_delaunay_points(10, seed=123)
        np.testing.assert_array_equal(pts1, pts2)

    def test_sample_unique_delaunay_points_varies_with_seed(self):
        """Different seeds produce different point sets."""
        pts1 = sample_unique_delaunay_points(10, seed=1)
        pts2 = sample_unique_delaunay_points(10, seed=2)
        assert not np.allclose(pts1, pts2)

    def test_sample_unique_delaunay_points_rejects_too_few(self):
        """Sampling fewer than 3 points raises ValueError."""
        with pytest.raises(ValueError, match="at least 3 points"):
            sample_unique_delaunay_points(2, seed=42)


class TestToPoints:
    """Test _to_points argument parsing and validation."""

    @pytest.mark.parametrize(
        "args",
        [
            {"num_points": 8, "seed": 42},
            {"num_points": 15, "seed": 999},
        ],
    )
    def test_to_points_valid_args(self, args):
        """Valid arguments produce correct number of points."""
        points = _to_points(args)
        assert len(points) == args["num_points"]
        assert all(isinstance(pt, tuple) and len(pt) == 2 for pt in points)

    def test_to_points_deterministic(self):
        """Same arguments produce identical point lists."""
        args = {"num_points": 10, "seed": 123}
        assert _to_points(args) == _to_points(args)

    @pytest.mark.parametrize(
        "bad_args,exc,regex",
        [
            ({"seed": 42}, ValueError, "must contain"),
            ({"num_points": 10}, ValueError, "must contain"),
            ({"num_points": 2, "seed": 42}, ValueError, "at least 3"),
        ],
    )
    def test_to_points_invalid_args(self, bad_args, exc, regex):
        """Invalid arguments raise appropriate exceptions."""
        with pytest.raises(exc, match=regex):
            _to_points(bad_args)


class TestComputeDelaunayTriangulation:
    """Test Delaunay triangulation computation and canonicalisation."""

    @pytest.mark.parametrize(
        "points,expected_min_triangles",
        [
            ([(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)], 1),
            ([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)], 2),
        ],
    )
    def test_compute_delaunay_triangulation_valid(self, points, expected_min_triangles):
        """Valid point sets produce correct triangulation structure."""
        triangles = _compute_delaunay_triangulation(points)
        assert isinstance(triangles, list)
        assert len(triangles) >= expected_min_triangles
        for tri in triangles:
            assert isinstance(tri, list)
            assert len(tri) == 3
            assert all(isinstance(idx, int) for idx in tri)
            assert tri == sorted(tri)  # Each triangle sorted
        # List of triangles sorted lexicographically
        assert triangles == sorted(triangles)

    def test_compute_delaunay_triangulation_deterministic(self):
        """Same points produce identical triangulation."""
        points = [(0.1, 0.2), (0.8, 0.3), (0.5, 0.9), (0.2, 0.7)]
        tri1 = _compute_delaunay_triangulation(points)
        tri2 = _compute_delaunay_triangulation(points)
        assert tri1 == tri2


class TestMakePrompt:
    """Test prompt generation."""

    def test_make_prompt_contains_required_text(self):
        """Prompt contains all required instructions and point data."""
        datagen_args = {"num_points": 8, "seed": 42}
        points = _to_points(datagen_args)
        display_points = np.round(points, 3)
        prompt = make_prompt(datagen_args)

        # Required phrases
        for phrase in [
            "2D points",
            "general position",
            "indices correspond to the order shown",
            "Delaunay triangulation",
            "list of triangles",
            "three point indices",
            "sorted in ascending order",
            "Python list of lists of integers only",
        ]:
            assert phrase in prompt

        # Point coordinates appear
        for x, y in display_points:
            assert str(float(x)) in prompt
            assert str(float(y)) in prompt

    def test_make_prompt_deterministic(self):
        """Same arguments produce identical prompts."""
        args = {"num_points": 10, "seed": 999}
        assert make_prompt(args) == make_prompt(args)


class TestGetSolutions:
    """Test solution computation."""

    def test_get_solutions_basic_properties(self):
        """Solutions have correct structure and properties."""
        datagen_args = {"num_points": 12, "seed": 123}
        solutions = get_solutions(datagen_args)

        assert isinstance(solutions, list)
        assert len(solutions) >= 1  # At least one triangle

        for tri in solutions:
            assert isinstance(tri, list)
            assert len(tri) == 3
            assert all(isinstance(idx, int) for idx in tri)
            assert tri == sorted(tri)  # Each triangle sorted
            assert all(0 <= idx < datagen_args["num_points"] for idx in tri)

        # Lexicographically sorted
        assert solutions == sorted(solutions)

    def test_get_solutions_deterministic(self):
        """Same arguments produce identical solutions."""
        args = {"num_points": 10, "seed": 42}
        assert get_solutions(args) == get_solutions(args)

    def test_get_solutions_matches_scipy(self):
        """Solutions match scipy.spatial.Delaunay output."""
        datagen_args = {"num_points": 8, "seed": 7}
        points = _to_points(datagen_args)
        solutions = get_solutions(datagen_args)

        # Compute reference triangulation
        point_array = np.array(points, dtype=float)
        tri = SciPyDelaunay(point_array)
        expected = sorted([sorted(map(int, simplex)) for simplex in tri.simplices])

        assert solutions == expected


class TestGenerateDatasetRecord:
    """Test dataset record generation."""

    def test_generate_dataset_record_structure(self):
        """Record has all required fields with correct types."""
        datagen_args = {"num_points": 10, "seed": 42}
        record = generate_dataset_record(datagen_args)

        # Required keys
        for key in ["id", "prompt", "ground_truth", "metadata", "datagen_args"]:
            assert key in record

        # Metadata structure
        assert record["metadata"]["problem_type"] == "delaunay_triangulation"
        assert "tags" in record["metadata"]
        assert "difficulty" in record["metadata"]
        assert "requires_visual" in record["metadata"]

        # Datagen args preserved
        assert record["datagen_args"] == datagen_args

        # Ground truth is list of triangles
        assert isinstance(record["ground_truth"], list)
        for tri in record["ground_truth"]:
            assert isinstance(tri, list)
            assert len(tri) == 3
            assert all(isinstance(idx, int) for idx in tri)

    def test_generate_dataset_record_metadata_override(self):
        """Metadata can be overridden."""
        datagen_args = {"num_points": 8, "seed": 123}
        custom_metadata = {
            "tags": ["custom", "test"],
            "difficulty": "hard",
            "requires_visual": True,
        }
        record = generate_dataset_record(datagen_args, metadata=custom_metadata)

        assert record["metadata"]["tags"] == ["custom", "test"]
        assert record["metadata"]["difficulty"] == "hard"
        assert record["metadata"]["requires_visual"] is True

    def test_generate_dataset_record_id_stability(self):
        """Same arguments produce same ID."""
        args = {"num_points": 8, "seed": 123}
        rec1 = generate_dataset_record(args)
        rec2 = generate_dataset_record(args)

        assert rec1["id"] == rec2["id"]
        assert len(rec1["id"]) == 8  # Default hash prefix length

    def test_generate_dataset_record_json_serializable(self):
        """Record is JSON-serializable and round-trips correctly."""
        args = {"num_points": 10, "seed": 42}
        record = generate_dataset_record(args)

        serialized = json.dumps(record, ensure_ascii=False)
        parsed = json.loads(serialized)

        assert parsed["id"] == record["id"]
        assert parsed["ground_truth"] == record["ground_truth"]
        assert parsed["datagen_args"] == record["datagen_args"]

    def test_generate_dataset_record_deterministic(self):
        """Same arguments produce identical records."""
        args = {"num_points": 12, "seed": 999}
        rec1 = generate_dataset_record(args)
        rec2 = generate_dataset_record(args)

        assert rec1 == rec2
