"""Tests for the discovery engine."""

import pytest

from algo_discovery.engine import (
    DiscoveryEngine,
    EngineConfig,
    default_engine,
    hypotheses_by_name,
)
from algo_discovery.hypotheses import ArithmeticHypothesis, ConstantHypothesis


class TestDiscoveryEngine:
    def test_best_hypothesis_for_arithmetic(self) -> None:
        engine = default_engine()
        result = engine.discover((1, 3, 5, 7, 9))
        assert result.best is not None
        assert result.best.name == "arithmetic"
        assert result.best.prediction == 11

    def test_constant_sequence(self) -> None:
        engine = default_engine()
        result = engine.discover((4, 4, 4, 4))
        assert result.best is not None
        assert result.best.name == "constant"

    def test_zero_confidence_dropped_by_default(self) -> None:
        engine = default_engine()
        result = engine.discover((1, 2, 4, 8))
        assert all(s.confidence > 0.0 for s in result.scores)

    def test_can_keep_zeros(self) -> None:
        engine = DiscoveryEngine(config=EngineConfig(drop_zero=False))
        result = engine.discover((1, 2, 4, 8))
        assert any(s.confidence == 0.0 for s in result.scores)

    def test_custom_hypotheses_only(self) -> None:
        engine = DiscoveryEngine(hypotheses=[ConstantHypothesis()])
        assert engine.supported_names == ["constant"]
        result = engine.discover((5, 5, 5))
        assert result.best is not None and result.best.name == "constant"

    def test_result_ranked_descending(self) -> None:
        engine = default_engine()
        result = engine.discover((2, 6, 18, 54))
        confidences = [s.confidence for s in result.scores]
        assert confidences == sorted(confidences, reverse=True)

    def test_tuple_or_list_input(self) -> None:
        engine = default_engine()
        a = engine.discover((1, 2, 3))
        b = engine.discover([1, 2, 3])
        assert a.sequence == b.sequence

    def test_repr(self) -> None:
        engine = DiscoveryEngine(hypotheses=[ArithmeticHypothesis()])
        assert "DiscoveryEngine" in repr(engine)


class TestHypothesesByName:
    def test_selects_by_name(self) -> None:
        hs = hypotheses_by_name(["arithmetic", "constant"])
        names = [h.name for h in hs]
        assert names == ["arithmetic", "constant"]

    def test_unknown_raises(self) -> None:
        with pytest.raises(KeyError):
            hypotheses_by_name(["nope"])


class TestSequenceValidation:
    def test_short_sequence_rejected_with_clear_error(self) -> None:
        engine = default_engine()
        with pytest.raises(ValueError, match="at least 3"):
            engine.discover((1, 2))