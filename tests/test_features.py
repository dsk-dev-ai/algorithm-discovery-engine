"""Tests for feature extraction."""

from fractions import Fraction

from algo_discovery.features import (
    common_gcd,
    differences,
    first_differences,
    growth_rate,
    invariants,
    is_palindrome,
    monotonicity,
    ratios,
    second_differences,
    sequence_vector,
    sign_pattern,
    transforms,
)
from algo_discovery.models import IntegerSequence


class TestDifferences:
    def test_first(self) -> None:
        seq = IntegerSequence((1, 3, 6, 10))
        assert first_differences(seq) == [2, 3, 4]

    def test_second(self) -> None:
        seq = IntegerSequence((1, 4, 9, 16))
        assert second_differences(seq) == [2, 2]

    def test_flat_helper(self) -> None:
        assert differences([1, 2, 4]) == [1, 2]


class TestRatios:
    def test_exact(self) -> None:
        seq = IntegerSequence((2, 3, 6))
        assert ratios(seq) == [Fraction(3, 2), Fraction(2, 1)]

    def test_zero_skipped(self) -> None:
        seq = IntegerSequence((0, 4, 12))
        assert ratios(seq) == [Fraction(3, 1)]


class TestSignPattern:
    def test_mixed(self) -> None:
        seq = IntegerSequence((1, -2, 0, 4))
        assert sign_pattern(seq) == ("+", "-", "0", "+")


class TestMonotonicity:
    def test_strict_increasing(self) -> None:
        assert monotonicity(IntegerSequence((1, 2, 5))) == "strictly-increasing"

    def test_increasing(self) -> None:
        assert monotonicity(IntegerSequence((1, 1, 2))) == "increasing"

    def test_decreasing(self) -> None:
        assert monotonicity(IntegerSequence((5, 3, 1))) == "strictly-decreasing"

    def test_mixed(self) -> None:
        assert monotonicity(IntegerSequence((1, 3, 2))) == "mixed"


class TestPalindrome:
    def test_is_palindrome(self) -> None:
        assert is_palindrome(IntegerSequence((1, 2, 3, 2, 1)))

    def test_not_palindrome(self) -> None:
        assert not is_palindrome(IntegerSequence((1, 2, 3, 2, 2)))


class TestGrowthRate:
    def test_median_ratio(self) -> None:
        seq = IntegerSequence((1, 2, 4, 8))
        assert growth_rate(seq) == 2.0

    def test_no_ratios(self) -> None:
        assert growth_rate(IntegerSequence((0, 0, 0))) == 0.0


class TestCommonGcd:
    def test_gcd(self) -> None:
        assert common_gcd(IntegerSequence((12, 18, 30))) == 6

    def test_all_zero(self) -> None:
        assert common_gcd(IntegerSequence((0, 0, 0))) == 0


class TestInvariants:
    def test_summary_contains_keys(self) -> None:
        info = invariants(IntegerSequence((2, 4, 8, 16)))
        assert set(info) == {
            "length",
            "span",
            "sign_pattern",
            "monotonicity",
            "palindrome",
            "growth_rate",
            "gcd",
            "first_difference_set",
            "second_difference_set",
        }
        assert info["length"] == 4
        assert info["gcd"] == 2

    def test_first_diff_set(self) -> None:
        info = invariants(IntegerSequence((1, 3, 5, 7)))
        assert info["first_difference_set"] == (2,)


class TestSequenceVector:
    def test_normalized(self) -> None:
        vec = sequence_vector(IntegerSequence((0, 2, 4, 6)))
        span = 6
        assert vec == [2 / span, 2 / span, 2 / span]

    def test_zero_span_guard(self) -> None:
        assert sequence_vector(IntegerSequence((1, 1, 1))) == [0.0, 0.0]


class TestTransforms:
    def test_registered(self) -> None:
        ts = transforms()
        seq = IntegerSequence((1, 3, 6))
        assert ts["differences"](seq) == [2.0, 3.0]
        assert ts["ratios"](seq) == [3.0, 2.0]