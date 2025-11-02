"""Tests for Shikaku datagen helpers."""

from __future__ import annotations

import json

import pytest

from visual_geometry_bench.datagen.shikaku_tasks import (
    generate_dataset_record,
    get_solutions,
    make_prompt,
)


@pytest.fixture()
def tiny_dataset(tmp_path):
    puzzle = {
        "id": "2x2:test",
        "width": 2,
        "height": 2,
        "numbers": [[4, 0], [0, 0]],
        "solution_rectangles": [
            {"id": 0, "top": 0, "left": 0, "height": 2, "width": 2},
        ],
        "rect_version": "unit-test",
    }
    dataset_path = tmp_path / "rectangles.json"
    dataset_path.write_text(json.dumps([puzzle]), encoding="utf-8")
    return dataset_path, puzzle


def test_make_prompt_contains_bounding_box_instruction(tiny_dataset):
    dataset_path, _ = tiny_dataset
    datagen_args = {
        "dataset_path": str(dataset_path),
        "puzzle_index": 0,
    }
    prompt = make_prompt(datagen_args)
    assert "list of bounding boxes" in prompt
    assert "[left_col, top_row, right_col, bottom_row]" in prompt
    # Grid should appear verbatim
    assert "4 0" in prompt


def test_get_solutions_returns_bounding_boxes(tiny_dataset):
    dataset_path, _ = tiny_dataset
    datagen_args = {
        "dataset_path": str(dataset_path),
        "puzzle_index": 0,
    }
    solution = get_solutions(datagen_args)
    assert solution == [[0, 0, 1, 1]]


def test_generate_dataset_record_structure_and_determinism(tiny_dataset):
    dataset_path, puzzle = tiny_dataset
    datagen_args = {
        "dataset_path": str(dataset_path),
        "puzzle_index": 0,
    }

    record_a = generate_dataset_record(datagen_args)
    record_b = generate_dataset_record(datagen_args)

    # Required keys
    for key in ("id", "prompt", "ground_truth", "metadata", "datagen_args"):
        assert key in record_a

    assert record_a == record_b  # deterministic
    assert record_a["ground_truth"] == [[0, 0, 1, 1]]
    assert record_a["metadata"]["problem_type"] == "shikaku_rectangles"
    assert record_a["datagen_args"]["puzzle_index"] == 0
    # Puzzle metadata carried through for verification
    assert record_a["puzzle"]["numbers"] == puzzle["numbers"]
