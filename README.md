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
