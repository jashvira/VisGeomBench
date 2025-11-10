#!/usr/bin/env python3
"""Regenerate model_visuals for every task/question across stored runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.render_spotcheck_visuals import _load_jsonl, render_spotchecks


REPO_ROOT = Path(__file__).resolve().parents[1]


def _resolve_dataset_path(meta_path: Path, repo_root: Path) -> Path | None:
    with meta_path.open("r", encoding="utf-8") as handle:
        metadata = json.load(handle)
    dataset_ref = metadata.get("env_args", {}).get("dataset_path")
    if not dataset_ref:
        return None
    dataset_path = Path(dataset_ref)
    if not dataset_path.is_absolute():
        dataset_path = repo_root / dataset_path
    return dataset_path if dataset_path.exists() else None


def regenerate_visuals(runs_root: Path, output_root: Path) -> None:
    model_dirs = sorted(runs_root.glob("visual_geometry_bench.evaluation--*"))
    if not model_dirs:
        raise SystemExit(f"No model directories found under {runs_root}")

    for model_dir in model_dirs:
        if not model_dir.is_dir():
            continue
        model_slug = model_dir.name.split("--")[-1]
        for dataset_dir in sorted(p for p in model_dir.iterdir() if p.is_dir()):
            results_path = dataset_dir / "results.jsonl"
            metadata_path = dataset_dir / "metadata.json"
            if not results_path.exists() or not metadata_path.exists():
                continue

            dataset_path = _resolve_dataset_path(metadata_path, REPO_ROOT)
            if dataset_path is None:
                print(f"[skip] {dataset_dir}: missing dataset JSON ({metadata_path})")
                continue

            rows = _load_jsonl(results_path)
            if not rows:
                print(f"[skip] {results_path}: no rows to render")
                continue

            indices = list(range(1, len(rows) + 1))
            out_dir = output_root / model_slug / dataset_dir.name
            out_dir.mkdir(parents=True, exist_ok=True)

            print(
                f"[render] model={model_slug} dataset={dataset_dir.name} "
                f"questions={len(indices)} -> {out_dir}"
            )
            render_spotchecks(results_path, dataset_path, out_dir, indices)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runs-root",
        type=Path,
        default=REPO_ROOT / "blog_prep",
        help="Root directory containing stored eval runs (default: blog_prep)",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=REPO_ROOT / "blog_prep" / "model_visuals",
        help="Where to write per-question figures",
    )
    args = parser.parse_args()

    regenerate_visuals(args.runs_root, args.output_root)


if __name__ == "__main__":
    main()
