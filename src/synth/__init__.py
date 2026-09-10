"""Algorithm synthesis & discovery (local).

The :mod:`synth` package searches for candidate algorithms from input/output
examples:

* :mod:`synth.grammar` — expression tree language + Python rendering.
* :mod:`synth.search` — grammar-based scanner enumeration and strategy
  templates (vote / seen / fib / circular-Kadane).
* :mod:`synth.corpus` — discovery targets, reference oracles, fuzz inputs.
* :mod:`synth.discovery` — orchestration, verification, novelty, reporting.

CLI:

    python -m synth discover            # full pass over every target
    python -m synth discover --smoke    # reduced budget (CI-friendly)
"""

from synth.discovery import discover

__version__ = "1.0.0"

__all__ = ["discover"]