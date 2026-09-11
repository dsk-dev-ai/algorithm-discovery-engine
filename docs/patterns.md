# Pattern discovery

The `algo_discovery` package ranks candidate hypotheses for an integer sequence
and scores them with confidence, an explanation, and (when applicable) a
predicted next term.

## CLI

```sh
uv run python -m algo_discovery 1 4 9 16 25
```

## Python API

```python
from algo_discovery import DiscoveryEngine

engine = DiscoveryEngine()

# Squares
result = engine.discover((1, 4, 9, 16, 25))
print(result.best.name)        # "quadratic"
print(result.best.prediction)  # 36

# Subset of hypotheses only
from algo_discovery.engine import hypotheses_by_name
engine = DiscoveryEngine(hypotheses=hypotheses_by_name(["arithmetic", "fibonacci-like"]))
```

## Built-in hypotheses

| Hypothesis            | Detects                                            |
| --------------------- | -------------------------------------------------- |
| `constant`            | identical terms                                    |
| `arithmetic`          | constant differences                               |
| `geometric`           | constant ratios                                    |
| `quadratic`           | constant second differences                        |
| `cubic`               | constant third differences                         |
| `powers-of-two`       | 2^n growth ladder                                  |
| `fibonacci-like`      | recurrence a(n) = a(n-1) + a(n-2)                  |
| `affine-recurrence`   | general linear recurrences                         |
| `prime`               | primes / prime-like patterns                       |
| `alternating-sign`    | sign oscillation                                  |

Each yields a confidence (0–1), an explanation string, and a predicted next term
when it fits.

## Feature extraction

Every hypothesis sees the same feature vector derived from the sequence:
differences, ratios, sign patterns, monotonicity, palindromicity, growth rate,
gcd, and a normalized numeric encoding.