"""Shared style constants for VisGeomBench visualisations."""

from __future__ import annotations

import matplotlib as mpl

# Colour palette tuned for clarity and colour-blind friendliness.
COLOURS: dict[str, str] = {
    "background": "#ffffff",
    "grid": "#b0b0b0",
    "points": "#111111",
    "truth": "#2e7d32",
    "answer": "#1565c0",
    "partial": "#f57c00",
    "reference": "#1565c0",
    "correct_neighbour": "#f57c00",
    "annotation": "#37474f",
    "success_panel": "#E8F5E9",
    "success_text": "#1B5E20",
    "success_accent": "#2E7D32",
    "failure_panel": "#FFEBEE",
    "failure_text": "#B71C1C",
    "failure_accent": "#C62828",
    "partial_panel": "#FFF3E0",
    "partial_text": "#EF6C00",
    "partial_accent": "#F57C00",
    "neutral_panel": "#ECEFF1",
    "neutral_text": "#37474f",
    "missed_vertex": "#D32F2F",
    "extra_vertex": "#8E24AA",
}

# Default font/line settings applied via matplotlib rcParams when rendering.
def apply_matplotlib_style() -> None:
    """Apply a consistent Matplotlib style for all plots."""

    mpl.rcParams.update(
        {
            "figure.dpi": 120,
            "figure.facecolor": COLOURS["background"],
            "axes.facecolor": COLOURS["background"],
            "axes.edgecolor": COLOURS["annotation"],
            "axes.labelcolor": COLOURS["annotation"],
            "grid.color": COLOURS["grid"],
            "grid.alpha": 0.4,
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.titleweight": "semibold",
            "axes.grid": True,
            "xtick.color": COLOURS["annotation"],
            "ytick.color": COLOURS["annotation"],
            "legend.frameon": False,
        }
    )
