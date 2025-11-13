#!/usr/bin/env python3
"""Regenerate blog prompts JSON from datasets referenced in blog.md."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
BLOG_MD_DEFAULT = ROOT / "blog_prep" / "paper_package" / "blog.md"
OUTPUT_DEFAULT = ROOT / "blog_prep" / "blog_prompts.json"
DATA_ROOT = ROOT / "data"


def _collect_dataset_names(blog_md: Path) -> list[str]:
    text = blog_md.read_text(encoding="utf-8")
    pattern = re.compile(r"./assets/blog_prep/[^/]+/([^/]+)/")
    discovered: set[str] = set()
    for match in pattern.finditer(text):
        dataset = match.group(1)
        if (DATA_ROOT / f"{dataset}.jsonl").exists():
            discovered.add(dataset)
    return sorted(discovered)


def _load_dataset_prompts(dataset: str) -> list[dict[str, str]]:
    path = DATA_ROOT / f"{dataset}.jsonl"
    entries: list[dict[str, str]] = []
    if not path.exists():
        return entries

    with path.open("r", encoding="utf-8") as handle:
        for idx, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            prompt = record.get("prompt", "")
            rec_id = record.get("id") or str(idx)
            entries.append({"question": idx, "id": rec_id, "prompt": prompt})
    return entries


def update_blog_prompts(blog_md: Path, output_path: Path, datasets: Iterable[str] | None = None) -> None:
    if datasets is None:
        dataset_names = _collect_dataset_names(blog_md)
    else:
        dataset_names = sorted(set(datasets))

    payload = {name: _load_dataset_prompts(name) for name in dataset_names}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote prompts for {len(payload)} datasets -> {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blog-md", type=Path, default=BLOG_MD_DEFAULT, help="Path to blog markdown file")
    parser.add_argument("--out", type=Path, default=OUTPUT_DEFAULT, help="Where to write blog_prompts.json")
    parser.add_argument(
        "--datasets",
        nargs="*",
        help="Optional explicit dataset names (otherwise inferred from blog markdown)",
    )
    args = parser.parse_args()
    update_blog_prompts(args.blog_md, args.out, datasets=args.datasets)


if __name__ == "__main__":
    main()
