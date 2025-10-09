"""Verification for visual geometry evaluation problems.

Provides functions to verify model answers against ground truth solutions,
handling parsing, validation, and canonicalisation.
"""

from visual_geometry_bench.verification.topology_enumeration import (
    verify_topology_enumeration,
)

__all__ = [
    "verify_topology_enumeration",
]

