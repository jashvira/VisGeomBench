#!/usr/bin/env python3
"""Synchronise blog package assets with the latest source figures.

The blog markdown stored in ``blog_prep/paper_package/blog.md`` references
images via ``./assets/...`` paths so the entire folder can be zipped and shared
without additional context. This script re-populates that ``assets`` directory
by copying the matching files from the main repository (e.g. ``blog_prep/...``
or ``blog_prep/visualisations/...``).

Usage:
    uv run python scripts/refresh_blog_assets.py

Optional flags allow overriding the markdown path, repository root, the assets
prefix, and enabling a dry run.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import Iterable, Set

MARKDOWN_IMAGE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
HTML_IMAGE = re.compile(r"<img[^>]+src=['\"]([^'\"]+)['\"]", re.IGNORECASE)


def _collect_paths(text: str) -> Set[str]:
    """Return every image path referenced via Markdown or inline HTML."""
    matches = set(MARKDOWN_IMAGE.findall(text))
    matches.update(HTML_IMAGE.findall(text))
    return {m.strip() for m in matches if m.strip()}


def _default_doc_path() -> Path:
    script_path = Path(__file__).resolve()
    return script_path.parents[1] / "blog_prep" / "paper_package" / "blog.md"


def _default_repo_root(doc_path: Path) -> Path:
    # blog.md sits at repo/blog_prep/paper_package/blog.md
    # repo root is therefore two levels up.
    return doc_path.parents[2]


def refresh_assets(
    doc_path: Path,
    repo_root: Path,
    assets_prefix: str = "./assets/",
    dry_run: bool = False,
) -> int:
    text = doc_path.read_text(encoding="utf-8")
    references = sorted(p for p in _collect_paths(text) if p.startswith(assets_prefix))

    if not references:
        print(f"No asset references using prefix '{assets_prefix}' were found in {doc_path}.")
        return 0

    copied = 0
    missing: list[str] = []

    for rel in references:
        source_rel = Path(rel[len(assets_prefix) :])
        source_path = (repo_root / source_rel).resolve()
        dest_path = (doc_path.parent / Path(rel)).resolve()

        if not source_path.exists():
            missing.append(f"{rel} -> {source_path}")
            continue

        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if dry_run:
            print(f"[dry-run] Would copy {source_path} -> {dest_path}")
            continue

        shutil.copy2(source_path, dest_path)
        copied += 1

    if missing:
        joined = "\n  - ".join(missing)
        print(
            "Warning: source files missing for the following references:\n  - " + joined,
            file=sys.stderr,
        )

    print(f"Synced {copied} assets from {repo_root} into {doc_path.parent / 'assets'}.")
    return copied


def main(argv: Iterable[str] | None = None) -> int:
    default_doc = _default_doc_path()
    parser = argparse.ArgumentParser(description="Refresh packaged blog assets from source figures.")
    parser.add_argument(
        "--doc",
        type=Path,
        default=default_doc,
        help=f"Path to the blog markdown file (default: {default_doc})",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root that contains the authoritative assets (defaults to doc path minus two parents)",
    )
    parser.add_argument(
        "--assets-prefix",
        default="./assets/",
        help="Only copy paths that start with this prefix (default: ./assets/)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print planned copies without writing files.")

    args = parser.parse_args(list(argv) if argv is not None else None)

    doc_path = args.doc.resolve()
    if not doc_path.exists():
        parser.error(f"Markdown file {doc_path} does not exist")

    repo_root = args.repo_root.resolve() if args.repo_root else _default_repo_root(doc_path)

    refresh_assets(doc_path, repo_root, assets_prefix=args.assets_prefix, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
