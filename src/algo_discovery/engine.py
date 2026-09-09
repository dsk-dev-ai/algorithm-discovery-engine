"""Discovery engine: run hypotheses over a sequence and rank the results."""

from __future__ import annotations

from dataclasses import dataclass

from algo_discovery.hypotheses import (
    ALL_HYPOTHESES,
    BaseHypothesis,
    build_hypotheses,
)
from algo_discovery.models import DiscoveryResult, IntegerSequence


@dataclass
class EngineConfig:
    """Tuning knobs for the discovery run."""

    max_ties_kept: int | None = None
    drop_zero: bool = True


class DiscoveryEngine:
    """Ranks all candidate hypotheses for an integer sequence."""

    def __init__(
        self,
        hypotheses: list[BaseHypothesis] | None = None,
        config: EngineConfig | None = None,
    ) -> None:
        self.hypotheses = hypotheses if hypotheses is not None else build_hypotheses()
        self.config = config or EngineConfig()

    def discover(self, terms: tuple[int, ...] | list[int]) -> DiscoveryResult:
        """Evaluate every hypothesis against the given sequence."""
        seq = IntegerSequence(terms)
        scores = [h.detect(seq) for h in self.hypotheses]
        if self.config.drop_zero:
            scores = [s for s in scores if s.confidence > 0.0]
        result = DiscoveryResult(sequence=seq, scores=scores)
        result.scores = result.ranked
        return result

    @property
    def supported_names(self) -> list[str]:
        return [h.name for h in self.hypotheses]

    def __repr__(self) -> str:
        kinds = ", ".join(h.__class__.__name__ for h in self.hypotheses)
        return f"<DiscoveryEngine hypotheses=[{kinds}]>"


def default_engine() -> DiscoveryEngine:
    """Engine over the standard built-in hypothesis set."""
    return DiscoveryEngine()


def hypotheses_by_name(names: list[str]) -> list[BaseHypothesis]:
    """Instantiate the named built-in hypotheses only."""
    by_name = {cls().name: cls for cls in ALL_HYPOTHESES}
    missing = [n for n in names if n not in by_name]
    if missing:
        raise KeyError(f"unknown hypotheses: {', '.join(missing)}")
    return [by_name[n]() for n in names]