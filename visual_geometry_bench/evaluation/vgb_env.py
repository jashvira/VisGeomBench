"""VisGeomBench evaluation environment for Verifiers."""

from __future__ import annotations

import json
import os
from typing import Any, Iterable

import verifiers as vf
from datasets import Dataset

from visual_geometry_bench.registry import (
    TASK_REGISTRY,
    get_verifier,
    requires_ground_truth as task_requires_ground_truth,
)

from .answer_parser import PythonLiteralParser
from .dataset_jsonl import load_jsonl


def _resolve_dataset_path(dataset_path: str | None) -> str:
    """Resolve dataset path from argument or environment variable."""

    resolved = dataset_path or os.environ.get("VGB_DATASET")
    if not resolved:
        raise ValueError(
            "Missing dataset path. Pass dataset_path or set VGB_DATASET env var."
        )
    return resolved


def _format_records(
    records: Iterable[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """Create dataset rows plus a lookup table for raw records."""

    formatted: list[dict[str, Any]] = []
    lookup: dict[str, dict[str, Any]] = {}

    for index, record in enumerate(records):
        problem_type = record.get("metadata", {}).get("problem_type", "")
        needs_ground_truth = task_requires_ground_truth(problem_type)
        answer_payload = record.get("ground_truth") if needs_ground_truth else ""

        record_id = record.get("id", "")
        token = record_id or str(index)

        formatted.append(
            {
                "id": record_id,
                "prompt": [{"role": "user", "content": record["prompt"]}],
                "answer": json.dumps(answer_payload) if answer_payload not in ("", None) else "",
                "info": json.dumps({"record_token": token}),
            }
        )

        lookup[token] = record

    return formatted, lookup


def _resolve_record(info, record_lookup, default_record):
    """Extract record from info using lookup token."""
    if isinstance(info, str):
        if info in record_lookup:
            return dict(record_lookup[info])
        else:
            try:
                info = json.loads(info)
            except json.JSONDecodeError:
                return default_record
    
    if isinstance(info, dict):
        token = info.get("record_token")
        if isinstance(token, str) and token in record_lookup:
            return dict(record_lookup[token])
    
    return default_record


def _make_reward_func(record_lookup: dict[str, dict[str, Any]]):
    """Create reward function compatible with vf.Rubric."""

    def reward_func(parser, completion, answer, *, info=None, **_kwargs):
        extracted = parser.parse_answer(completion)
        if extracted is None:
            return 0.0

        record = _resolve_record(info, record_lookup, {})
        record_problem = record.get("metadata", {}).get("problem_type")

        if record_problem not in TASK_REGISTRY:
            raise ValueError(
                f"Unknown problem type '{record_problem}'. Available types: {list(TASK_REGISTRY.keys())}"
            )

        verifier = get_verifier(record_problem)
        needs_gt = task_requires_ground_truth(record_problem)

        # Handle ground truth injection
        if answer and answer not in (None, ""):
            try:
                record["ground_truth"] = json.loads(answer)
            except (json.JSONDecodeError, TypeError):
                if needs_gt:
                    return 0.0
        elif needs_gt:
            return 0.0

        return 1.0 if verifier(extracted, record) else 0.0

    return reward_func


def load_environment(
    dataset_path: str | None = None,
    *,
    system_prompt: str | None = None,
):
    """Construct and return a vf.SingleTurnEnv for evaluation.

    Args:
        dataset_path: Path to JSONL dataset (or use VGB_DATASET env var)
        system_prompt: Optional system prompt for the environment

    Returns:
        vf.SingleTurnEnv configured with dataset and rubric
    """

    path = _resolve_dataset_path(dataset_path)
    raw_records = load_jsonl(path)

    dataset_rows, record_lookup = _format_records(raw_records)
    dataset = Dataset.from_list(dataset_rows)
    parser = PythonLiteralParser()
    reward_func = _make_reward_func(record_lookup)
    rubric = vf.Rubric(funcs=[reward_func], parser=parser)

    return vf.SingleTurnEnv(
        dataset=dataset,
        rubric=rubric,
        parser=parser,
        system_prompt=system_prompt,
    )
