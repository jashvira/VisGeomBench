"""Shared style constants for VisGeomBench visualisations."""

from __future__ import annotations

from typing import Any, Sequence, Tuple

import matplotlib as mpl
import matplotlib.pyplot as plt

# Colour palette tuned for clarity and colour-blind friendliness.
COLOURS: dict[str, str] = {
    "background": "#ffffff",
    "grid": "#b0b0b0",
    "points": "#111111",
    "truth": "#2e7d32",
    "answer": "#c62828",
    "partial": "#f57c00",
    "reference": "#1565c0",
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


def get_reward_style(reward: Any) -> Tuple[str, str, str, str]:
    """Return (label, text_colour, panel_colour, accent_colour) for reward value."""

    try:
        value = float(reward) if reward is not None else None
    except (TypeError, ValueError):  # pragma: no cover - defensive
        value = None

    if value is None:
        return (
            "Reward unavailable",
            COLOURS["neutral_text"],
            COLOURS["neutral_panel"],
            COLOURS["reference"],
        )

    if value >= 0.999:
        return (
            "Model answer correct",
            COLOURS["success_text"],
            COLOURS["success_panel"],
            COLOURS["success_accent"],
        )

    if value <= 0.001:
        return (
            "Model answer incorrect",
            COLOURS["failure_text"],
            COLOURS["failure_panel"],
            COLOURS["failure_accent"],
        )

    return (
        "Model answer partially correct",
        COLOURS["partial_text"],
        COLOURS["partial_panel"],
        COLOURS["partial_accent"],
    )


def decorate_with_reward(
    fig: plt.Figure,
    axes: Sequence[plt.Axes],
    reward: Any,
    style: Tuple[str, str, str, str] | None = None,
    metadata_caption: str | None = None,
) -> Tuple[str, str, str, str]:
    """Apply reward-aware theming to the figure and return the resolved style tuple."""

    label, text_colour, panel_colour, accent = style or get_reward_style(reward)

    fig.patch.set_facecolor(panel_colour)
    if getattr(fig, "_suptitle", None) is not None:
        fig._suptitle.set_color(accent)

    if reward is None:
        reward_text = "?"
    else:
        try:
            reward_text = f"{float(reward):.2f}"
        except (TypeError, ValueError):  # pragma: no cover - defensive
            reward_text = str(reward)

    fig.text(
        0.02,
        0.96,
        label,
        color=text_colour,
        fontsize=12,
        ha="left",
        va="top",
        weight="semibold",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor=accent, linewidth=1.5, alpha=0.95),
    )
    fig.text(
        0.98,
        0.96,
        f"Reward: {reward_text}",
        color=accent,
        fontsize=12,
        ha="right",
        va="top",
        weight="semibold",
    )

    if metadata_caption:
        fig.text(
            0.5,
            0.02,
            metadata_caption,
            ha="center",
            va="bottom",
            fontsize=11,
            color=text_colour,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor=accent, linewidth=1.0, alpha=0.9),
        )

    for ax in axes:
        if ax is None:
            continue
        for spine in getattr(ax, "spines", {}).values():
            spine.set_color(accent)
            spine.set_linewidth(1.4)

    return label, text_colour, panel_colour, accent
