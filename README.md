# VGBench

Visual geometry evaluation benchmark for LLMs.

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
