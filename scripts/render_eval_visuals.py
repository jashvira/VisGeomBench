"""Generate visualisations from evaluation results JSONL files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from visual_geometry_bench.evaluation.answer_parser import PythonLiteralParser

from visualisations import visualise_record


def _load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _extract_record(row: dict[str, Any]) -> dict[str, Any] | None:
    info = row.get("info")
    if isinstance(info, dict) and isinstance(info.get("raw_record"), dict):
        return info["raw_record"]
    # Backwards compatibility: some runs may embed the record under `row["task"]` if dict
    task = row.get("task")
    if isinstance(task, dict):
        return task
    return None


def _reconstruct_record_from_prompt(prompt_text: str) -> dict[str, Any] | None:
    """Attempt to reconstruct a full dataset record by prompt matching."""
    import json
    from pathlib import Path

    candidates = [
        Path("data/sample_dataset.jsonl"),
        Path("data/preview.jsonl"),
        Path("data/preview_uniform.jsonl"),
        Path("data/visual_geometry_bench_sample.jsonl"),
    ]
    for cand in candidates:
        if not cand.is_file():
            continue
        with cand.open() as f:
            for line in f:
                rec = json.loads(line)
                if prompt_text == rec.get("prompt", ""):
                    return rec
    return None


def _extract_answer(row: dict[str, Any], parser: PythonLiteralParser) -> Any:
    # Preferred: raw answer stored explicitly
    info = row.get("info")
    if isinstance(info, dict) and "raw_answer" in info:
        raw_answer = info["raw_answer"]
        if isinstance(raw_answer, str):
            parsed = parser.parse_answer(raw_answer)
            return parsed if parsed is not None else raw_answer

    # Fallback: use completion text (last assistant message)
    completion = row.get("completion")
    if isinstance(completion, list) and completion:
        content = completion[-1].get("content")
        if isinstance(content, str):
            parsed = parser.parse_answer(content)
            if parsed is not None:
                return parsed
            return content

    # Final fallback: row "answer" field as-is
    ans = row.get("answer")
    # Defensive: if answer is a non-iterable primitive (int/float/bool), wrap in list so renderers can handle it gracefully
    if isinstance(ans, (int, float, bool)):
        return [ans]
    return ans


def render_results(results_path: Path, output_dir: Path, fmt: str, detail: bool, overwrite: bool) -> None:
    rows = _load_rows(results_path)
    if not rows:
        print(f"No rows found in {results_path}")
        return

    run_id = results_path.parent.name
    model_fragment = results_path.parent.parent.name if results_path.parent.parent else "unknown-model"
    model_name = model_fragment.split("--")[-1].replace("_", " ")
    metadata_caption = f"Model: {model_name} • Run: {run_id}"

    target_dir = output_dir / run_id
    target_dir.mkdir(parents=True, exist_ok=True)

    parser = PythonLiteralParser()

    for index, row in enumerate(rows):
        record = _extract_record(row)
        if not record:
            # Attempt to reconstruct by prompt matching
            prompt_text = row.get("prompt", [{}])[0].get("content", "")
            record = _reconstruct_record_from_prompt(prompt_text)
            if not record:
                print(f"[{index}] skipping (cannot reconstruct record)")
                continue

        record_id = record.get("id") or f"record_{index}"
        question_number = index + 1
        output_file = target_dir / f"{question_number:03d}.{fmt}"
        if output_file.exists() and not overwrite:
            print(f"[{question_number:03d}] exists, skipping (use --overwrite to regenerate)")
            continue

        answer = _extract_answer(row, parser)
        reward = row.get("reward")
        try:
            visualise_record(
                record,
                answer,
                detail=detail,
                save_dir=target_dir,
                fmt=fmt,
                reward=reward,
                output_stub=f"{question_number:03d}",
                metadata_caption=metadata_caption,
            )
            print(f"[{question_number:03d}] rendered (id={record_id})")
        except Exception as exc:  # noqa: BLE001 - propagate info but continue batching
            print(f"[{question_number:03d}] failed: {exc}")
            # Fallback: render with an explicit Invalid answer to avoid missing images
            try:
                visualise_record(
                    record,
                    "Invalid answer",
                    detail=detail,
                    save_dir=target_dir,
                    fmt=fmt,
                    reward=reward,
                    output_stub=f"{question_number:03d}",
                    metadata_caption=metadata_caption,
                )
                print(f"[{question_number:03d}] rendered (fallback, id={record_id})")
            except Exception as fallback_exc:
                print(f"[{question_number:03d}] fallback also failed: {fallback_exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path, help="Path to results.jsonl file")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("outputs/visualisations"),
        help="Output directory base (default: outputs/visualisations)",
    )
    parser.add_argument("--fmt", default="png", help="Image format (png, svg, ...)")
    parser.add_argument("--detail", action="store_true", help="Request detail figures where available")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Regenerate figures even if output directory already exists",
    )
    args = parser.parse_args()

    render_results(args.results, args.out, args.fmt, args.detail, args.overwrite)


if __name__ == "__main__":  # pragma: no cover
    main()
