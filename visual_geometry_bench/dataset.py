"""Dataset building and export utilities.

Config-driven dataset generation with:
- Static task registry (functional, no dynamic imports)
- Smart metadata inheritance (tag union + shallow override)
- JSONL export for streamable datasets
- Content-addressed IDs for deterministic generation
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Iterable

from visual_geometry_bench.registry import TASK_REGISTRY, get_generator


def build_records_from_config(cfg: dict) -> list[dict]:
    """Build dataset records from config via pure function composition.

    Smart metadata inheritance:
    - Tags: union of task-level and question-level tags
    - Other fields: shallow override (question > task)

    Dispatches to task generators via static registry (no dynamic imports).

    Args:
        cfg: Configuration dict from TOML (must have 'task' key)

    Returns:
        List of dataset records with {id, prompt, ground_truth, metadata, datagen_args}

    Raises:
        KeyError: If task type not found in task registry
    """
    tasks = cfg.get("task", [])

    def build_task_records(task: dict) -> list[dict]:
        """Build all records for a single task."""
        task_type = task["type"]
        if task_type not in TASK_REGISTRY:
            available = ", ".join(sorted(TASK_REGISTRY.keys()))
            raise KeyError(f"Unknown task type '{task_type}'. Available types: {available}")
        generator = get_generator(task_type)
        task_metadata = task.get("metadata", {})
        datagen_args_list = task.get("datagen_args_grid", [])

        def build_record(item: dict) -> dict:
            """Build a single record with metadata inheritance."""
            # Separate datagen_args from metadata override
            datagen_args = {k: v for k, v in item.items() if k != "metadata"}
            question_metadata = item.get("metadata", {})

            # Merge metadata: shallow override for most fields
            merged_metadata = {**task_metadata, **question_metadata}

            # Special case: tags use union (merge lists)
            task_tags = task_metadata.get("tags", [])
            question_tags = question_metadata.get("tags", [])
            if task_tags or question_tags:
                merged_metadata["tags"] = list(set(task_tags) | set(question_tags))

            return generator(datagen_args=datagen_args, **merged_metadata)

        return list(map(build_record, datagen_args_list))

    # Flatten list of lists from all tasks
    return [rec for task in tasks for rec in build_task_records(task)]


def save_jsonl(records: Iterable[dict], filepath: str | Path) -> None:
    """Save dataset records to JSONL file (one JSON object per line).

    Args:
        records: Iterable of record dictionaries
        filepath: Output file path
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def load_config(path: str | Path) -> dict:
    """Load TOML configuration file.

    Args:
        path: Path to TOML config file

    Returns:
        Configuration dictionary
    """
    with open(path, "rb") as f:
        return tomllib.load(f)


def build_dataset_from_config(config_path: str | Path, output_path: str | Path | None = None) -> list[dict]:
    """Load config, build dataset records, and optionally save to file.

    Args:
        config_path: Path to TOML configuration file
        output_path: Optional path to save JSONL output (overrides config)

    Returns:
        List of generated dataset records
    """
    cfg = load_config(config_path)
    records = build_records_from_config(cfg)

    # Save if output path specified (command-line override) or in config
    out_path = output_path or cfg.get("dataset", {}).get("output")
    if out_path:
        save_jsonl(records, out_path)

    return records
