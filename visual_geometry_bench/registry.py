"""Central registry mapping problem types to datagen generators and verifiers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

# Import modules directly
from visual_geometry_bench.datagen import (
    convex_hull_tasks,
    delaunay_tasks,
    half_subdivision_neighbours,
    shikaku_tasks,
    topology_edge_tasks,
    topology_enumeration,
    two_segments,
)
from visual_geometry_bench.verification.convex_hull_ordering import verify_convex_hull_ordering
from visual_geometry_bench.verification.delaunay_tasks import verify_delaunay_triangulation
from visual_geometry_bench.verification.half_subdivision_neighbours import verify_half_subdivision_neighbours
from visual_geometry_bench.verification.shikaku_tasks import verify_shikaku
from visual_geometry_bench.verification.topology_edge_tasks import verify_topology_edge_tasks
from visual_geometry_bench.verification.topology_enumeration import verify_topology_enumeration
from visual_geometry_bench.verification.two_segments import verify_two_segments

GeneratorFn = Callable[..., dict]
VerifierFn = Callable[[str, dict], bool]


@dataclass(frozen=True)
class TaskSpec:
    """Specification for a benchmark task."""

    generator: GeneratorFn
    verifier: VerifierFn
    requires_ground_truth: bool


TASK_REGISTRY: Dict[str, TaskSpec] = {
    "topology_enumeration": TaskSpec(
        generator=topology_enumeration.generate_dataset_record,
        verifier=verify_topology_enumeration,
        requires_ground_truth=True,
    ),
    "topology_edge_tasks": TaskSpec(
        generator=topology_edge_tasks.generate_dataset_record,
        verifier=verify_topology_edge_tasks,
        requires_ground_truth=True,
    ),
    "convex_hull_ordering": TaskSpec(
        generator=convex_hull_tasks.generate_dataset_record,
        verifier=verify_convex_hull_ordering,
        requires_ground_truth=True,
    ),
    "two_segments": TaskSpec(
        generator=two_segments.generate_dataset_record,
        verifier=verify_two_segments,
        requires_ground_truth=False,
    ),
    "delaunay_triangulation": TaskSpec(
        generator=delaunay_tasks.generate_dataset_record,
        verifier=verify_delaunay_triangulation,
        requires_ground_truth=True,
    ),
    "shikaku_rectangles": TaskSpec(
        generator=shikaku_tasks.generate_dataset_record,
        verifier=verify_shikaku,
        requires_ground_truth=True,
    ),
    "half_subdivision_neighbours": TaskSpec(
        generator=half_subdivision_neighbours.generate_dataset_record,
        verifier=verify_half_subdivision_neighbours,
        requires_ground_truth=True,
    ),
}


def get_task_spec(task_type: str) -> TaskSpec:
    """Return the specification for ``task_type``."""
    if task_type not in TASK_REGISTRY:
        raise ValueError(f"Unknown problem type '{task_type}'. Available types: {list(TASK_REGISTRY.keys())}")
    return TASK_REGISTRY[task_type]


def get_generator(task_type: str) -> GeneratorFn:
    """Return the dataset generator for ``task_type``."""
    return get_task_spec(task_type).generator


def get_verifier(problem_type: str) -> VerifierFn:
    """Return the verifier for ``problem_type``."""
    return get_task_spec(problem_type).verifier


def requires_ground_truth(problem_type: str) -> bool:
    """Return whether ``problem_type`` requires ground truth during evaluation."""
    return get_task_spec(problem_type).requires_ground_truth


__all__ = [
    "GeneratorFn",
    "VerifierFn",
    "TaskSpec",
    "TASK_REGISTRY",
    "get_task_spec",
    "get_generator",
    "get_verifier",
    "requires_ground_truth",
]
