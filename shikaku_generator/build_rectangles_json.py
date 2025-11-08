#!/usr/bin/env python3
"""Generate Rectangles puzzles and serialise problem+solution metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover
    def tqdm(iterable, **kwargs):  # type: ignore
        return iterable

ROOT = Path(__file__).resolve().parent
GEN = ROOT / "generated"
GEN.mkdir(parents=True, exist_ok=True)
RECT = ROOT / "rect"


def run(command: Sequence[str], input_text: str = "") -> str:
    """Execute a subprocess command relative to ``ROOT`` and return stdout."""

    result = subprocess.run(
        command,
        cwd=str(ROOT),
        input=input_text,
        text=True,
        capture_output=True,
    )
    if result.returncode:
        sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)
    return result.stdout


def parse_save(path: Path) -> Dict[str, str]:
    """Parse a .sav file into a mapping from section keys to payload strings."""

    entries: Dict[str, str] = {}
    for line in path.read_text().splitlines():
        tokens = line.split(":", 2)
        if len(tokens) < 3:
            continue
        key = tokens[0].strip()
        payload = tokens[2]
        entries[key] = payload
    return entries


def mask_xor(buffer: bytearray, seed: bytes) -> None:
    """In-place XOR mask using a SHA1-derived keystream seeded by ``seed``."""

    digest = b""
    digest_pos = 0
    counter = 0
    for index in range(len(buffer)):
        if digest_pos == 0:
            hasher = hashlib.sha1()
            hasher.update(seed)
            hasher.update(str(counter).encode("ascii"))
            digest = hasher.digest()
            counter += 1
        buffer[index] ^= digest[digest_pos]
        digest_pos = (digest_pos + 1) % 20


def deobfuscate_bitmap(blob: bytes) -> bytes:
    """Reverse the puzzle binary obfuscation described by the RECT solver."""

    bit_count = len(blob) * 8
    num_bytes = len(blob)
    first_half = num_bytes // 2
    second_half = num_bytes - first_half
    data = bytearray(blob)
    seed = bytes(data[:first_half])
    target = data[first_half:first_half + second_half]
    mask_xor(target, seed)
    seed = bytes(data[first_half:first_half + second_half])
    target = data[:first_half]
    mask_xor(target, seed)
    if bit_count % 8:
        data[bit_count // 8] &= (0xFF00 >> (bit_count % 8)) & 0xFF
    return bytes(data)


def decode_desc_grid(body: str, width: int, height: int) -> List[List[int]]:
    """Decode RECT solver body text into a numeric grid of clues and blanks."""

    decoded: List[int] = []
    cursor = 0
    total_cells = width * height
    while cursor < len(body) and len(decoded) < total_cells:
        char = body[cursor]
        cursor += 1
        if char == "_":
            continue
        if "a" <= char <= "z":
            run_length = ord(char) - ord("a") + 1
            decoded.extend([0] * run_length)
        else:
            digits = char
            while cursor < len(body) and body[cursor].isdigit():
                digits += body[cursor]
                cursor += 1
            decoded.append(int(digits))
    if len(decoded) != total_cells:
        raise SystemExit("decoded cell count mismatch")
    return [decoded[row * width:(row + 1) * width] for row in range(height)]


def parse_aux_solution(solution_data: str, width: int, height: int) -> Tuple[List[List[int]], List[List[int]]]:
    """Decode auxiliary solution text into vertical and horizontal edge masks."""

    if not solution_data or not solution_data.startswith("S"):
        return [], []
    edge_flags = solution_data[1:]
    vertical_edge_count = (width - 1) * height
    horizontal_edge_count = (height - 1) * width
    if len(edge_flags) != vertical_edge_count + horizontal_edge_count:
        return [], []
    vertical_flags = edge_flags[:vertical_edge_count]
    horizontal_flags = edge_flags[vertical_edge_count:]
    edges_v = [
        [1 if vertical_flags[row * (width - 1) + col] == "1" else 0 for col in range(width - 1)]
        for row in range(height)
    ]
    edges_h = [
        [1 if horizontal_flags[row * width + col] == "1" else 0 for col in range(width)]
        for row in range(height - 1)
    ]
    return edges_v, edges_h


def rectangles_from_edges(
    clue_grid: Sequence[Sequence[int]],
    vertical_edges: Sequence[Sequence[int]],
    horizontal_edges: Sequence[Sequence[int]],
) -> Tuple[List[List[int]], List[Dict[str, object]]]:
    """Assemble regions into rectangles using edge masks produced by RECT."""

    height = len(clue_grid)
    width = len(clue_grid[0]) if clue_grid else 0

    if height == 0 or width == 0:
        empty_map = [[-1] * width for _ in range(height)]
        return empty_map, []

    region_map = [[-1] * width for _ in range(height)]
    rectangles: List[Dict[str, object]] = []

    rectangle_id = 0
    for row in range(height):
        for col in range(width):
            if region_map[row][col] != -1:
                continue

            top = row
            left = col
            right = col
            while right < width - 1 and vertical_edges[top][right] == 0:
                right += 1

            bottom = row
            while bottom < height - 1 and horizontal_edges[bottom][left] == 0:
                bottom += 1

            cells: List[Tuple[int, int]] = []
            clue = 0
            for r in range(top, bottom + 1):
                for c in range(left, right + 1):
                    if region_map[r][c] != -1:
                        raise ValueError("cell already assigned to a rectangle")
                    region_map[r][c] = rectangle_id
                    cells.append((r, c))
                    val = clue_grid[r][c]
                    if val:
                        clue = val

            rect_width = right - left + 1
            rect_height = bottom - top + 1
            area = rect_width * rect_height

            rectangles.append(
                {
                    "id": rectangle_id,
                    "top": top,
                    "left": left,
                    "width": rect_width,
                    "height": rect_height,
                    "area": area,
                    "clue": clue,
                    "cells": cells,
                }
            )
            rectangle_id += 1

    return region_map, rectangles


def distribute_counts(min_size: int, max_size: int, total: int) -> Dict[int, int]:
    """Spread ``total`` puzzles evenly across size buckets within bounds."""

    sizes = list(range(min_size, max_size + 1))
    base_quota = total // len(sizes)
    remainder = total % len(sizes)
    counts: Dict[int, int] = {size: base_quota for size in sizes}
    for index, size in enumerate(sizes):
        if index < remainder:
            counts[size] += 1
    return counts


def generate_ids(counts: Dict[int, int], rect_exec: str, expand: float) -> List[str]:
    """Request puzzle IDs from the RECT solver for each size bucket."""

    puzzle_ids: List[str] = []
    for size, quantity in tqdm(counts.items(), desc="Generating IDs", unit="size"):
        if quantity <= 0:
            continue
        param = f"{size}x{size}"
        if expand > 0:
            param = f"{param}e{expand:g}"
        output = run([rect_exec, "--generate", str(quantity), param])
        puzzle_ids.extend(line.strip() for line in output.splitlines() if line.strip())
    return puzzle_ids


def main() -> None:
    """Command-line entry point generating puzzles and serialising summaries."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=50, help="total puzzles to generate")
    parser.add_argument("--min-size", type=int, default=5, help="minimum grid size (square)")
    parser.add_argument("--max-size", type=int, default=20, help="maximum grid size (square)")
    parser.add_argument("--prefix", default="rect", help="basename for generated .sav files")
    parser.add_argument("--out-name", default="rectangles", help="output file stem inside generated/")
    parser.add_argument(
        "--expand",
        type=float,
        default=0.0,
        help=(
            "Expansion factor passed as 'e' suffix to the rect generator. "
            "Higher values (e.g. 0.4-0.8) stretch the base grid and typically yield harder puzzles."
        ),
    )
    args = parser.parse_args()

    if args.min_size < 2 or args.max_size < args.min_size:
        raise SystemExit("invalid size bounds")
    if args.count <= 0:
        raise SystemExit("count must be positive")

    rect_exec = str(RECT.resolve())
    rect_version = run([rect_exec, "--version"]).strip()

    counts = distribute_counts(args.min_size, args.max_size, args.count)
    ids = generate_ids(counts, rect_exec, args.expand)

    if len(ids) != args.count:
        raise SystemExit(f"expected {args.count} ids, got {len(ids)}")

    (GEN / f"{args.out_name}_ids.txt").write_text("\n".join(ids) + "\n")

    run(
        [
            rect_exec,
            "--with-solutions",
            "--save",
            str((GEN / args.prefix).resolve()),
            "--save-suffix",
            ".sav",
        ],
        input_str="\n".join(ids) + "\n",
    )

    records = []
    for idx, gid in enumerate(tqdm(ids, desc="Parsing", unit="puzzle")):
        header, body = gid.split(":", 1)
        w, h = map(int, header.split("x"))
        numbers = decode_desc_grid(body, w, h)

        sav = parse_save(GEN / f"{args.prefix}{idx}.sav")
        seed_hex = sav.get("HEXSEED")
        seed = sav.get("SEED") if seed_hex is None else None
        params_str = sav.get("PARAMS")
        cparams_str = sav.get("CPARAMS")
        aux_hex = sav.get("AUXINFO")
        solve_text = sav.get("SOLVE")
        aux = ""
        edges_v: List[List[int]]
        edges_h: List[List[int]]
        if aux_hex:
            aux_hex = re.sub(r"\s+", "", aux_hex)
            aux_bytes = bytes.fromhex(aux_hex)
            aux = deobfuscate_bitmap(aux_bytes).decode("ascii")
            edges_v, edges_h = parse_aux_solution(aux, w, h)
        elif solve_text:
            aux = re.sub(r"\s+", "", solve_text)
            edges_v, edges_h = parse_aux_solution(aux, w, h)
        else:
            edges_v, edges_h = [], []

        region_map, rectangles = rectangles_from_edges(numbers, edges_v, edges_h)

        records.append(
            {
                "id": gid,
                "width": w,
                "height": h,
                "rect_version": rect_version,
                "params": params_str,
                "cparams": cparams_str,
                "seed_hex": seed_hex,
                "seed": seed,
                "counts": {
                    "rectangles": len(rectangles),
                    "cells": w * h,
                },
                "numbers": numbers,
                "edges_v": edges_v,
                "edges_h": edges_h,
                "solution_regions": region_map,
                "solution_rectangles": rectangles,
            }
        )

    json_path = GEN / f"{args.out_name}.json"
    jsonl_path = GEN / f"{args.out_name}.jsonl"
    json_path.write_text(json.dumps(records, indent=2))
    with jsonl_path.open("w") as fh:
        for rec in records:
            fh.write(json.dumps(rec) + "\n")

    summary = {
        "total_puzzles": len(records),
        "size_bounds": [args.min_size, args.max_size],
        "size_distribution": counts,
        "output_base": str(json_path),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
