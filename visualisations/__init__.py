"""Visualisation utilities for Visual Geometry Bench records."""

from __future__ import annotations

from .render import visualise_record

# Ensure built-in renderers register on import.
from . import geometry as _geometry  # noqa: F401
from . import topology as _topology  # noqa: F401
from . import two_segments as _two_segments  # noqa: F401
from . import shikaku as _shikaku  # noqa: F401
from . import half_subdivision as _half_subdivision  # noqa: F401

__all__ = [
    "visualise_record",
]
