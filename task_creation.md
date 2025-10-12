# Adding a New Evaluation Task

## Core Components

### 0. Configuration (TOML in `configs/`)
Use TOML. See `configs/sample_dataset.toml`.
```toml
[dataset]
output = "data/<task>.jsonl"

[[task]]
type = "<task>"
datagen_args_grid = [
  { /* args variant 1 */ },
  { /* args variant 2 */ }
]
# optional per-task overrides:
# metadata = { tags = ["..."], difficulty = "...", requires_visual = true }
```

### 1. Data Generation (`visual_geometry_bench/datagen/<task>.py`)
Implement three functions:
- `make_prompt(...)` → problem statement with parameters
- `get_solutions(...)` → ground truth in the exact format the model should output
- `generate_dataset_record(datagen_args, ...)` → eval record:
  ```python
  {
      "id": content_hash,
      "prompt": str,
      "ground_truth": <model's expected output format>,  # CRITICAL: must match what model outputs
      "metadata": {"problem_type", "tags", "difficulty", "requires_visual"},
      "datagen_args": {...}  # for reproducibility
  }
  ```

**Ground truth format:** Must be the exact structure the model should output. The generic evaluation harness (`vgb_env.py`) passes only `ground_truth` to verifiers, so it must be self-contained and in the model's answer format (e.g., a list of tuples, a list of edge pairs, etc.). See `topology_enumeration.py` and `topology_edge_tasks.py` for examples.

#### Shared datagen utilities
- Use `visual_geometry_bench.datagen.utils` for general operations.
- Prefer these helpers over reimplementing.

### 2. Verification (`visual_geometry_bench/verification/<task>.py`)
Single function:
```python
def verify_<task>(model_output: str, record: dict) -> bool:
# Or optionally with diagnostic mode:
# def verify_<task>(model_output: str, record: dict, *, return_diff: bool = False) -> bool | dict:
```

**Input:** `record` contains `{"ground_truth": <model's expected format>}`. The verifier should compare the parsed model output directly against `record["ground_truth"]`.

Implementation pattern:
1. **Parse**: extract answer from model output (strict format validation)
2. **Validate**: check constraints with early exits where possible
3. **Canonicalise**: normalise prediction and ground truth to comparable forms
4. **Compare**: deterministic equality check

Return modes (optional, but recommended):
- `return_diff=False`: bool (efficient, early exits)
- `return_diff=True`: `{passed, missing, extra, errors, details}` for diagnostics

Add module docstring with tight semantics: answer format, validation steps, pass criterion.

### 3. Tests
**Datagen** (`tests/test_datagen/test_<task>.py`):
- Valid records: `generate_dataset_record` produces correct structure
- Consistency: `get_solutions` matches `datagen_args` constraints
- Determinism: same args → same output

**Verification** (`tests/test_verification/test_<task>.py`):
- Pass: correct solutions and task-specific invariances
- Fail: parse errors, format violations, constraint violations
- Diagnostics: `return_diff=True` provides useful output (if implemented)

Avoid repetition; one test per distinct failure mode.

### 4. Export (`visual_geometry_bench/verification/__init__.py`)
```python
from .task import verify_task
__all__ = [..., "verify_task"]
```

## Principles
- **Deterministic**: same input → same output
- **Non-throwing**: return False/dict, never raise
- **No duplicate work**: single pass, early exits
- **Tight docs**: succinct philosophy in docstrings

---

## Checklist

- [ ] Config: TOML file in `configs/` (see `configs/sample_dataset.toml`)
- [ ] Datagen: `make_prompt`, `get_solutions`, `generate_dataset_record`
- [ ] Datagen tests: valid records, consistency, determinism
- [ ] Verification: `verify_<task>(model_output, record)` (optionally `return_diff=False`)
- [ ] Verification tests: pass cases, fail cases, (optionally diff diagnostics)
- [ ] Export: add to `__init__.py` `__all__`
- [ ] Run: `pytest tests/test_datagen/test_<task>.py tests/test_verification/test_<task>.py`

