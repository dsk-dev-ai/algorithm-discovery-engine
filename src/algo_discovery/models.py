"""Core data model for sequences and discovery results."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class IntegerSequence:
    """An immutable integer sequence.

    A sequence of at least three integers (the framework needs enough
    evidence to distinguish hypotheses). Empty and length-1/2 sequences are
    rejected at construction.
    """

    terms: tuple[int, ...]

    def __init__(self, terms: tuple[int, ...] | list[int]) -> None:
        if len(terms) < 3:
            raise ValueError("a sequence needs at least 3 terms")
        object.__setattr__(self, "terms", tuple(terms))

    def __len__(self) -> int:
        return len(self.terms)

    def __getitem__(self, index: int) -> int:
        return self.terms[index]

    @property
    def span(self) -> int:
        """max - min over the whole sequence (a crude trend measure)."""
        return max(self.terms) - min(self.terms)


@dataclass
class HypothesisScore:
    """Confidence of a single hypothesis against a sequence."""

    name: str
    confidence: float
    detail: str = ""
    prediction: int | None = None

    def __post_init__(self) -> None:
        self.confidence = round(max(0.0, min(1.0, self.confidence)), 4)


@dataclass
class DiscoveryResult:
    """Ranked set of hypotheses for one sequence."""

    sequence: IntegerSequence
    scores: list[HypothesisScore] = field(default_factory=list)

    @property
    def best(self) -> HypothesisScore | None:
        ranked = self.ranked
        return ranked[0] if ranked else None

    @property
    def ranked(self) -> list[HypothesisScore]:
        return sorted(self.scores, key=lambda s: s.confidence, reverse=True)