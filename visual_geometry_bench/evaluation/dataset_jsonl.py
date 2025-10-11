from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Load JSONL file into a list of dicts (no transformation).

    Args:
        path: Path to JSONL file

    Returns:
        List of JSON objects per line.
    """
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


