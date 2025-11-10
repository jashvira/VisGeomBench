#!/usr/bin/env python3
"""Generate per-task success-rate comparisons for latest eval runs."""
from __future__ import annotations

import json
import math
import pathlib
from collections import defaultdict
from functools import lru_cache
import re

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.patches import Patch


BASE_DIR = pathlib.Path(__file__).parent
OUTPUT_PATH = BASE_DIR / "task_performance.png"
SUBPLOT_PATH = BASE_DIR / "task_performance_subplots.png"
OVERALL_PATH = BASE_DIR / "task_performance_overall.png"
ASSET_DIR = BASE_DIR / "assets"

MODEL_BRANDING = {
    "gpt-5-2025-08-07": {
        "color": "#8A8F9C",
        "label": "OpenAI GPT-5 (2025-08-07)",
        "axis_label": "OpenAI GPT-5",
        "logo": ASSET_DIR / "gpt_logo.png",
        "logo_zoom": 0.18,
        "icon": ASSET_DIR / "openai_icon.png",
        "icon_zoom": 0.13,
    },
    "gemini-2.5-pro": {
        "color": "#6A9CFF",
        "label": "Google Gemini 2.5 Pro",
        "axis_label": "Gemini 2.5 Pro",
        "logo": ASSET_DIR / "gemini_logo.png",
        "logo_zoom": 0.18,
        "icon": ASSET_DIR / "gemini_icon.png",
        "icon_zoom": 0.12,
    },
}


def _friendly_model_name(dirname: str) -> str:
    # Use the suffix after the last double-dash as the readable model label.
    if "--" in dirname:
        return dirname.split("--")[-1]
    return dirname


def load_success_rates():
    """Return nested dict task -> model -> (success_rate, count)."""
    task_metrics = defaultdict(dict)
    for model_dir in sorted(BASE_DIR.iterdir()):
        if not model_dir.is_dir():
            continue
        if not model_dir.name.startswith("visual_geometry_bench"):
            continue
        model_name = _friendly_model_name(model_dir.name)
        for task_dir in sorted(model_dir.iterdir()):
            if not task_dir.is_dir():
                continue
            results_file = task_dir / "results.jsonl"
            if not results_file.exists():
                continue
            rewards = []
            with results_file.open() as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    reward = obj.get("reward")
                    if reward is None:
                        continue
                    rewards.append(reward)
            if not rewards:
                continue
            success_rate = sum(1 for r in rewards if r == 1) / len(rewards)
            task_metrics[task_dir.name][model_name] = (success_rate, len(rewards))
    return task_metrics


def _pretty_task_name(task: str) -> str:
    name = task.replace("_", " ")
    name = re.sub(r"\bcurated\b", "", name, flags=re.IGNORECASE)
    name = " ".join(name.split())
    return name.title()


def _display_label(model: str) -> str:
    branding = MODEL_BRANDING.get(model)
    if branding and branding.get("label"):
        return branding["label"]
    return model


def _axis_label(model: str) -> str:
    branding = MODEL_BRANDING.get(model)
    if branding and branding.get("axis_label"):
        return branding["axis_label"]
    return _display_label(model)


def _model_color(model: str, fallback_idx: int) -> str:
    branding = MODEL_BRANDING.get(model)
    if branding and branding.get("color"):
        return branding["color"]
    return plt.cm.tab10(fallback_idx % 10)


@lru_cache(maxsize=None)
def _load_image(path: pathlib.Path):
    if not path or not path.exists():
        return None
    return mpimg.imread(path)


def _add_header(fig, models, title="Visual Geometry Bench", show_logos=False):
    fig.text(
        0.5,
        0.975,
        title,
        ha="center",
        va="top",
        fontsize=14,
        weight="bold",
        color="#111827",
    )
    if not show_logos:
        return

    branded = []
    for model in models:
        branding = MODEL_BRANDING.get(model)
        if not branding:
            continue
        logo_path = branding.get("logo")
        logo = _load_image(logo_path)
        if logo is None:
            continue
        branded.append((model, logo))
    if not branded:
        return
    if len(branded) == 1:
        xs = [0.08]
    elif len(branded) == 2:
        xs = [0.08, 0.92]
    else:
        xs = np.linspace(0.1, 0.9, len(branded))

    for (model, logo), x in zip(branded, xs):
        zoom = MODEL_BRANDING.get(model, {}).get("logo_zoom", 0.18)
        image = OffsetImage(logo, zoom=zoom)
        ab = AnnotationBbox(
            image,
            (x, 0.97),
            xycoords="figure fraction",
            frameon=False,
            box_alignment=(0.5, 1.0),
        )
        fig.add_artist(ab)


def plot_grouped(task_metrics):
    tasks = sorted(task_metrics.keys())
    models = sorted({model for metrics in task_metrics.values() for model in metrics})
    if not tasks or not models:
        raise SystemExit("No data found to plot.")

    x = np.arange(len(tasks))
    width = 0.8 / len(models)

    fig, ax = plt.subplots(figsize=(12, 5.5), facecolor="#f5f7fb")
    ax.set_facecolor("#ffffff")
    for idx, model in enumerate(models):
        offsets = x - 0.4 + width / 2 + idx * width
        heights = [task_metrics[task].get(model, (0, 0))[0] for task in tasks]
        color = _model_color(model, idx)
        bars = ax.bar(offsets, heights, width, label=_display_label(model), color=color)
        for bar, height in zip(bars, heights):
            if height is None:
                continue
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.02,
                f"{height * 100:.0f}%",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    ax.set_ylabel("Success rate")
    ax.set_ylim(0, 1.12)
    ax.set_xticks(x, [_pretty_task_name(t) for t in tasks], rotation=15, ha="right")
    ax.grid(axis="y", color="#e5e7eb", linestyle="--", linewidth=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.margins(x=0.02)
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0, 1.15))
    fig.tight_layout(rect=[0, 0.02, 1, 0.9])
    _add_header(fig, models)
    fig.savefig(OUTPUT_PATH, dpi=200)
    print(f"Wrote {OUTPUT_PATH}")


def plot_subplots(task_metrics):
    tasks = sorted(task_metrics.keys())
    models = sorted({model for metrics in task_metrics.values() for model in metrics})
    if not tasks or not models:
        raise SystemExit("No data found to plot.")

    cols = min(3, len(tasks))
    rows = math.ceil(len(tasks) / cols)
    fig, axes = plt.subplots(
        rows,
        cols,
        figsize=(4.8 * cols, 3.5 * rows),
        sharey=True,
        facecolor="#f5f7fb",
    )
    if not isinstance(axes, np.ndarray):
        axes = np.array([axes])
    axes = axes.flatten()

    for idx_ax, (ax, task) in enumerate(zip(axes, tasks)):
        values = [task_metrics[task].get(model, (0, 0))[0] for model in models]
        colors = [_model_color(model, idx) for idx, model in enumerate(models)]
        bars = ax.bar(range(len(models)), values, color=colors)
        _add_icons_on_bars(ax, bars, models)
        ax.set_title(_pretty_task_name(task), fontsize=11, weight="bold", pad=10)
        ax.set_ylim(0, 1.12)
        ax.set_xticks(range(len(models)))
        ax.set_xticklabels([_axis_label(m) for m in models], rotation=12, ha="right", fontsize=9)
        ax.grid(axis="y", color="#e5e7eb", linestyle="--", linewidth=0.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        if (idx_ax % cols) != 0:
            ax.set_yticklabels([])
            ax.set_ylabel("")
        for bar, height in zip(bars, values):
            if height is None:
                continue
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.02,
                f"{height * 100:.0f}%",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    for ax in axes[len(tasks) :]:
        ax.axis("off")

    fig.supylabel("Success rate")
    fig.tight_layout(rect=[0, 0.03, 1, 0.9])
    fig.subplots_adjust(hspace=0.5, wspace=0.35)
    _add_header(fig, models)
    fig.savefig(SUBPLOT_PATH, dpi=200)
    print(f"Wrote {SUBPLOT_PATH}")


def _add_icons_on_bars(ax, bars, models):
    for bar, model in zip(bars, models):
        branding = MODEL_BRANDING.get(model)
        if not branding:
            continue
        icon_path = branding.get("icon")
        icon = _load_image(icon_path)
        if icon is None:
            continue
        zoom = branding.get("icon_zoom", 0.1)
        image = OffsetImage(icon, zoom=zoom)
        center_x = bar.get_x() + bar.get_width() / 2
        height = bar.get_height()
        if height <= 0:
            continue
        center_y = max(height * 0.5, 0.08)
        ab = AnnotationBbox(
            image,
            (center_x, center_y),
            xycoords="data",
            frameon=False,
            box_alignment=(0.5, 0.5),
        )
        ax.add_artist(ab)


def plot_overall(task_metrics):
    aggregates = defaultdict(lambda: {"successes": 0.0, "total": 0})
    for task_data in task_metrics.values():
        for model, (rate, count) in task_data.items():
            aggregates[model]["successes"] += rate * count
            aggregates[model]["total"] += count

    models = sorted(aggregates.keys())
    if not models:
        raise SystemExit("No aggregate data found.")

    values = []
    for model in models:
        total = aggregates[model]["total"]
        value = aggregates[model]["successes"] / total if total else 0
        values.append(value)

    fig, ax = plt.subplots(figsize=(6.5, 4.5), facecolor="#f5f7fb")
    ax.set_facecolor("#ffffff")
    colors = [_model_color(model, idx) for idx, model in enumerate(models)]
    bars = ax.bar(range(len(models)), values, color=colors, width=0.5)
    ax.set_ylim(0, 1.05)
    ax.set_xticks(range(len(models)))
    ax.set_xticklabels([_display_label(m) for m in models], rotation=15, ha="right")
    ax.set_ylabel("Success rate")
    ax.grid(axis="y", color="#e5e7eb", linestyle="--", linewidth=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for bar, height in zip(bars, values):
        if height is None:
            continue
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.02,
            f"{height * 100:.0f}%",
            ha="center",
            va="bottom",
            fontsize=10,
        )
    _add_icons_on_bars(ax, bars, models)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    _add_header(fig, models, show_logos=False)
    fig.savefig(OVERALL_PATH, dpi=200)
    print(f"Wrote {OVERALL_PATH}")


def main():
    metrics = load_success_rates()
    plot_grouped(metrics)
    plot_subplots(metrics)
    plot_overall(metrics)


if __name__ == "__main__":
    main()
