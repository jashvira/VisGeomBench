"""VGBench evaluation environment for Verifiers."""

from __future__ import annotations

import json
import os
from typing import Callable

import verifiers as vf
from datasets import Dataset

from visual_geometry_bench.verification.topology_enumeration import (
    verify_topology_enumeration,
)
from visual_geometry_bench.verification.topology_edge_tasks import (
    verify_topology_edge_tasks,
)

from .answer_parser import PythonLiteralParser
from .dataset_jsonl import load_jsonl

# Static registry: problem_type -> verifier function
_VERIFIER_REGISTRY: dict[str, callable] = {
    "topology_enumeration": verify_topology_enumeration,
    "topology_edge_tasks": verify_topology_edge_tasks,
}


def load_environment(
    dataset_path: str | None = None,
    verify_fn: Callable[[str, dict], bool] | None = None,
    *,
    system_prompt: str | None = None,
):
    """Construct and return a vf.SingleTurnEnv for evaluation.

    Args:
        dataset_path: Path to JSONL dataset (or use VGB_DATASET env var)
        verify_fn: Boolean verifier (model_output, record) -> bool
        system_prompt: Optional system prompt for the environment

    Returns:
        vf.SingleTurnEnv configured with dataset and rubric
    """
    path = dataset_path or os.environ.get("VGB_DATASET")
    if not path:
        raise ValueError(
            "Missing dataset path. Pass dataset_path or set VGB_DATASET env var."
        )

    records = load_jsonl(path)

    # Auto-select verifier from registry if not provided
    if verify_fn is None:
        problem_type = (records[0].get("metadata", {}).get("problem_type", "") if records else "")
        if problem_type not in _VERIFIER_REGISTRY:
            raise ValueError(
                f"Unknown problem type '{problem_type}'. "
                f"Available types: {list(_VERIFIER_REGISTRY.keys())}"
            )
        chosen_verify_fn = _VERIFIER_REGISTRY[problem_type]
    else:
        chosen_verify_fn = verify_fn

    # Adapt dataset to verifiers format: each item needs "prompt" and "answer"
    # answer = ground truth only (display and verifier input)
    dataset_list = []
    for rec in records:
        dataset_list.append({
            "id": rec.get("id", ""),
            "prompt": [{"role": "user", "content": rec["prompt"]}],
            "answer": json.dumps(rec["ground_truth"]),
        })

    # Convert to HuggingFace Dataset (required by verifiers)
    dataset = Dataset.from_list(dataset_list)

    # Instantiate parser for extracting literals from verbose CoT outputs
    parser = PythonLiteralParser()

    # Reward function: extract literal from completion, then verify
    def reward_func(parser, completion, answer, **kwargs):
        """Reward function following ARC-AGI pattern."""
        # Extract final answer from (potentially verbose) completion
        extracted = parser.parse_answer(completion)
        if extracted is None:
            return 0.0

        # Build minimal record for verifier from answer (ground truth only)
        try:
            ground_truth = json.loads(answer)
            record = {"ground_truth": ground_truth}
            return 1.0 if chosen_verify_fn(extracted, record) else 0.0
        except json.JSONDecodeError:
            return 0.0

    rubric = vf.Rubric(funcs=[reward_func], parser=parser)

    return vf.SingleTurnEnv(
        dataset=dataset,
        rubric=rubric,
        parser=parser,
        system_prompt=system_prompt,
    )

