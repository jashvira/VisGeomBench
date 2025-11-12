"""Render model-answer visualisations using dataset + answer JSONL files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from visualisations import visualise_record
from visualisations.render import RenderMode


def _iter_records(dataset_path: Path):
    with dataset_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def _load_answers(path: Path, *, id_field: str, answer_field: str) -> dict[str, object]:
    mapping: dict[str, object] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            record_id = data.get(id_field)
            if record_id is None:
                continue
            mapping[str(record_id)] = data.get(answer_field)
    return mapping


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="Path to dataset JSONL file")
    parser.add_argument("answers", type=Path, help="Path to answers JSONL file")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/figures/model_answers"),
        help="Directory to write rendered figures (default: data/figures/model_answers)",
    )
    parser.add_argument("--fmt", default="png", help="Image format (default: png)")
    parser.add_argument(
        "--detail",
        action="store_true",
        help="Render in detail mode (passes detail=True to the renderer)",
    )
    parser.add_argument(
        "--suffix",
        default="answer",
        help="Suffix appended to the record id for the output filename",
    )
    parser.add_argument(
        "--metadata-caption",
        default=None,
        help="Optional caption rendered under each figure (e.g., model name)",
    )
    parser.add_argument(
        "--id-field",
        default="id",
        help="Field name in the answers JSONL containing the record identifier",
    )
    parser.add_argument(
        "--answer-field",
        default="answer",
        help="Field name in the answers JSONL containing the model output",
    )
    parser.add_argument(
        "--skip-missing",
        action="store_true",
        help="Skip rendering records with no matching answer",
    )
    args = parser.parse_args()

    answers = _load_answers(args.answers, id_field=args.id_field, answer_field=args.answer_field)
    if not answers:
        raise SystemExit("No answers found in the provided file.")

    args.out.mkdir(parents=True, exist_ok=True)

    for record in _iter_records(args.dataset):
        record_id = record.get("id")
        if record_id is None:
            continue
        answer = answers.get(str(record_id))
        if answer is None and args.skip_missing:
            continue
        stub = f"{record_id}_{args.suffix}" if args.suffix else str(record_id)
        visualise_record(
            record,
            answer,
            detail=args.detail,
            save_dir=args.out,
            fmt=args.fmt,
            output_stub=stub,
            metadata_caption=args.metadata_caption,
            mode=RenderMode.MODEL_ANSWER,
        )


if __name__ == "__main__":
    main()

