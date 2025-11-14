# VisGeomBench

Visual geometry evaluation benchmark for LLMs.

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

## Render Visualisations

Generate question/ground-truth figures and model-answer figures separately:

```bash
# Ground-truth prompts / references
uv run python scripts/render_ground_truth.py data/<dataset>.jsonl --out data/figures/questions

# Model answers (requires JSONL with {"id", "answer"})
uv run python scripts/render_model_answers.py data/<dataset>.jsonl outputs/<answers>.jsonl --out data/figures/model_answers --metadata-caption "Model XYZ"
```

Use `--detail` to enable verbose render modes and `--suffix`/`--fmt` to customise filenames and image formats.

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

## Third-Party Components

The Shikaku task depends on Simon Tatham's Portable Puzzle Collection (MIT License).
Fetch the sources (≈30 MB) with the helper script, then build the `rect` generator
with CMake (requires any C compiler + CMake ≥3.16):

```bash
uv run python scripts/fetch_shikaku_puzzles.py
cd shikaku_generator/puzzles
cmake -S . -B build
cmake --build build --target rect
cp build/rect ..
```

The resulting executable is ignored in git; use `shikaku_generator/build_rectangles_json.py`
to regenerate puzzle JSON once the binary is available. The upstream licence text is
provided in `third_party/sgt-puzzles-LICENCE`.
