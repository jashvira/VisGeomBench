"""Rendering entry points for VisGeomBench visualisations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping

import matplotlib.pyplot as plt

from .styles import COLOURS, apply_matplotlib_style

RendererResult = plt.Figure | Mapping[str, plt.Figure]
Renderer = Callable[[dict[str, Any], Any, bool], RendererResult]

_RENDERERS: dict[str, Renderer] = {}
_STYLE_APPLIED = False


def register_renderer(problem_type: str, renderer: Renderer, *, overwrite: bool = False) -> None:
    """Register a renderer for a given problem type."""

    if problem_type in _RENDERERS and not overwrite:
        raise ValueError(f"Renderer already registered for '{problem_type}'")
    _RENDERERS[problem_type] = renderer


def visualise_record(
    record: Mapping[str, Any],
    answer: Any | None = None,
    *,
    detail: bool = False,
    save_dir: str | Path | None = None,
    fmt: str = "png",
    output_stub: str | None = None,
    metadata_caption: str | None = None,
    answer_label: str | None = None,
    show: bool | None = None,
) -> RendererResult:
    """Render a dataset record (and optional model answer) into figure(s)."""

    problem_type = record.get("metadata", {}).get("problem_type")
    if not problem_type:
        raise KeyError("record.metadata.problem_type is required")

    renderer = _RENDERERS.get(problem_type)
    if renderer is None:
        raise NotImplementedError(f"No renderer registered for '{problem_type}'")

    _ensure_matplotlib_style()

    payload: Mapping[str, Any]
    if answer_label:
        payload = dict(record)
        render_meta = dict(payload.get("_render_meta", {}))
        render_meta["answer_label"] = answer_label
        payload["_render_meta"] = render_meta
    else:
        payload = record

    result = renderer(payload, answer, detail, show=show)

    def _apply_metadata_caption(fig: plt.Figure) -> None:
        if not metadata_caption:
            return
        # Ensure there is breathing room below the axes for the caption
        # Disable incompatible layout engines before manual adjustments (e.g., constrained layout)
        try:
            layout_engine = fig.get_layout_engine()
        except AttributeError:  # Matplotlib < 3.8 compatibility
            layout_engine = None
        if layout_engine:
            fig.set_layout_engine(None)

        current_bottom = fig.subplotpars.bottom
        target_bottom = 0.12
        if current_bottom < target_bottom:
            fig.subplots_adjust(bottom=target_bottom)
        fig.text(
            0.5,
            0.01,
            metadata_caption,
            ha="center",
            va="bottom",
            fontsize=11,
            color=COLOURS["annotation"],
        )

    if isinstance(result, Mapping):
        for fig in result.values():
            if isinstance(fig, plt.Figure):
                _apply_metadata_caption(fig)
    elif isinstance(result, plt.Figure):
        _apply_metadata_caption(result)

    if save_dir is not None:
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        record_id = record.get("id", "record")
        stem = output_stub or record_id
        output_path = save_dir / f"{stem}.{fmt}"
        if isinstance(result, Mapping):
            for name, fig in result.items():
                if not isinstance(fig, plt.Figure):
                    continue
                target = output_path.with_name(f"{stem}_{name}{output_path.suffix}")
                fig.savefig(target, format=fmt, dpi=150)
                plt.close(fig)
        else:
            result.savefig(output_path, format=fmt, dpi=150, bbox_inches="tight")
            plt.close(result)

    return result


def get_answer_label(record: Mapping[str, Any], default: str = "Answer") -> str:
    meta = record.get("_render_meta") if isinstance(record, Mapping) else None
    if isinstance(meta, Mapping):
        label = meta.get("answer_label")
        if isinstance(label, str) and label.strip():
            return label
    return default


def _ensure_matplotlib_style() -> None:
    global _STYLE_APPLIED
    if not _STYLE_APPLIED:
        apply_matplotlib_style()
        _STYLE_APPLIED = True


def _persist_figures(result: RendererResult, base_dir: Path, record_id: str, fmt: str) -> None:
    base_dir = base_dir / record_id
    base_dir.mkdir(parents=True, exist_ok=True)

    if isinstance(result, Mapping):
        for name, fig in result.items():
            _save_figure(fig, base_dir / f"{name}.{fmt}")
    else:
        _save_figure(result, base_dir / f"main.{fmt}")


def _save_figure(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
