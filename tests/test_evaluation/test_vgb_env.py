from __future__ import annotations

import json

import pytest

from visual_geometry_bench.evaluation import vgb_env
from visual_geometry_bench.registry import TASK_REGISTRY, TaskSpec


def test_format_records_creates_lookup_and_json_info():
    """Validate that _format_records:
    - Returns a lookup mapping tokens to full records.
    - Emits JSON-encoded info with record_token.
    - Includes ground_truth in answer only for problem types that require it.
    """
    records = [
        {
            "id": "requires_gt",
            "prompt": "prompt-known",
            "ground_truth": [1, 2, 3],
            "metadata": {"problem_type": "topology_enumeration"},
        },
        {
            "id": "no_gt",
            "prompt": "prompt-free",
            "ground_truth": [{"shape": "triangle", "count": 4}],
            "metadata": {"problem_type": "two_segments"},
        },
    ]

    formatted, lookup = vgb_env._format_records(records)

    assert len(formatted) == 2
    assert lookup["requires_gt"]["prompt"] == "prompt-known"
    assert lookup["no_gt"]["prompt"] == "prompt-free"

    info_payload = json.loads(formatted[0]["info"])
    assert info_payload == {"record_token": "requires_gt"}

    assert json.loads(formatted[0]["answer"]) == [1, 2, 3]

    assert formatted[1]["answer"] == ""


@pytest.fixture()
def sample_records():
    """Minimal records for reward-lookup tests using the two_segments task."""
    return [
        {
            "id": "rec_known",
            "prompt": "prompt-known",
            "ground_truth": [1, 2, 3],
            "metadata": {"problem_type": "two_segments"},
        },
        {
            "id": "rec_segments",
            "prompt": "prompt-segments",
            "ground_truth": [{"shape": "triangle", "count": 4}],
            "metadata": {"problem_type": "two_segments"},
        },
    ]


@pytest.mark.parametrize("info_format", [
    lambda: json.dumps({"record_token": "rec_segments"}),
    lambda: {"record_token": "rec_segments"}
])
def test_reward_lookup(info_format, sample_records, monkeypatch):
    """Verify the reward function resolves records via different info formats."""
    _, lookup = vgb_env._format_records(sample_records)
    captured: dict[str, dict] = {}

    original_spec = TASK_REGISTRY["two_segments"]

    def verifier(output, record):
        captured["record"] = record
        return output == "OK"

    monkeypatch.setitem(
        TASK_REGISTRY,
        "two_segments",
        TaskSpec(
            generator=original_spec.generator,
            verifier=verifier,
            requires_ground_truth=original_spec.requires_ground_truth,
        ),
    )

    reward_fn = vgb_env._make_reward_func("two_segments", lookup)

    info = info_format()
    assert reward_fn(parser=_DummyParser(), completion="OK", answer="", info=info) == 1.0
    assert captured["record"]["id"] == "rec_segments"


def test_error_on_unknown_problem_type():
    """Verify that an error is raised for unknown problem types."""
    records = [{"id": "test", "prompt": "test", "metadata": {"problem_type": "unknown_task"}}]
    
    # Test _select_verifier raises error
    with pytest.raises(ValueError, match="Unknown problem type 'unknown_task'"):
        vgb_env._select_verifier(records)
    
    # Test _format_records raises error
    with pytest.raises(ValueError, match="Unknown problem type 'unknown_task'"):
        vgb_env._format_records(records)
    
    # Test reward function raises error when record has unknown type
    records_with_valid = [{"id": "test", "prompt": "test", "metadata": {"problem_type": "two_segments"}}]
    _, lookup = vgb_env._format_records(records_with_valid)
    
    # Create record with unknown problem type in lookup
    lookup["test"] = {"id": "test", "metadata": {"problem_type": "unknown_task"}}
    reward_fn = vgb_env._make_reward_func("two_segments", lookup)
    
    with pytest.raises(ValueError, match="Unknown problem type 'unknown_task'"):
        reward_fn(parser=_DummyParser(), completion="OK", answer="", info='{"record_token": "test"}')


class _DummyParser:
    """Stub parser that returns the completion unchanged for test isolation."""
    def parse_answer(self, completion):  # noqa: D401 - simple dummy method
        return completion
