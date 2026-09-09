# algorithm-discovery-engine

Experimental framework for **automated mathematical pattern discovery**: it
takes an integer sequence, generates candidate hypotheses (arithmetic and
geometric progressions, polynomial fits, recurrences, structural invariants),
scores each against the data, and returns a ranked result with optional
next-term predictions — plus a pure feature-extraction module for numeric and
structural analysis.

## Features

- **10 built-in hypotheses**: constant, arithmetic, geometric (exact rational
  ratios), quadratic, cubic, powers-of-two, Fibonacci-like, affine linear
  recurrence (`a[i] = p·a[i-1] + q`), prime, and alternating-sign.
- **Ranked results**: each hypothesis yields a confidence in `[0, 1]`, a human
  explanation, and a predicted next term when it fits.
- **Feature extraction**: first/second differences, exact rational ratios,
  sign patterns, monotonicity, palindromicity, growth rate, gcd, and a
  normalized numeric vector for clustering.
- **Pluggable**: register your own hypotheses via `BaseHypothesis` or filter
  to a named subset.
- Fully type-checked (mypy strict), linted (ruff), and unit-tested (pytest).

## Install & use

```python
from algo_discovery import DiscoveryEngine

engine = DiscoveryEngine()

# Squares
result = engine.discover((1, 4, 9, 16, 25))
print(result.best.name)       # "quadratic"
print(result.best.prediction) # 36

# Everything ranked, highest confidence first
for s in result.scores:
    print(f"{s.name:16s} {s.confidence:1.2f}  {s.detail}")

# Subset of hypotheses only
from algo_discovery.engine import hypotheses_by_name
engine = DiscoveryEngine(hypotheses=hypotheses_by_name(["arithmetic", "fibonacci-like"]))
```

## Feature extraction

```python
from algo_discovery import IntegerSequence
from algo_discovery.features import invariants, sequence_vector

seq = IntegerSequence((1, 4, 9, 16))
print(invariants(seq))        # {'length': 4, 'monotonicity': 'strictly-increasing', ...}
print(sequence_vector(seq))   # normalized first differences
```

## CLI

```sh
uv run python -m algo_discovery 1 4 9 16
```

Prints the ranked hypotheses for the given sequence.

## Development

Requires Python ≥ 3.10 and [uv](https://docs.astral.sh/uv/).

```sh
uv sync --group dev
uv run pytest -q      # tests
uv run ruff check src tests
uv run mypy -p algo_discovery
```

## Structure

```
src/algo_discovery/
  models.py      IntegerSequence, HypothesisScore, DiscoveryResult
  hypotheses.py  10 built-in hypotheses + registry
  engine.py      DiscoveryEngine (run + rank)
  features.py    numeric/structural feature extraction
tests/           unit tests (models, hypotheses, engine, features)
```

## License

MIT — see [LICENSE](LICENSE).