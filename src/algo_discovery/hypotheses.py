"""Built-in mathematical hypotheses.

Each hypothesis inspects an :class:`IntegerSequence` and reports a confidence
in [0, 1] plus an optional next-term prediction.
"""

from __future__ import annotations

from fractions import Fraction

from algo_discovery.models import HypothesisScore, IntegerSequence


class BaseHypothesis:
    """Abstract base for a sequence hypothesis."""

    name = "base"
    description = ""

    def detect(self, seq: IntegerSequence) -> HypothesisScore:
        raise NotImplementedError


class ConstantHypothesis(BaseHypothesis):
    """All terms are equal."""

    name = "constant"

    def detect(self, seq: IntegerSequence) -> HypothesisScore:
        equal = all(t == seq[0] for t in seq.terms)
        conf = 1.0 if equal else 0.0
        pred = seq[0] if equal else None
        return HypothesisScore(self.name, conf, "c, c, c, ...", pred)


class ArithmeticHypothesis(BaseHypothesis):
    """Constant first difference (a, a+d, a+2d, ...)."""

    name = "arithmetic"

    def detect(self, seq: IntegerSequence) -> HypothesisScore:
        diffs = {seq[i + 1] - seq[i] for i in range(len(seq) - 1)}
        if len(diffs) == 1:
            d = next(iter(diffs))
            return HypothesisScore(
                self.name, 1.0, f"a[i] = a[0] + {d}·i", seq[-1] + d
            )
        return HypothesisScore(self.name, 0.0)


class GeometricHypothesis(BaseHypothesis):
    """Constant ratio (a, a·r, a·r², ...) over the rationals."""

    name = "geometric"

    def detect(self, seq: IntegerSequence) -> HypothesisScore:
        if any(t == 0 for t in seq.terms):
            return HypothesisScore(self.name, 0.0)
        ratios = {
            Fraction(seq[i + 1], seq[i]) for i in range(len(seq) - 1)
        }
        if len(ratios) == 1:
            r = next(iter(ratios))
            num, den = r.numerator, r.denominator
            pred = seq[-1] * num // den if (seq[-1] * num) % den == 0 else None
            return HypothesisScore(
                self.name, 1.0, f"a[i] = a[0] · ({num}/{den})^i", pred,
            )
        return HypothesisScore(self.name, 0.0)


class QuadraticHypothesis(BaseHypothesis):
    """Constant non-zero second difference => degree-2 polynomial in the index."""

    name = "quadratic"

    def detect(self, seq: IntegerSequence) -> HypothesisScore:
        if len(seq) < 3:
            return HypothesisScore(self.name, 0.0)
        first = [seq[i + 1] - seq[i] for i in range(len(seq) - 1)]
        second = {first[i + 1] - first[i] for i in range(len(first) - 1)}
        if len(second) == 1:
            d2 = next(iter(second))
            if d2 == 0:
                # zero curvature is just a linear (arithmetic) pattern
                return HypothesisScore(self.name, 0.0)
            ndiff = first[-1] + d2
            return HypothesisScore(self.name, 1.0, f"Δ² = {d2}", seq[-1] + ndiff)
        return HypothesisScore(self.name, 0.0)


class PowerOfTwoHypothesis(BaseHypothesis):
    """Terms are exact powers of 2 (a[i] = 2^k)."""

    name = "powers-of-two"

    @staticmethod
    def _is_power_of_two(value: int) -> bool:
        return value > 0 and (value & (value - 1)) == 0

    def detect(self, seq: IntegerSequence) -> HypothesisScore:
        if any(not self._is_power_of_two(t) for t in seq.terms):
            return HypothesisScore(self.name, 0.0)
        # consecutive powers of 2: each term is double the previous
        consecutive = all(
            seq.terms[i + 1] == 2 * seq.terms[i] for i in range(len(seq) - 1)
        )
        return HypothesisScore(self.name, 1.0, "powers of 2",
                               2 * seq[-1] if consecutive else None)


class CubicHypothesis(BaseHypothesis):
    """Constant third difference => degree-3 polynomial in the index."""

    name = "cubic"

    def detect(self, seq: IntegerSequence) -> HypothesisScore:
        if len(seq) < 4:
            return HypothesisScore(self.name, 0.0)

        def diffs(values: list[int]) -> list[int]:
            return [values[i + 1] - values[i] for i in range(len(values) - 1)]

        first = diffs(list(seq.terms))
        second = diffs(first)
        third = diffs(second)
        if len(set(third)) == 1:
            d3 = third[0]
            if d3 == 0:
                return HypothesisScore(self.name, 0.0)
            nd2 = second[-1] + d3
            nd1 = first[-1] + nd2
            return HypothesisScore(self.name, 1.0, f"Δ³ = {d3}", seq[-1] + nd1)
        return HypothesisScore(self.name, 0.0)


class FibonacciLikeHypothesis(BaseHypothesis):
    """Every term (past the first two) equals the sum of its two predecessors."""

    name = "fibonacci-like"

    def detect(self, seq: IntegerSequence) -> HypothesisScore:
        terms = seq.terms
        for i in range(2, len(terms)):
            if terms[i] != terms[i - 1] + terms[i - 2]:
                return HypothesisScore(self.name, 0.0)
        return HypothesisScore(self.name, 1.0, "a[i] = a[i-1] + a[i-2]",
                                terms[-1] + terms[-2])


class RecurrenceLinearHypothesis(BaseHypothesis):
    """Best-fit linear recurrence a[i] = p·a[i-1] + q (solve exactly when possible)."""

    name = "linear-recurrence"

    def detect(self, seq: IntegerSequence) -> HypothesisScore:
        terms = seq.terms
        # solve for (p, q) from the first two constraints
        # a1 = p*a0 + q ; a2 = p*a1 + q  =>  p = (a2 - a1)/(a1 - a0)
        denom = terms[1] - terms[0]
        if denom == 0:
            if terms[2] == terms[1]:
                return HypothesisScore(
                    self.name, 1.0, "a[i] = a[i-1] (constant)", terms[-1]
                )
            return HypothesisScore(self.name, 0.0)
        if (terms[2] - terms[1]) % denom != 0:
            return HypothesisScore(self.name, 0.0)
        p = (terms[2] - terms[1]) // denom
        q = terms[1] - p * terms[0]
        for i in range(3, len(terms)):
            if terms[i] != p * terms[i - 1] + q:
                return HypothesisScore(self.name, 0.0)
        return HypothesisScore(
            self.name, 1.0, f"a[i] = {p}·a[i-1] + {q}",
            p * terms[-1] + q,
        )


class PrimeHypothesis(BaseHypothesis):
    """Terms are consecutive (or non-decreasing) primes."""

    name = "primes"

    @staticmethod
    def _is_prime(value: int) -> bool:
        if value < 2:
            return False
        if value < 4:
            return True
        if value % 2 == 0 or value % 3 == 0:
            return False
        i = 5
        while i * i <= value:
            if value % i == 0 or value % (i + 2) == 0:
                return False
            i += 6
        return True

    def detect(self, seq: IntegerSequence) -> HypothesisScore:
        if any(not self._is_prime(t) for t in seq.terms):
            return HypothesisScore(self.name, 0.0)
        consecutive = all(
            all(not self._is_prime(c) for c in range(seq[i] + 1, seq[i + 1]))
            for i in range(len(seq) - 1)
        ) if all(seq[i] < seq[i + 1] for i in range(len(seq) - 1)) else False
        conf = 1.0 if consecutive else 0.7
        return HypothesisScore(self.name, conf, "all terms are prime")


class AlternatingHypothesis(BaseHypothesis):
    """Strictly alternating signs with non-decreasing magnitudes."""

    name = "alternating"

    def detect(self, seq: IntegerSequence) -> HypothesisScore:
        mags = [abs(t) for t in seq.terms]
        signs = [t > 0 for t in seq.terms]
        strictly_alt = all(signs[i] != signs[i + 1] for i in range(len(signs) - 1))
        monotone_mag = all(mags[i] <= mags[i + 1] for i in range(len(mags) - 1))
        conf = 1.0 if strictly_alt and monotone_mag else 0.0
        mag_growth = mags[-1] - mags[-2]
        pred = seq[-1] - mag_growth if signs[-1] else seq[-1] + mag_growth
        return HypothesisScore(self.name, conf, "sign alternates", pred)


ALL_HYPOTHESES: tuple[type[BaseHypothesis], ...] = (
    ConstantHypothesis,
    ArithmeticHypothesis,
    GeometricHypothesis,
    QuadraticHypothesis,
    CubicHypothesis,
    PowerOfTwoHypothesis,
    FibonacciLikeHypothesis,
    RecurrenceLinearHypothesis,
    PrimeHypothesis,
    AlternatingHypothesis,
)


def build_hypotheses(extra: list[BaseHypothesis] | None = None) -> list[BaseHypothesis]:
    """Instantiate the standard hypothesis set plus any extras."""
    instances: list[BaseHypothesis] = [cls() for cls in ALL_HYPOTHESES]
    if extra:
        instances.extend(extra)
    return instances


def describe(hypothesis: BaseHypothesis) -> str:
    """Human description used by the CLI/reporter."""
    return f"{hypothesis.name}: {hypothesis.description or hypothesis.name}"