"""Tests for Shikaku verification logic."""

from __future__ import annotations

import json

import pytest

from visual_geometry_bench.verification.shikaku_tasks import verify_shikaku


@pytest.fixture()
def sample_record(tmp_path):
    # Valid 2x2: single box covering the grid, matching a single clue 4
    record = {
        "ground_truth": [[0, 0, 1, 1]],
        "puzzle": {
            "numbers": [
                [4, 0],
                [0, 0],
            ],
            "width": 2,
            "height": 2,
        },
    }
    path = tmp_path / "sample.jsonl"
    path.write_text(json.dumps(record), encoding="utf-8")
    return record


def test_verify_shikaku_accepts_correct_answer(sample_record):
    prediction = json.dumps(sample_record["ground_truth"])
    assert verify_shikaku(prediction, sample_record)


def test_verify_shikaku_rejects_overlap(sample_record):
    overlap = json.dumps([[0, 0, 1, 1], [0, 0, 1, 1]])
    result = verify_shikaku(overlap, sample_record, return_diff=True)
    assert not result["passed"]
    assert "overlap" in result["errors"][0]


def test_verify_shikaku_rejects_missing_cells(sample_record):
    # Use a puzzle where 1x1 boxes are correct so clue checks pass, then drop one cell
    record_multi = {
        "ground_truth": [[0, 0, 0, 0], [0, 1, 0, 1], [1, 0, 1, 0], [1, 1, 1, 1]],
        "puzzle": {
            "numbers": [
                [1, 1],
                [1, 1],
            ],
            "width": 2,
            "height": 2,
        },
    }
    # Drop bottom-right cell -> uncovered
    missing = json.dumps([[0, 0, 0, 0], [0, 1, 0, 1], [1, 0, 1, 0]])
    result = verify_shikaku(missing, record_multi, return_diff=True)
    assert not result["passed"]
    assert any("uncovered" in err for err in result["errors"]) or "uncovered" in result["errors"][0]


def test_verify_shikaku_rejects_wrong_area(sample_record):
    wrong = json.dumps([[0, 0, 0, 0], [1, 0, 1, 1]])
    result = verify_shikaku(wrong, sample_record, return_diff=True)
    assert not result["passed"]
    assert "clue" in result["errors"][0]


def test_verify_shikaku_parse_failure():
    record = {"ground_truth": [[0, 0, 1, 1]], "puzzle": {"numbers": [[1, 0], [0, 0]]}}
    result = verify_shikaku("not valid", record, return_diff=True)
    assert not result["passed"]
    assert result["errors"] == ["parse_failure"]
