"""Tests for the built-in hypotheses."""

from algo_discovery.hypotheses import (
    AlternatingHypothesis,
    ArithmeticHypothesis,
    ConstantHypothesis,
    CubicHypothesis,
    FibonacciLikeHypothesis,
    GeometricHypothesis,
    PowerOfTwoHypothesis,
    PrimeHypothesis,
    QuadraticHypothesis,
    RecurrenceLinearHypothesis,
    build_hypotheses,
)
from algo_discovery.models import IntegerSequence


def _best(hypothesis, seq: IntegerSequence):
    return hypothesis.detect(seq)


class TestConstant:
    def test_constant_detected(self) -> None:
        s = _best(ConstantHypothesis(), IntegerSequence((7, 7, 7, 7)))
        assert s.confidence == 1.0
        assert s.prediction == 7

    def test_non_constant_rejected(self) -> None:
        s = _best(ConstantHypothesis(), IntegerSequence((1, 2, 3)))
        assert s.confidence == 0.0


class TestArithmetic:
    def test_detected(self) -> None:
        s = _best(ArithmeticHypothesis(), IntegerSequence((1, 3, 5, 7)))
        assert s.confidence == 1.0
        assert s.prediction == 9

    def test_rejected_when_not_linear(self) -> None:
        s = _best(ArithmeticHypothesis(), IntegerSequence((1, 2, 4)))
        assert s.confidence == 0.0


class TestGeometric:
    def test_detected(self) -> None:
        s = _best(GeometricHypothesis(), IntegerSequence((3, 6, 12, 24)))
        assert s.confidence == 1.0
        assert s.prediction == 48

    def test_rational_ratio(self) -> None:
        s = _best(GeometricHypothesis(), IntegerSequence((2, 3, 3)))  # ratio 3/2
        assert s.prediction is None  # 3 * 3/2 is not integral

    def test_zero_terms_rejected(self) -> None:
        s = _best(GeometricHypothesis(), IntegerSequence((0, 2, 4)))
        assert s.confidence == 0.0


class TestQuadratic:
    def test_detected(self) -> None:
        # n^2: 1, 4, 9, 16
        s = _best(QuadraticHypothesis(), IntegerSequence((1, 4, 9, 16)))
        assert s.confidence == 1.0
        assert s.prediction == 25

    def test_arithmetic_is_not_quadratic(self) -> None:
        s = _best(QuadraticHypothesis(), IntegerSequence((1, 2, 3)))
        assert s.confidence == 0.0


class TestCubic:
    def test_detected(self) -> None:
        # n^3: 1, 8, 27, 64, 125
        s = _best(CubicHypothesis(), IntegerSequence((1, 8, 27, 64, 125)))
        assert s.confidence == 1.0
        assert s.prediction == 216


class TestPowerOfTwo:
    def test_consecutive_powers(self) -> None:
        s = _best(PowerOfTwoHypothesis(), IntegerSequence((2, 4, 8, 16)))
        assert s.confidence == 1.0
        assert s.prediction == 32

    def test_all_powers_but_not_consecutive(self) -> None:
        s = _best(PowerOfTwoHypothesis(), IntegerSequence((2, 8, 32)))
        assert s.confidence == 1.0
        assert s.prediction is None

    def test_non_power_rejected(self) -> None:
        s = _best(PowerOfTwoHypothesis(), IntegerSequence((2, 3, 5)))
        assert s.confidence == 0.0


class TestFibonacciLike:
    def test_detected(self) -> None:
        s = _best(FibonacciLikeHypothesis(), IntegerSequence((1, 1, 2, 3, 5)))
        assert s.confidence == 1.0
        assert s.prediction == 8

    def test_rejected(self) -> None:
        s = _best(FibonacciLikeHypothesis(), IntegerSequence((1, 2, 4)))
        assert s.confidence == 0.0


class TestLinearRecurrence:
    def test_pq_recurrence(self) -> None:
        # a[i] = 2*a[i-1] + 1 : 1, 3, 7, 15, 31
        s = _best(RecurrenceLinearHypothesis(), IntegerSequence((1, 3, 7, 15, 31)))
        assert s.confidence == 1.0
        assert s.prediction == 63

    def test_constant_covered(self) -> None:
        s = _best(RecurrenceLinearHypothesis(), IntegerSequence((5, 5, 5)))
        assert s.confidence == 1.0

    def test_rejected(self) -> None:
        s = _best(RecurrenceLinearHypothesis(), IntegerSequence((1, 2, 5, 10)))
        assert s.confidence == 0.0


class TestPrime:
    def test_consecutive_primes(self) -> None:
        s = _best(PrimeHypothesis(), IntegerSequence((2, 3, 5, 7, 11)))
        assert s.confidence == 1.0

    def test_primes_but_not_consecutive(self) -> None:
        s = _best(PrimeHypothesis(), IntegerSequence((5, 11, 13)))
        assert s.confidence == 0.7

    def test_non_prime_rejected(self) -> None:
        s = _best(PrimeHypothesis(), IntegerSequence((2, 3, 6)))
        assert s.confidence == 0.0


class TestAlternating:
    def test_alternating_monotone(self) -> None:
        s = _best(AlternatingHypothesis(), IntegerSequence((1, -2, 4, -8)))
        assert s.confidence == 1.0

    def test_no_alternation_rejected(self) -> None:
        s = _best(AlternatingHypothesis(), IntegerSequence((1, 2, 3)))
        assert s.confidence == 0.0


class TestRegistry:
    def test_build_hypotheses_covers_all(self) -> None:
        names = [h.name for h in build_hypotheses()]
        assert "arithmetic" in names
        assert "fibonacci-like" in names
        assert "primes" in names
        assert len(names) == 10

    def test_extras_appended(self) -> None:
        extra = [ArithmeticHypothesis()]
        assert len(build_hypotheses(extra)) == 11