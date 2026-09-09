"""algo_discovery: automated discovery of mathematical patterns.

A framework that takes integer sequences and generates, scores, and ranks
candidate mathematical hypotheses (arithmetic/geometric progressions,
polynomial patterns, recurrences, and structural invariants).
"""

from algo_discovery.engine import DiscoveryEngine
from algo_discovery.hypotheses import BaseHypothesis
from algo_discovery.models import DiscoveryResult, IntegerSequence

__all__ = [
    "BaseHypothesis",
    "DiscoveryEngine",
    "DiscoveryResult",
    "IntegerSequence",
]

__version__ = "0.1.0"