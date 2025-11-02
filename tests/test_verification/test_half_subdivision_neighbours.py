"""Tests for half-subdivision neighbours verification."""

import pytest

from visual_geometry_bench.verification.half_subdivision_neighbours import (
    verify_half_subdivision_neighbours,
)


@pytest.fixture
def base_record():
    return {"ground_truth": ["00", "01", "10"]}


class TestVerification:
    """Test verification logic."""

    def test_verify_exact_match(self, base_record):
        """Exact match passes."""
        assert verify_half_subdivision_neighbours('["00", "01", "10"]', base_record)

    def test_verify_order_irrelevant(self, base_record):
        """Order doesn't matter."""
        assert verify_half_subdivision_neighbours('["10", "00", "01"]', base_record)

    def test_verify_comma_separated(self, base_record):
        """Comma-separated format works."""
        assert verify_half_subdivision_neighbours("00, 01, 10", base_record)

    def test_verify_unquoted_tokens(self):
        """Unquoted tokens work when no leading zeros."""
        record = {"ground_truth": ["0", "1", "10"]}
        assert verify_half_subdivision_neighbours("[0, 1, 10]", record)

    def test_verify_root_label(self):
        """Empty root label handled correctly."""
        record = {"ground_truth": ['""', "0", "1"]}
        assert verify_half_subdivision_neighbours('["", "0", "1"]', record)
        assert verify_half_subdivision_neighbours('["0", "1", ""]', record)

    def test_verify_missing_neighbour(self, base_record):
        """Missing neighbour fails."""
        assert not verify_half_subdivision_neighbours('["00", "01"]', base_record)

    def test_verify_extra_neighbour(self, base_record):
        """Extra neighbour fails."""
        assert not verify_half_subdivision_neighbours('["00", "01", "10", "11"]', base_record)

    def test_verify_duplicate_rejected(self, base_record):
        """Duplicates are rejected."""
        assert not verify_half_subdivision_neighbours('["00", "01", "10", "00"]', base_record)

    def test_verify_invalid_label(self, base_record):
        """Invalid characters rejected."""
        assert not verify_half_subdivision_neighbours('["00", "01", "abc"]', base_record)

    def test_verify_empty_output(self):
        """Empty output matches empty ground truth."""
        record = {"ground_truth": []}
        assert verify_half_subdivision_neighbours("[]", record)

    def test_verify_parse_failure(self, base_record):
        """Unparseable output fails."""
        assert not verify_half_subdivision_neighbours("not a valid format", base_record)

    def test_verify_return_diff_mode(self, base_record):
        """Diagnostic mode returns detailed diff."""
        result = verify_half_subdivision_neighbours('["00", "01"]', base_record, return_diff=True)
        assert isinstance(result, dict)
        assert not result["passed"]
        assert "10" in result["missing"]
        assert not result["extra"]


class TestEdgeCases:
    """Test edge cases."""

    def test_verify_whitespace_tolerant(self, base_record):
        """Whitespace is trimmed."""
        assert verify_half_subdivision_neighbours('[ " 00 " , " 01 " , " 10 " ]', base_record)

    def test_verify_newline_separated(self, base_record):
        """Newline-separated format works."""
        assert verify_half_subdivision_neighbours("00\n01\n10", base_record)

    def test_verify_non_string_output(self, base_record):
        """Non-string output fails gracefully."""
        assert not verify_half_subdivision_neighbours(None, base_record)
        assert not verify_half_subdivision_neighbours(123, base_record)
