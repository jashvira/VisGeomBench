"""Tests for convex hull ordering verifier."""

from __future__ import annotations

import json

import pytest

from visual_geometry_bench.verification.convex_hull_ordering import (
    verify_convex_hull_ordering,
)


@pytest.fixture
def record() -> dict:
    return {"ground_truth": [0, 2, 5, 7]}


def test_verify_pass(record):
    pred = json.dumps(record["ground_truth"])
    assert verify_convex_hull_ordering(pred, record) is True


def test_verify_fail_parse(record):
    assert verify_convex_hull_ordering("not a list", record) is False


def test_verify_fail_invalid_sequence(record):
    assert verify_convex_hull_ordering("[0, 0, 2]", record) is False


def test_verify_fail_wrong_order(record):
    pred = json.dumps([0, 7, 5, 2])
    diff = verify_convex_hull_ordering(pred, record, return_diff=True)
    assert isinstance(diff, dict)
    assert diff["passed"] is False
    assert diff["errors"] == ["order_mismatch"]


def test_fail_missing_indices(record):
    pred = json.dumps([0, 2, 5])
    diff = verify_convex_hull_ordering(pred, record, return_diff=True)
    assert diff == {
        "passed": False,
        "missing": [7],
        "extra": [],
        "errors": [],
    }
