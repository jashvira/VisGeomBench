"""Tests for the visualisations package and CLI."""

from __future__ import annotations

import json
from importlib import reload
from pathlib import Path

import matplotlib.pyplot as plt
import pytest

from scripts.render_eval_visuals import render_results
from visualisations.render import register_renderer, visualise_record

from visual_geometry_bench.datagen.convex_hull_tasks import (
    _compute_convex_hull,
    _hull_to_canonical_indices,
    _to_points as convex_to_points,
)
from visual_geometry_bench.datagen.delaunay_tasks import (
    _compute_delaunay_triangulation,
    _to_points as delaunay_to_points,
)


@pytest.fixture(autouse=True)
def clear_renderers(monkeypatch):
    monkeypatch.setattr("visualisations.render._RENDERERS", {})
    monkeypatch.setattr("visualisations.render._STYLE_APPLIED", False)


@pytest.fixture
def renderers_ready():
    import visualisations.geometry as geom
    import visualisations.topology as topo
    import visualisations.two_segments as two_seg
    import visualisations.shikaku as shikaku
    import visualisations.half_subdivision as half_sub

    reload(geom)
    reload(topo)
    reload(two_seg)
    reload(shikaku)
    reload(half_sub)
    yield
    plt.close("all")


def dummy_renderer(record, answer, detail):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title(record["id"])
    if answer is not None:
        ax.text(0.5, 0.5, str(answer), ha="center")
    return fig


def test_visualise_record_dispatch_and_save(tmp_path: Path) -> None:
    register_renderer("dummy_task", dummy_renderer)

    record = {
        "id": "abc123",
        "metadata": {"problem_type": "dummy_task"},
    }

    result = visualise_record(record, answer={"foo": 1}, reward=0.5)
    assert isinstance(result, plt.Figure)
    assert result.axes[0].get_title() == "abc123"

    save_dir = tmp_path / "viz"
    visualise_record(record, answer=None, save_dir=save_dir, reward=1.0, output_stub="007")

    saved_file = save_dir / "007.png"
    assert saved_file.exists()


def test_convex_hull_renderer_generates_figure(renderers_ready):
    datagen_args = {"num_points": 6, "seed": 11}
    points = convex_to_points(datagen_args)
    hull = _compute_convex_hull(points)
    assert hull is not None
    hull_indices = _hull_to_canonical_indices(hull)

    record = {
        "id": "convex",
        "metadata": {"problem_type": "convex_hull_ordering"},
        "datagen_args": datagen_args,
        "ground_truth": hull_indices,
    }

    fig = visualise_record(record, hull_indices, reward=1.0)
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 2
    plt.close(fig)


def test_delaunay_renderer_generates_figure(renderers_ready):
    datagen_args = {"num_points": 8, "seed": 3}
    points = delaunay_to_points(datagen_args)
    triangulation = _compute_delaunay_triangulation(points)

    record = {
        "id": "delaunay",
        "metadata": {"problem_type": "delaunay_triangulation"},
        "datagen_args": datagen_args,
        "ground_truth": triangulation,
    }

    fig = visualise_record(record, triangulation, reward=0.0)
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 2
    plt.close(fig)


def test_topology_renderers_generate_figures(renderers_ready):
    edge_record = {
        "id": "top-edge",
        "metadata": {"problem_type": "topology_edge_tasks"},
        "datagen_args": {
            "corner_order": ["bottom-left", "bottom-right", "top-right", "top-left"],
            "cases": [
                [1, 1, 1, 1],
                [1, 2, 2, 1],
            ],
        },
        "ground_truth": [[], [[1, 3]]],
    }

    edge_fig = visualise_record(edge_record, edge_record["ground_truth"], reward=1.0)
    assert isinstance(edge_fig, plt.Figure)
    plt.close(edge_fig)

    enumeration_record = {
        "id": "top-enum",
        "metadata": {"problem_type": "topology_enumeration"},
        "prompt": "List configurations",
        "ground_truth": [[0, 1, 0, 1], [1, 0, 0, 1]],
    }

    enum_fig = visualise_record(enumeration_record, enumeration_record["ground_truth"], reward=0.5)
    assert isinstance(enum_fig, plt.Figure)
    plt.close(enum_fig)


def test_two_segments_renderer_generates_figure(renderers_ready):
    record = {
        "id": "two-seg",
        "metadata": {"problem_type": "two_segments"},
        "datagen_args": {
            "counts": {"triangle": 4},
            "square": "unit",
            "snap_decimals": 2,
        },
        "ground_truth": [{"shape": "triangle", "count": 4}],
    }
    answer = [((0.0, 0.0), (1.0, 1.0)), ((1.0, 0.0), (0.0, 1.0))]

    fig = visualise_record(record, answer, reward=0.75)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_render_results_generates_output(tmp_path: Path, renderers_ready) -> None:
    record = {
        "id": "two_seg_run",
        "metadata": {"problem_type": "two_segments"},
        "datagen_args": {
            "counts": {"triangle": 4},
            "square": "unit",
            "snap_decimals": 2,
        },
        "ground_truth": [{"shape": "triangle", "count": 4}],
    }

    run_dir = tmp_path / "run"
    run_dir.mkdir()
    results_path = run_dir / "results.jsonl"
    row = {
        "info": {
            "raw_record": record,
            "raw_answer": "[((0, 0), (1, 1)), ((1, 0), (0, 1))]",
        },
        "completion": [{"content": "[((0, 0), (1, 1)), ((1, 0), (0, 1))]"}],
    }
    results_path.write_text(json.dumps(row) + "\n", encoding="utf-8")

    output_dir = tmp_path / "out"
    render_results(results_path, output_dir, fmt="png", detail=False, overwrite=True)

    expected_file = output_dir / "run" / "001.png"
    assert expected_file.exists()
    plt.close("all")


def test_shikaku_renderer_generates_figure(renderers_ready):
    record = {
        "id": "shikaku-test",
        "metadata": {"problem_type": "shikaku_rectangles"},
        "datagen_args": {
            "width": 5,
            "height": 5,
            "numbers": [
                [4, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 3, 0, 0],
                [0, 2, 0, 0, 0],
                [0, 0, 0, 0, 0],
            ],
        },
        "ground_truth": [[0, 0, 1, 1], [0, 2, 2, 2], [3, 1, 4, 4]],
    }
    fig = visualise_record(record, record["ground_truth"])
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 2
    plt.close(fig)


def test_half_subdivision_renderer_generates_figure(renderers_ready):
    record = {
        "id": "half-sub-test",
        "metadata": {"problem_type": "half_subdivision_neighbours"},
        "datagen_args": {
            "dim": "D2",
            "max_depth": 4,
            "min_depth": 2,
            "split_prob": 0.7,
            "start_axis": "x",
            "tree_seed": 42,
            "target_leaf": "A",
        },
        "ground_truth": ["B", "C"],
    }
    answer = ["B", "D"]
    fig = visualise_record(record, answer)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)
