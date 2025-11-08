#!/usr/bin/env python3
"""Download and unpack Simon Tatham's puzzle sources locally."""

from __future__ import annotations

import argparse
import shutil
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Tuple
from urllib import request

PUZZLES_ARCHIVE_URL = "https://www.chiark.greenend.org.uk/~sgtatham/puzzles/puzzles.tar.gz"


def download_archive(url: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with request.urlopen(url) as response, destination.open("wb") as fh:  # nosec: B310 - trusted upstream
        shutil.copyfileobj(response, fh)
    return destination


def extract_archive(archive_path: Path, destination: Path) -> Tuple[Path, str]:
    temp_root = Path(tempfile.mkdtemp(prefix="sgt-puzzles-"))
    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(temp_root)
        members = [m.name.split("/", 1)[0] for m in tar.getmembers() if m.name]
    top_dir = members[0] if members else ""
    source_root = temp_root / top_dir if top_dir else temp_root
    if destination.exists():
        raise FileExistsError(f"Destination already exists: {destination}")
    shutil.move(str(source_root), destination)
    shutil.rmtree(temp_root, ignore_errors=True)
    return destination, top_dir


def ensure_destination(dest: Path, force: bool) -> None:
    if dest.exists():
        if not force:
            raise FileExistsError(
                f"Destination '{dest}' already exists. Use --force to overwrite."
            )
        shutil.rmtree(dest)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dest",
        type=Path,
        default=Path("shikaku_generator/puzzles"),
        help="Destination directory for extracted sources",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite destination directory if it already exists",
    )
    parser.add_argument(
        "--url",
        default=PUZZLES_ARCHIVE_URL,
        help="Override download URL (defaults to upstream puzzles tarball)",
    )
    args = parser.parse_args()

    try:
        ensure_destination(args.dest, args.force)
        with tempfile.TemporaryDirectory(prefix="sgt-puzzles-archive-") as tmpdir:
            archive_path = Path(tmpdir) / "puzzles.tar.gz"
            print(f"Downloading {args.url} …")
            download_archive(args.url, archive_path)
            dest_path, folder = extract_archive(archive_path, args.dest)
            print(f"Extracted {folder or 'archive'} to {dest_path}")
            print("Ready to run cmake --build build --target rect")
    except FileExistsError as exc:  # pragma: no cover - simple CLI guard
        print(exc, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
