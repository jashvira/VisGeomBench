"""Script to generate dataset from configuration file."""

import sys
from pathlib import Path

from visual_geometry_bench.dataset import build_dataset_from_config


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_dataset.py <config_path> [output_path]")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)

    print(f"Loading config from: {config_path}")
    records = build_dataset_from_config(config_path, output_path)

    print(f"Generated {len(records)} dataset records")
    if output_path:
        print(f"Saved to: {output_path}")

    # Print first record as sample
    if records:
        import json
        print("\nSample record:")
        print(json.dumps(records[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

