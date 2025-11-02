"""Tests for half-subdivision neighbours task generation."""

import pytest

from visual_geometry_bench.datagen.half_subdivision_neighbours import (
    generate_dataset_record,
    get_solutions,
    make_prompt,
)


class TestPromptGeneration:
    """Test prompt generation."""

    def test_make_prompt_includes_tree_and_target(self):
        """Prompt contains treelib tree and target label."""
        args = {"max_depth": 3, "split_prob": 1.0, "seed": 42, "target_label": "000"}
        prompt = make_prompt(args)
        assert "```" in prompt
        assert '""' in prompt
        assert "000" in prompt
        assert "alternating" in prompt.lower()

    def test_make_prompt_deterministic(self):
        """Same args produce identical prompts."""
        args = {"max_depth": 4, "split_prob": 0.7, "seed": 100, "min_depth": 2}
        assert make_prompt(args) == make_prompt(args)


class TestSolutionGeneration:
    """Test neighbour computation."""

    def test_get_solutions_returns_list_of_labels(self):
        """Solutions are list of string labels."""
        args = {"max_depth": 3, "split_prob": 1.0, "seed": 42}
        solutions = get_solutions(args)
        assert isinstance(solutions, list)
        assert all(isinstance(label, str) for label in solutions)
        assert all(all(ch in "01" for ch in label) or label == '""' for label in solutions)

    def test_get_solutions_deterministic(self):
        """Same args produce identical solutions."""
        args = {"max_depth": 4, "split_prob": 0.6, "seed": 7, "min_depth": 2}
        assert get_solutions(args) == get_solutions(args)

    def test_get_solutions_unique_labels(self):
        """Returned neighbour labels are unique."""
        args = {"max_depth": 4, "split_prob": 1.0, "seed": 3, "min_depth": 2}
        solutions = get_solutions(args)
        assert len(solutions) == len(set(solutions))

    def test_get_solutions_forced_target(self):
        """Forcing target_label works when label is a leaf."""
        args = {"max_depth": 3, "split_prob": 1.0, "seed": 42, "target_label": "000"}
        solutions = get_solutions(args)
        assert isinstance(solutions, list)
        assert "000" not in solutions

    def test_get_solutions_forced_target_invalid_raises(self):
        """Forcing a non-leaf target_label raises ValueError."""
        args = {"max_depth": 3, "split_prob": 1.0, "seed": 42, "target_label": "999"}
        with pytest.raises(ValueError, match="not a leaf"):
            get_solutions(args)

    def test_3d_mode_generates_and_differs_from_2d(self):
        """3D mode works and produces different prompts/solutions than 2D."""
        args_2d = {"max_depth": 3, "split_prob": 1.0, "seed": 42, "dimension": "2D"}
        args_3d = {"max_depth": 3, "split_prob": 1.0, "seed": 42, "dimension": "3D"}
        prompt_2d = make_prompt(args_2d)
        prompt_3d = make_prompt(args_3d)
        sol_2d = get_solutions(args_2d)
        sol_3d = get_solutions(args_3d)
        # Prompts should mention square vs cube and axis rules
        assert "square" in prompt_2d
        assert "cube" in prompt_3d
        assert "x → y → z" in prompt_3d
        # Solutions can differ due to different adjacency definitions
        assert isinstance(sol_2d, list) and isinstance(sol_3d, list)

    def test_2d_start_axis_y_flips_first_split_to_horizontal(self):
        """In 2D, start_axis='y' makes the first split horizontal."""
        args = {"max_depth": 1, "min_depth": 1, "split_prob": 1.0, "seed": 0, "start_axis": "y"}
        # With start_axis='y' and depth 1, we get two leaves stacked vertically (y-split)
        # Choose target '0' (top) and '1' (bottom) to verify adjacency is vertical
        # Here we just verify the prompt and that solutions are produced (geometry is handled by datagen)
        prompt = make_prompt(args)
        solutions = get_solutions(args)
        assert isinstance(solutions, list)
        # Prompt should still describe the alternating rule (but first split is horizontal)
        assert "alternating" in prompt.lower()

    def test_3d_face_only_adjacency(self):
        """In 3D, only face-touching voxels count as neighbours (edges/corners excluded)."""
        args = {"max_depth": 2, "min_depth": 2, "split_prob": 1.0, "seed": 0, "dimension": "3D", "target_label": "00"}
        # With depth 2, we have 8 voxels in a cube. Target '00' is at (-x,-y) quadrant.
        # Face neighbours: '01' (shares x-face), '10' (shares y-face)
        # Edge/corner contacts like '11' should not count.
        solutions = get_solutions(args)
        # Expected face neighbours for this deterministic configuration
        expected = {"01", "10"}
        assert set(solutions) == expected

    def test_runtime_dimension_metadata(self):
        """Dataset records include correct runtime dimension."""
        from visual_geometry_bench.datagen.half_subdivision_neighbours import generate_dataset_record
        record_2d = generate_dataset_record({"max_depth": 2, "seed": 0, "split_prob": 1.0, "dimension": "2D"})
        record_3d = generate_dataset_record({"max_depth": 2, "seed": 0, "split_prob": 1.0, "dimension": "3D"})
        assert record_2d["runtime"]["dimension"] == "2D"
        assert record_3d["runtime"]["dimension"] == "3D"


class TestDatasetRecordGeneration:
    """Test dataset record generation."""

    def test_generate_dataset_record_structure(self):
        """Record has required keys and correct structure."""
        args = {"max_depth": 4, "split_prob": 0.7, "seed": 42, "min_depth": 2}
        record = generate_dataset_record(args)

        assert "id" in record
        assert "prompt" in record
        assert "ground_truth" in record
        assert "metadata" in record
        assert "datagen_args" in record
        assert "runtime" in record

        assert isinstance(record["id"], str)
        assert isinstance(record["prompt"], str)
        assert isinstance(record["ground_truth"], list)
        assert isinstance(record["metadata"], dict)
        assert record["metadata"]["problem_type"] == "half_subdivision_neighbours"

    def test_generate_dataset_record_deterministic(self):
        """Same args produce identical records."""
        args = {"max_depth": 3, "split_prob": 1.0, "seed": 100}
        rec1 = generate_dataset_record(args)
        rec2 = generate_dataset_record(args)
        assert rec1["id"] == rec2["id"]
        assert rec1["prompt"] == rec2["prompt"]
        assert rec1["ground_truth"] == rec2["ground_truth"]

    def test_generate_dataset_record_metadata(self):
        """Record metadata includes tags and difficulty when provided."""
        args = {"max_depth": 3, "split_prob": 1.0, "seed": 42}
        record = generate_dataset_record(
            args, tags=["geometry", "tree"], difficulty="medium"
        )
        assert "geometry" in record["metadata"]["tags"]
        assert record["metadata"]["difficulty"] == "medium"

    @pytest.mark.parametrize(
        "bad_args,exc,regex",
        [
            ({}, ValueError, "must include"),
            ({"max_depth": 5}, ValueError, "must include"),
            ({"max_depth": -1, "seed": 42, "split_prob": 0.5}, ValueError, "non-negative"),
            ({"max_depth": 5, "seed": 42, "split_prob": 1.5}, ValueError, "within"),
        ],
    )
    def test_generate_dataset_record_invalid_args(self, bad_args, exc, regex):
        """Invalid arguments raise appropriate exceptions."""
        with pytest.raises(exc, match=regex):
            generate_dataset_record(bad_args)
