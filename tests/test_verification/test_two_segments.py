"""Verification tests for two-segment tasks."""

from visual_geometry_bench.datagen.two_segments import generate_dataset_record
from visual_geometry_bench.verification.two_segments import verify_two_segments


def _make_record(counts, **kwargs):
    datagen_args = {"counts": counts}
    datagen_args.update(kwargs)
    return generate_dataset_record(datagen_args=datagen_args)


def _lift_unit_segments(corners, unit_segments):
    (x0, y0), (x1, y1), _, (x3, y3) = corners
    axis_u = (x1 - x0, y1 - y0)
    axis_v = (x3 - x0, y3 - y0)

    def map_point(point):
        u, v = point
        return (x0 + u * axis_u[0] + v * axis_v[0], y0 + u * axis_u[1] + v * axis_v[1])

    return [
        (map_point(seg[0]), map_point(seg[1]))
        for seg in unit_segments
    ]


def test_verify_two_segments_pass_unit_square():
    record = _make_record({"triangle": 4})
    output = str([((0.0, 0.0), (1.0, 1.0)), ((0.0, 1.0), (1.0, 0.0))])
    assert verify_two_segments(output, record)


def test_verify_two_segments_counts_fail():
    record = _make_record({"triangle": 4})
    bad = str([((0.0, 0.0), (1.0, 0.0)), ((0.0, 1.0), (1.0, 1.0))])
    assert not verify_two_segments(bad, record)


def test_verify_two_segments_boundary_fail():
    record = _make_record({"triangle": 4})
    bad = str([((0.1, 0.1), (1.0, 1.0)), ((0.0, 1.0), (1.0, 0.0))])
    assert not verify_two_segments(bad, record)


def test_verify_two_segments_coordinate_grid_enforced():
    record = _make_record({"triangle": 4}, coordinate_grid=[0.0, 0.5, 1.0])
    ok = str([((0.0, 0.0), (1.0, 1.0)), ((0.0, 1.0), (1.0, 0.0))])
    assert verify_two_segments(ok, record)

    bad = str([((0.0, 0.0), (1.0, 1.0)), ((0.0, 1.0), (1.0, 0.3))])
    assert not verify_two_segments(bad, record)


def test_verify_two_segments_transformed_square():
    corners = [(2.0, 2.0), (3.0, 2.0), (3.0, 3.0), (2.0, 3.0)]
    record = _make_record({"triangle": 4}, corners=corners)
    output = str([((2.0, 2.0), (3.0, 3.0)), ((2.0, 3.0), (3.0, 2.0))])
    assert verify_two_segments(output, record)


def test_verify_two_segments_random_square_seed():
    record = _make_record({"triangle": 4}, square="random", square_seed=7)
    corners = record["datagen_args"]["corners"]
    unit_segments = [((0.0, 0.0), (1.0, 1.0)), ((0.0, 1.0), (1.0, 0.0))]
    lifted = _lift_unit_segments(corners, unit_segments)
    output = str(lifted)
    assert verify_two_segments(output, record)


def test_verify_two_segments_return_diff():
    record = _make_record({"triangle": 4})
    ok = str([((0.0, 0.0), (1.0, 1.0)), ((0.0, 1.0), (1.0, 0.0))])
    diff = verify_two_segments(ok, record, return_diff=True)
    assert diff["passed"] is True
    assert diff["errors"] == []


def test_verify_missing_counts_bool_mode():
    """Test verifier returns False when datagen_args.counts is missing."""
    record = {"datagen_args": {}}
    assert not verify_two_segments("[[(0.0, 0.0), (1.0, 1.0)], [(0.0, 1.0), (1.0, 0.0)]]", record)


def test_verify_missing_counts_diff_mode():
    """Test verifier returns diagnostic dict when datagen_args.counts is missing."""
    record = {"datagen_args": {}}
    diff = verify_two_segments("[[(0.0, 0.0), (1.0, 1.0)], [(0.0, 1.0), (1.0, 0.0)]]", record, return_diff=True)
    assert diff == {
        "passed": False,
        "errors": ["missing_counts"],
        "details": {"raw_output": "[[(0.0, 0.0), (1.0, 1.0)], [(0.0, 1.0), (1.0, 0.0)]]"},
    }


def test_verify_missing_counts_datagen_args_none():
    """Test verifier returns False when datagen_args is entirely missing."""
    record = {}
    assert not verify_two_segments("[[(0.0, 0.0), (1.0, 1.0)], [(0.0, 1.0), (1.0, 0.0)]]", record)


def test_verify_missing_counts_diff_mode_no_datagen_args():
    """Test verifier returns diagnostic dict when datagen_args is entirely missing."""
    record = {}
    diff = verify_two_segments("[[(0.0, 0.0), (1.0, 1.0)], [(0.0, 1.0), (1.0, 0.0)]]", record, return_diff=True)
    assert diff == {
        "passed": False,
        "errors": ["missing_counts"],
        "details": {"raw_output": "[[(0.0, 0.0), (1.0, 1.0)], [(0.0, 1.0), (1.0, 0.0)]]"},
    }
