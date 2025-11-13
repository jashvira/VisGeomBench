from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Iterable

from visualisations.render import RenderMode, visualise_record
from visual_geometry_bench.datagen.half_subdivision_neighbours import _prepare_case


def _load_record(record_id: str, jsonl_path: Path) -> dict:
    with jsonl_path.open() as fh:
        for line in fh:
            record = json.loads(line)
            if record.get("id") == record_id:
                return record
    raise ValueError(f"Record {record_id!r} not found in {jsonl_path}")


def _parse_answer(raw: str | None) -> list[str] | None:
    if not raw:
        return None

    candidate: object = raw
    if isinstance(candidate, str) and candidate.strip().startswith("["):
        try:
            candidate = ast.literal_eval(candidate)
        except (ValueError, SyntaxError):
            candidate = candidate.strip()

    if isinstance(candidate, str):
        try:
            candidate = json.loads(candidate)
        except json.JSONDecodeError:
            return None

    if isinstance(candidate, Iterable):
        items = [item for item in candidate if isinstance(item, str)]
        return items or None

    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render half-subdivision records in question and/or model-answer mode.",
    )
    parser.add_argument("--record-id", required=True, help="Record ID inside the JSONL file.")
    parser.add_argument(
        "--jsonl",
        default=Path("data/half_subdivision.jsonl"),
        type=Path,
        help="Path to the half-subdivision JSONL (default: %(default)s).",
    )
    parser.add_argument(
        "--mode",
        choices=["question", "answer", "both"],
        default="both",
        help="Which view(s) to render (default: %(default)s).",
    )
    parser.add_argument(
        "--model-answer",
        help="Optional string/list literal of neighbour labels for the model-answer view.",
    )
    parser.add_argument(
        "--save-dir",
        type=Path,
        help="If supplied, figures are saved there instead of (or in addition to) being shown.",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Disable interactive display (useful for non-GUI environments).",
    )
    args = parser.parse_args()

    record = _load_record(args.record_id, args.jsonl)

    # Rebuild the deterministic subdivision so the renderer matches the dataset prompt.
    _prepare_case(record["datagen_args"])

    model_answer = _parse_answer(args.model_answer)
    show_figures = not args.no_show

    if args.mode in {"question", "both"}:
        visualise_record(
            record,
            answer=None,
            show=show_figures,
            mode=RenderMode.GROUND_TRUTH,
            save_dir=args.save_dir,
            output_stub=f"{args.record_id}_question",
        )

    if args.mode in {"answer", "both"}:
        visualise_record(
            record,
            answer=model_answer,
            show=show_figures,
            mode=RenderMode.MODEL_ANSWER,
            save_dir=args.save_dir,
            output_stub=f"{args.record_id}_model",
        )


if __name__ == "__main__":
    main()
