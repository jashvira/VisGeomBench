#!/usr/bin/env python3
"""Render spot-check visualisations for specific eval questions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from visual_geometry_bench.evaluation.answer_parser import PythonLiteralParser
from visualisations import visualise_record


def _clean_dataset_name(stem: str) -> str:
    cleaned = stem.replace("_", " ").replace("curated", "")
    cleaned = " ".join(cleaned.split())
    return cleaned.title()


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _load_dataset_records(path: Path) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    records = _load_jsonl(path)
    mapping: dict[str, dict[str, Any]] = {}
    for record in records:
        key = record.get("id") or record.get("metadata", {}).get("record_token")
        if key:
            mapping[key] = record
    return records, mapping


def render_spotchecks(
    results_path: Path,
    dataset_path: Path,
    output_dir: Path,
    indices: list[int],
) -> None:
    rows = _load_jsonl(results_path)
    if not rows:
        raise SystemExit(f"No rows found in {results_path}")

    dataset_records, dataset_map = _load_dataset_records(dataset_path)
    if not dataset_records:
        raise SystemExit(f"No records loaded from {dataset_path}")

    parser = PythonLiteralParser()

    model_fragment = results_path.parent.parent.name
    model_name = model_fragment.split("--")[-1].replace("_", " ")
    dataset_name = _clean_dataset_name(dataset_path.stem)
    caption_prefix = f"{model_name} · {dataset_name}"

    output_dir.mkdir(parents=True, exist_ok=True)

    for idx in indices:
        zero_idx = idx - 1
        if zero_idx < 0 or zero_idx >= len(rows):
            print(f"[{idx}] out of range for {results_path}, skipping")
            continue
        row = rows[zero_idx]
        record_token = row.get("info", {}).get("record_token") or row.get("record_token")
        record = dataset_map.get(record_token)
        if not record:
            example_id = row.get("example_id")
            if isinstance(example_id, int) and 0 <= example_id < len(dataset_records):
                record = dataset_records[example_id]
            elif zero_idx < len(dataset_records):
                record = dataset_records[zero_idx]
        if not record:
            print(f"[{idx}] missing record token {record_token}, skipping")
            continue

        answer = row.get("answer")
        completion = row.get("completion")
        if isinstance(completion, list) and completion:
            content = completion[-1].get("content")
            parsed = parser.parse_answer(content) if isinstance(content, str) else None
            answer = parsed if parsed is not None else content

        output_stub = f"question_{idx:03d}"
        try:
            visualise_record(
                record,
                answer,
                detail=True,
                save_dir=output_dir,
                fmt="png",
                output_stub=output_stub,
                metadata_caption=f"{caption_prefix} · Q{idx}",
                answer_label=model_name,
            )
            print(f"[{idx}] rendered to {output_dir}/{output_stub}.png")
        except Exception as exc:  # noqa: BLE001
            print(f"[{idx}] failed to render: {exc}")


def parse_indices(limit: int | None, indices_arg: str | None, max_len: int) -> list[int]:
    if indices_arg:
        indices = []
        for part in indices_arg.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                start, end = part.split("-", 1)
                indices.extend(range(int(start), int(end) + 1))
            else:
                indices.append(int(part))
        return indices
    limit = limit or 1
    return list(range(1, min(max_len, limit) + 1))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--limit", type=int, default=1, help="Number of leading questions to visualise")
    parser.add_argument("--indices", type=str, help="Comma/range list of 1-based question indices (overrides --limit)")
    args = parser.parse_args()

    rows = _load_jsonl(args.results)
    if not rows:
        raise SystemExit(f"No rows found in {args.results}")
    indices = parse_indices(args.limit, args.indices, len(rows))

    render_spotchecks(args.results, args.dataset, args.output_dir, indices)


if __name__ == "__main__":
    main()
