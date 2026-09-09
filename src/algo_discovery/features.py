"""Feature extraction: numeric invariants and structural summaries.

These features feed downstream symbolic analysis — e.g. they can seed new
hypotheses or cluster sequences by behaviour. All functions are pure and
return hashable primitives for easy comparison/caching.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from fractions import Fraction

from algo_discovery.models import IntegerSequence

SequenceTransform = Callable[[IntegerSequence], list[float]]


def differences(values: list[int]) -> list[int]:
    """Consecutive differences of a flat int list."""
    return [values[i + 1] - values[i] for i in range(len(values) - 1)]


def first_differences(seq: IntegerSequence) -> list[int]:
    """a[i+1] - a[i] for consecutive terms."""
    return differences(list(seq.terms))


def second_differences(seq: IntegerSequence) -> list[int]:
    """Differences of the first differences."""
    return differences(first_differences(seq))


def ratios(seq: IntegerSequence) -> list[Fraction]:
    """a[i+1] / a[i] as exact rationals (terms after a 0 are skipped)."""
    out: list[Fraction] = []
    for i in range(len(seq) - 1):
        if seq[i] == 0:
            continue
        out.append(Fraction(seq[i + 1], seq[i]))
    return out


def sign_pattern(seq: IntegerSequence) -> tuple[str, ...]:
    """Per-term sign: '+' for positive, '-' for negative, '0' for zero."""
    return tuple("+" if t > 0 else "-" if t < 0 else "0" for t in seq.terms)


def monotonicity(seq: IntegerSequence) -> str:
    """One of: strictly-increasing, increasing, strictly-decreasing,
    decreasing, or mixed."""
    diffs = first_differences(seq)
    if all(d > 0 for d in diffs):
        return "strictly-increasing"
    if all(d >= 0 for d in diffs):
        return "increasing"
    if all(d < 0 for d in diffs):
        return "strictly-decreasing"
    if all(d <= 0 for d in diffs):
        return "decreasing"
    return "mixed"


def is_palindrome(seq: IntegerSequence) -> bool:
    """True when the sequence reads the same forwards and backwards."""
    return list(seq.terms) == list(reversed(seq.terms))


def growth_rate(seq: IntegerSequence) -> float:
    """Median absolute ratio between consecutive non-zero terms (0 if undefined)."""
    vals = [float(f) for f in ratios(seq) if f != 0]
    if not vals:
        return 0.0
    vals.sort()
    mid = len(vals) // 2
    if len(vals) % 2 == 1:
        return vals[mid]
    return (vals[mid - 1] + vals[mid]) / 2.0


def common_gcd(seq: IntegerSequence) -> int:
    """Gcd of the absolute values of all terms (0 for an all-zero sequence)."""
    result = 0
    for value in seq.terms:
        result = math.gcd(result, abs(value))
    return result


def invariants(seq: IntegerSequence) -> dict[str, object]:
    """A compact, hashable feature summary of a sequence."""
    return {
        "length": len(seq),
        "span": seq.span,
        "sign_pattern": sign_pattern(seq),
        "monotonicity": monotonicity(seq),
        "palindrome": is_palindrome(seq),
        "growth_rate": growth_rate(seq),
        "gcd": common_gcd(seq),
        "first_difference_set": tuple(set(first_differences(seq))),
        "second_difference_set": tuple(set(second_differences(seq))),
    }


def sequence_vector(seq: IntegerSequence) -> list[float]:
    """Normalized numeric vector for clustering: first differences scaled by span."""
    span = max(seq.span, 1)
    return [d / span for d in first_differences(seq)]


def transforms() -> dict[str, SequenceTransform]:
    """Named transforms producers can register/hypothesize around."""
    return {
        "differences": lambda s: [float(d) for d in first_differences(s)],
        "ratios": lambda s: [float(f) for f in ratios(s)],
    }