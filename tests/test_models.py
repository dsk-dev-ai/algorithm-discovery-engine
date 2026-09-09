"""Tests for the sequence/datamodel layer."""

import pytest

from algo_discovery.models import DiscoveryResult, HypothesisScore, IntegerSequence


class TestIntegerSequence:
    def test_requires_three_terms(self) -> None:
        with pytest.raises(ValueError):
            IntegerSequence((1, 2))
        with pytest.raises(ValueError):
            IntegerSequence(())
        with pytest.raises(ValueError):
            IntegerSequence([1, 5])

    def test_normalizes_to_tuple(self) -> None:
        seq = IntegerSequence([1, 2, 3])
        assert seq.terms == (1, 2, 3)
        assert len(seq) == 3

    def test_span(self) -> None:
        seq = IntegerSequence((1, 5, -2, 100))
        assert seq.span == 102

    def test_indexing(self) -> None:
        seq = IntegerSequence((1, 2, 3))
        assert seq[2] == 3


class TestHypothesisScore:
    def test_confidence_clamped(self) -> None:
        assert HypothesisScore("x", 3.0).confidence == 1.0
        assert HypothesisScore("x", -1.0).confidence == 0.0

    def test_rounded(self) -> None:
        assert HypothesisScore("x", 0.123456).confidence == 0.1235


class TestDiscoveryResult:
    def test_ranked_applies(self) -> None:
        seq = IntegerSequence((1, 2, 3))
        result = DiscoveryResult(sequence=seq)
        result.scores = [
            HypothesisScore("a", 0.4),
            HypothesisScore("b", 0.9),
            HypothesisScore("c", 0.2),
        ]
        by_name = {s.name: s.confidence for s in result.ranked}
        assert list(by_name) == ["b", "a", "c"]
        assert result.best is not None and result.best.name == "b"

    def test_best_none_when_empty(self) -> None:
        result = DiscoveryResult(sequence=IntegerSequence((1, 2, 3)))
        assert result.best is None
        assert result.ranked == []