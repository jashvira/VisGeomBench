"""Tests for topology enumeration problem: canonicalisation and solution retrieval."""

import pytest

from visual_geometry_bench.datagen.topology_enumeration import (
    canonicalize,
    get_solutions,
)


class TestCanonicalize:
    """Test canonicalisation (first-occurrence relabelling)."""

    def test_label_renaming_invariance(self):
        """Different labels, same pattern → same canonical form."""
        assert canonicalize((1, 0, 0, 0)) == (0, 1, 1, 1)
        assert canonicalize((7, 5, 5, 5)) == (0, 1, 1, 1)
        assert canonicalize((99, 42, 42, 42)) == (0, 1, 1, 1)

    def test_different_pattern(self):
        """Different pattern canonicalises correctly."""
        assert canonicalize((3, 3, 4, 4)) == (0, 0, 1, 1)
        assert canonicalize((0, 0, 1, 1)) == (0, 0, 1, 1)
        assert canonicalize((9, 9, 2, 2)) == (0, 0, 1, 1)

    def test_already_canonical(self):
        """Already canonical forms remain unchanged."""
        assert canonicalize((0, 1, 0, 2)) == (0, 1, 0, 2)
        assert canonicalize((0, 0, 1, 2)) == (0, 0, 1, 2)
        assert canonicalize((0, 1, 1, 1)) == (0, 1, 1, 1)


class TestGetSolutions:
    """Test solution retrieval and corner order permutation."""

    def test_correct_counts(self):
        """Verify correct number of solutions for each n_classes."""
        assert len(get_solutions(n_classes=2)) == 7
        assert len(get_solutions(n_classes=3)) == 4

    def test_corner_permutation(self):
        """Scrambled corner order returns reordered solutions."""
        canonical_order = ("bottom-left", "bottom-right", "top-right", "top-left")
        scrambled_order = ("top-right", "top-left", "bottom-left", "bottom-right")

        canonical_sols = get_solutions(n_classes=2, corner_order=canonical_order)
        scrambled_sols = get_solutions(n_classes=2, corner_order=scrambled_order)

        # Should have same count
        assert len(canonical_sols) == len(scrambled_sols)

        # Example: first canonical solution (1,0,0,0) in (BL,BR,TR,TL)
        # becomes (0,0,1,0) in (TR,TL,BL,BR) because we read TR→0, TL→0, BL→1, BR→0
        # Let's verify the permutation is actually applied
        assert canonical_sols != scrambled_sols  # Different orderings

        # Verify a specific case: canonical (1,0,0,0) means BL=1, BR=0, TR=0, TL=0
        # In scrambled order (TR,TL,BL,BR): position 0=TR, 1=TL, 2=BL, 3=BR
        # So we read: TR=0, TL=0, BL=1, BR=0 → (0,0,1,0)
        if (1, 0, 0, 0) in canonical_sols:
            assert (0, 0, 1, 0) in scrambled_sols

    def test_invalid_n_classes(self):
        """Invalid n_classes raises ValueError."""
        with pytest.raises(ValueError, match="n_classes must be 2 or 3"):
            get_solutions(n_classes=1)
        with pytest.raises(ValueError, match="n_classes must be 2 or 3"):
            get_solutions(n_classes=4)

    def test_invalid_corner_order(self):
        """Malformed corner_order raises ValueError."""
        with pytest.raises(ValueError, match="corner_order must be a permutation"):
            get_solutions(n_classes=2, corner_order=("invalid", "order", "bad", "names"))

        with pytest.raises(ValueError, match="corner_order must be a permutation"):
            get_solutions(n_classes=2, corner_order=("bottom-left", "bottom-left", "top-right", "top-left"))

