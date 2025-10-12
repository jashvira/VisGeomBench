# VGBench

Visual geometry evaluation benchmark for LLMs.

## Tasks

### Topology Enumeration
Tests whether a model can, given only corner labels of a unit square and assuming continuous class boundaries, enumerate all corner-label configurations that force a specified number of classes to meet inside the square.

## Install

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
