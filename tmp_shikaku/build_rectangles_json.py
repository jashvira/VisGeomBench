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
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover
    def tqdm(iterable, **kwargs):  # type: ignore
        return iterable

ROOT = Path(__file__).resolve().parent
GEN = ROOT / "generated"
GEN.mkdir(parents=True, exist_ok=True)
RECT = ROOT / "rect"


def run(args: Sequence[str], input_str: str = "") -> str:
    result = subprocess.run(
        args,
        cwd=str(ROOT),
        input=input_str,
        text=True,
        capture_output=True,
    )
    if result.returncode:
        sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)
    return result.stdout


def parse_save(path: Path) -> Dict[str, str]:
    data: Dict[str, str] = {}
    for line in path.read_text().splitlines():
        parts = line.split(":", 2)
        if len(parts) < 3:
            continue
        key = parts[0].strip()
        payload = parts[2]
        data[key] = payload
    return data


def mask_xor(buf: bytearray, seed: bytes) -> None:
    digest = b""
    dpos = 0
    counter = 0
    for j in range(len(buf)):
        if dpos == 0:
            h = hashlib.sha1()
            h.update(seed)
            h.update(str(counter).encode("ascii"))
            digest = h.digest()
            counter += 1
        buf[j] ^= digest[dpos]
        dpos = (dpos + 1) % 20


def deobfuscate_bitmap(blob: bytes) -> bytes:
    bits = len(blob) * 8
    nbytes = len(blob)
    first = nbytes // 2
    second = nbytes - first
    b = bytearray(blob)
    seed = bytes(b[:first])
    tgt = b[first:first + second]
    mask_xor(tgt, seed)
    seed = bytes(b[first:first + second])
    tgt = b[:first]
    mask_xor(tgt, seed)
    if bits % 8:
        b[bits // 8] &= (0xFF00 >> (bits % 8)) & 0xFF
    return bytes(b)


def decode_desc_grid(body: str, w: int, h: int) -> List[List[int]]:
    vals: List[int] = []
    i = 0
    total = w * h
    while i < len(body) and len(vals) < total:
        ch = body[i]
        i += 1
        if ch == "_":
            continue
        if "a" <= ch <= "z":
            runlen = ord(ch) - ord("a") + 1
            vals.extend([0] * runlen)
        else:
            num = ch
            while i < len(body) and body[i].isdigit():
                num += body[i]
                i += 1
            vals.append(int(num))
    if len(vals) != total:
        raise SystemExit("decoded cell count mismatch")
    return [vals[r * w:(r + 1) * w] for r in range(h)]


def parse_aux_solution(aux: str, w: int, h: int) -> Tuple[List[List[int]], List[List[int]]]:
    if not aux or not aux.startswith("S"):
        return [], []
    s = aux[1:]
    n_v = (w - 1) * h
    n_h = (h - 1) * w
    if len(s) != n_v + n_h:
        return [], []
    vs = s[:n_v]
    hs = s[n_v:]
    edges_v = [[1 if vs[r * (w - 1) + c] == "1" else 0 for c in range(w - 1)] for r in range(h)]
    edges_h = [[1 if hs[r * w + c] == "1" else 0 for c in range(w)] for r in range(h - 1)]
    return edges_v, edges_h


def rectangles_from_edges(
    numbers: Sequence[Sequence[int]],
    edges_v: Sequence[Sequence[int]],
    edges_h: Sequence[Sequence[int]],
) -> Tuple[List[List[int]], List[Dict[str, object]]]:
    h = len(numbers)
    w = len(numbers[0]) if numbers else 0
    region_map = [[-1] * w for _ in range(h)]
    rectangles: List[Dict[str, object]] = []

    def neighbors(r: int, c: int) -> Iterable[Tuple[int, int]]:
        if c + 1 < w and (not edges_v or edges_v[r][c] == 0):
            yield r, c + 1
        if c - 1 >= 0 and (not edges_v or edges_v[r][c - 1] == 0):
            yield r, c - 1
        if r + 1 < h and (not edges_h or edges_h[r][c] == 0):
            yield r + 1, c
        if r - 1 >= 0 and (not edges_h or edges_h[r - 1][c] == 0):
            yield r - 1, c

    current_id = 0
    for r in range(h):
        for c in range(w):
            if region_map[r][c] != -1:
                continue
            queue: deque[Tuple[int, int]] = deque([(r, c)])
            region_map[r][c] = current_id
            cells: List[Tuple[int, int]] = [(r, c)]
            while queue:
                rr, cc = queue.popleft()
                for nr, nc in neighbors(rr, cc):
                    if region_map[nr][nc] == -1:
                        region_map[nr][nc] = current_id
                        queue.append((nr, nc))
                        cells.append((nr, nc))

            rows = [rr for rr, _ in cells]
            cols = [cc for _, cc in cells]
            top, bottom = min(rows), max(rows)
            left, right = min(cols), max(cols)
            width = right - left + 1
            height = bottom - top + 1
            area = width * height
            clue = 0
            for rr, cc in cells:
                if numbers[rr][cc]:
                    clue = numbers[rr][cc]
                    break
            rectangles.append(
                {
                    "id": current_id,
                    "top": top,
                    "left": left,
                    "width": width,
                    "height": height,
                    "area": area,
                    "clue": clue,
                    "cells": cells,
                }
            )
            current_id += 1

    return region_map, rectangles


def distribute_counts(min_size: int, max_size: int, total: int) -> Dict[int, int]:
    sizes = list(range(min_size, max_size + 1))
    base = total // len(sizes)
    remainder = total % len(sizes)
    counts: Dict[int, int] = {s: base for s in sizes}
    for idx, size in enumerate(sizes):
        if idx < remainder:
            counts[size] += 1
    return counts


def generate_ids(counts: Dict[int, int], rect_exec: str) -> List[str]:
    ids: List[str] = []
    for size, qty in tqdm(counts.items(), desc="Generating IDs", unit="size"):
        if qty <= 0:
            continue
        out = run([rect_exec, "--generate", str(qty), f"{size}x{size}"])
        ids.extend(line.strip() for line in out.splitlines() if line.strip())
    return ids


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=50, help="total puzzles to generate")
    parser.add_argument("--min-size", type=int, default=5, help="minimum grid size (square)")
    parser.add_argument("--max-size", type=int, default=20, help="maximum grid size (square)")
    parser.add_argument("--prefix", default="rect", help="basename for generated .sav files")
    parser.add_argument("--out-name", default="rectangles", help="output file stem inside generated/")
    args = parser.parse_args()

    if args.min_size < 2 or args.max_size < args.min_size:
        raise SystemExit("invalid size bounds")
    if args.count <= 0:
        raise SystemExit("count must be positive")

    rect_exec = str(RECT.resolve())
    rect_version = run([rect_exec, "--version"]).strip()

    counts = distribute_counts(args.min_size, args.max_size, args.count)
    ids = generate_ids(counts, rect_exec)

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
