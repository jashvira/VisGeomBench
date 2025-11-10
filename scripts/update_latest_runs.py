#!/usr/bin/env python3
"""Utility to copy a new eval run into the top-level latest_runs directory.

Usage:
    python scripts/update_latest_runs.py <model_dir_name> <run_id>

Example:
    python scripts/update_latest_runs.py \\
        visual_geometry_bench.evaluation--google--gemini-2.5-pro \\
        5348ccfd

The script reads outputs/evals/<model_dir_name>/<run_id>/metadata.json to
discover which dataset was evaluated, then copies that run into
latest_runs/<model_dir_name>/<dataset_stem>, replacing any previous entry for
the same dataset.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVALS_ROOT = ROOT / "outputs" / "evals"
LATEST_ROOT = ROOT / "latest_runs"


def copy_run(model_dir: str, run_id: str, force: bool = False) -> Path | None:
    src_run = EVALS_ROOT / model_dir / run_id
    metadata_path = src_run / "metadata.json"
    results_path = src_run / "results.jsonl"

    if not src_run.exists():
        raise FileNotFoundError(f"Run directory not found: {src_run}")
    if not metadata_path.exists() or not results_path.exists():
        raise FileNotFoundError(f"Run missing metadata/results: {src_run}")

    with metadata_path.open() as handle:
        metadata = json.load(handle)

    dataset_path = metadata.get("env_args", {}).get("dataset_path")
    if not dataset_path:
        raise ValueError(f"No dataset_path recorded in metadata: {metadata_path}")

    dataset_name = Path(dataset_path).stem
    dest = LATEST_ROOT / model_dir / dataset_name

    if dest.exists() and not force:
        existing_meta = dest / "metadata.json"
        if existing_meta.exists():
            existing_mtime = existing_meta.stat().st_mtime
            new_mtime = metadata_path.stat().st_mtime
            if new_mtime <= existing_mtime:
                print(
                    f"Skipping copy: existing run for {dataset_name} is newer "
                    f"({existing_meta} mtime >= {metadata_path} mtime)"
                )
                return None
        shutil.rmtree(dest)
    elif dest.exists():
        shutil.rmtree(dest)

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src_run, dest)
    return dest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model_dir", help="e.g., visual_geometry_bench.evaluation--google--gemini-2.5-pro")
    parser.add_argument("run_id", help="hash-like directory name under the model directory")
    parser.add_argument("--force", action="store_true", help="overwrite even if existing run is newer or same timestamp")
    args = parser.parse_args()

    dest = copy_run(args.model_dir, args.run_id, force=args.force)
    if dest:
        print(f"Copied {args.model_dir}/{args.run_id} -> {dest}")
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
