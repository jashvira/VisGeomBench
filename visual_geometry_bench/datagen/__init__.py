"""Data generation for visual geometry evaluation dataset.

Provides problem generators, prompt builders, and solution retrievers for
various visual geometry reasoning tasks.
"""

from visual_geometry_bench.datagen.topology_enumeration import (
    build_problem_id,
    canonicalize,
    generate_dataset_record,
    get_solutions,
    make_prompt,
)

__all__ = [
    "build_problem_id",
    "canonicalize",
    "generate_dataset_record",
    "get_solutions",
    "make_prompt",
]

