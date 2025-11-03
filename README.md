# VisGeomBench

Visual geometry evaluation benchmark for LLMs.

## Tasks

### Topology Enumeration
Given corner labels of a unit square and continuous boundaries, list all canonical 4‑tuples that force n ∈ {2,3} classes to meet inside. Corner order is configurable; tuples are canonicalised by first‑occurrence relabelling.

### Convex Hull Ordering
Given 2D points (indices = input order), return convex‑hull vertex indices in counter‑clockwise order, rotated to start at the smallest index. Assesses global shape perception and robustness to boundary‑biased point distributions.

### Delaunay Triangulation
Given points in general position, return the Delaunay triangulation as sorted triples of point indices; the triangle list is sorted. Tests understanding of empty‑circle property and precise combinatorial indexing.

### Topology Edge Tasks
Given corner labels, either enumerate guaranteed edge connections (2‑class; triple‑junction cases excluded) or classify as "known behaviour", "ambiguous", or "three domains meeting". Assesses topological consistency from minimal boundary cues and handling of ambiguity.

### Half Subdivision Neighbours
Given an axis‑aligned binary half subdivision (2D or 3D) and a target leaf, list all adjacent leaves (edge‑adjacent in 2D, face‑adjacent in 3D). Tests hierarchical spatial reasoning and exact adjacency in discretised space.

### Shikaku Rectangles
Given a grid with clue numbers, partition it into rectangles so each rectangle contains exactly one clue equal to its area (0 denotes blanks). Return rectangles as [left, top, right, bottom] with 0‑indexed inclusive coordinates. Assesses spatial planning and constraint satisfaction.

### Two Segments
Inside a square, place two boundary‑anchored segments that, together with the boundary, realise the specified polygon counts (triangles/quadrilaterals/pentagons/hexagons). Return [((x0,y0),(x1,y1)), ((x2,y2),(x3,y3))]; supports unit, random, or explicit square corners. Tests constructive geometric planning and feasibility reasoning.

## Setup

```bash
uv sync --dev
```

## Generate Dataset

```bash
uv run python scripts/generate_dataset.py configs/sample_dataset.toml
```

## Test

```bash
uv run pytest tests/ -v
```

## Evaluate

```bash
uv run vf-eval visual_geometry_bench.evaluation \
  -a '{"dataset_path": "data/visual_geometry_bench_sample.jsonl"}' \
  -m google/gemini-2.5-flash-preview-09-2025 \
  -b https://openrouter.ai/api/v1 \
  -k OPENROUTER_API_KEY \
  -n 4 -r 3 -c 2 -s
```

Flags: `-n` examples, `-r` rollouts per example, `-c` max concurrent, `-s` save outputs.
