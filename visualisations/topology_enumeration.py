"""Topology enumeration renderer."""

from __future__ import annotations

import ast
from typing import Any, Mapping, Sequence

import matplotlib.pyplot as plt

from visual_geometry_bench.datagen.topology_enumeration import canonicalize, get_solutions

from .render import get_answer_label, register_renderer
from .styles import COLOURS
from .topology_common import _DEFAULT_CORNER_ORDER, _text_block

_CANONICAL_LABEL = "Canonical equivalence classes"


def _format_configuration_block(
    base_lines: Sequence[str],
    tuples: Sequence[tuple[int, int, int, int]] | None,
    *,
    section_label: str,
    include_canonical: bool = True,
    canonical_label: str = _CANONICAL_LABEL,
    canonical_mode: str = "summary",
    errors: Sequence[str] | None = None,
    empty_message: str | None = None,
) -> list[str]:
    lines = list(base_lines)

    if errors:
        if lines and lines[-1] != "":
            lines.append("")
        lines.extend(errors)
        return lines

    if tuples is None:
        if empty_message:
            if lines and lines[-1] != "":
                lines.append("")
            lines.append(empty_message)
        return lines

    configs = [tuple(cfg) for cfg in tuples]

    if lines and lines[-1] != "":
        lines.append("")

    lines.append(f"{section_label}:")
    lines.extend(str(cfg) for cfg in configs)

    if include_canonical:
        lines.append("")
        lines.append(f"{canonical_label}:")

        if canonical_mode == "per_tuple":
            for cfg in configs:
                lines.append(f"{cfg} → {canonicalize(cfg)}")
        else:
            seen: list[tuple[int, int, int, int]] = []
            for cfg in configs:
                canon = canonicalize(cfg)
                if canon not in seen:
                    seen.append(canon)
            lines.extend(str(cfg) for cfg in seen)

    return lines


def _parse_topology_answer(answer: Any) -> tuple[list[tuple[int, int, int, int]] | None, list[str]]:
    errors: list[str] = []

    if isinstance(answer, str):
        try:
            raw = ast.literal_eval(answer)
        except (ValueError, SyntaxError):
            errors.append("Parse failure: could not evaluate string answer.")
            return None, errors
    elif isinstance(answer, Sequence) and not isinstance(answer, (str, bytes)):
        raw = list(answer)
    else:
        errors.append(f"Unsupported answer type: {type(answer).__name__}")
        return None, errors

    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        errors.append("Answer is not an iterable of tuples.")
        return None, errors

    tuples: list[tuple[int, int, int, int]] = []
    for idx, item in enumerate(raw):
        if not isinstance(item, (list, tuple)):
            errors.append(f"Entry {idx} is not a tuple/list: {item!r}")
            return None, errors
        if len(item) != 4:
            errors.append(f"Entry {idx} has length {len(item)} (expected 4).")
            return None, errors
        try:
            coerced = tuple(int(x) for x in item)
        except (TypeError, ValueError):
            errors.append(f"Entry {idx} contains non-integer values: {item!r}")
            return None, errors
        tuples.append(coerced)

    return tuples, errors


def _prepare_text_axis(ax: plt.Axes, title: str | None, colour: str) -> None:
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    if title:
        ax.set_title(title, fontsize=13, weight="semibold", pad=10, color=colour)


def _layout_text_axes(fig: plt.Figure, answer_provided: bool) -> tuple[plt.Axes, plt.Axes | None]:
    if answer_provided:
        gs = fig.add_gridspec(1, 2, width_ratios=(1.2, 1.0), wspace=0.35)
        return fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
    return fig.add_subplot(111), None


def _build_truth_lines(datagen_args: Mapping[str, Any]) -> list[str]:
    args = dict(datagen_args or {})
    n_classes = args.get("n_classes")
    corner_order = tuple(args.get("corner_order", _DEFAULT_CORNER_ORDER))

    base: list[str] = []
    errors: list[str] = []
    tuples: list[tuple[int, int, int, int]] | None = None
    canonical_only: list[tuple[int, int, int, int]] | None = None

    if n_classes is None:
        errors.append("Missing datagen_args.n_classes")
    else:
        try:
            n_classes_int = int(n_classes)
        except (TypeError, ValueError):
            errors.append(f"Invalid n_classes: {n_classes!r}")
        else:
            try:
                solutions = get_solutions(n_classes_int, corner_order)
            except (AssertionError, ValueError) as exc:
                errors.append("Unable to compute ground truth")
                errors.append(str(exc))
            else:
                base.extend(
                    [
                        f"n_classes={n_classes_int}",
                        f"corner_order={corner_order}",
                        f"Ground-truth tuples: {len(solutions)}",
                    ]
                )
                tuples = [tuple(cfg) for cfg in solutions]
                seen: list[tuple[int, int, int, int]] = []
                for cfg in tuples:
                    canon = canonicalize(cfg)
                    if canon not in seen:
                        seen.append(canon)
                canonical_only = seen

    lines = _format_configuration_block(
        base,
        canonical_only,
        section_label="Solutions",
        include_canonical=False,
        errors=errors if errors else None,
        empty_message="No ground-truth configurations available.",
    )
    if lines and lines[0] != "":
        lines.insert(0, "")
    return lines


def _build_answer_lines(answer: Any, section_label: str) -> list[str]:
    parsed, errors = _parse_topology_answer(answer)
    base: list[str] = []
    if parsed is not None:
        base.append(f"Tuples provided: {len(parsed)}")

    lines = _format_configuration_block(
        base,
        parsed,
        section_label=section_label,
        include_canonical=True,
        canonical_label=_CANONICAL_LABEL,
        errors=errors if errors else None,
        empty_message="No valid tuples parsed from model answer.",
    )
    if lines and lines[0] != "":
        lines.insert(0, "")
    return lines


def _render_topology_enumeration(
    record: Mapping[str, Any],
    answer: Any,
    detail: bool,
    *,
    show: bool | None = None,
) -> plt.Figure:
    fig = plt.figure(figsize=(12, 6))
    fig.suptitle("Topology Enumeration", fontsize=15, weight="bold")
    fig.patch.set_facecolor("white")

    _ = show

    answer_provided = answer is not None
    ax_truth, ax_answer = _layout_text_axes(fig, answer_provided)

    _prepare_text_axis(ax_truth, None, COLOURS["truth"])
    if ax_answer is not None:
        model_label = get_answer_label(record, default="Model answers")
        _prepare_text_axis(ax_answer, model_label, COLOURS["answer"])
    else:
        model_label = None

    truth_lines = _build_truth_lines(record.get("datagen_args", {}))

    _text_block(ax_truth, truth_lines, color=COLOURS["truth"])

    if not answer_provided or ax_answer is None:
        return fig

    answer_lines = _build_answer_lines(answer, model_label or "Model answers")

    _text_block(ax_answer, answer_lines, color=COLOURS["answer"])

    return fig


register_renderer("topology_enumeration", _render_topology_enumeration)
