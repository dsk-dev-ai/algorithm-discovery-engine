# algorithm-discovery-engine

[![CI](https://github.com/dsk-dev-ai/algorithm-discovery-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/dsk-dev-ai/algorithm-discovery-engine/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A multi-language algorithms & data structures solving engine.** The same
catalog of problems and data structures is implemented, tested, and benchmarked
in **Java**, **C++**, **Rust**, and **Python** (regular + advanced tiers), with a
single `catalog/problems.json` as the source of truth and identical generated
test vectors across every language.

It also retains the original **automated mathematical pattern discovery**
framework: feed it an integer sequence and it generates, scores, and ranks
candidate hypotheses (arithmetic/geometric progressions, polynomial fits,
recurrences, structural invariants) with optional next-term predictions.

## The solving engine

### Catalog

`catalog/problems.json` is the single source of truth. Every problem/structure
carries shared test vectors that are checked in **all four languages**.

**Algorithms (10):** `two_sum`, `binary_search`, `merge_sort`, `quick_sort`,
`max_subarray`, `lcs` (longest common subsequence), `knapsack_01`,
`edit_distance`, `graph_bfs`, `graph_dfs`.

**Data structures (6):** `stack`, `queue`, `linked_list`, `bst` (binary search
tree), `trie`, `min_heap`.

### Language tiers

| Tier      | Location                        | Approach                                            |
| --------- | ------------------------------- | --------------------------------------------------- |
| Java      | `languages/java/`               | OO references; primary reference implementations    |
| C++       | `languages/cpp/`                | modern C++17 (RAII, iterators, no dependencies)     |
| Rust      | `languages/rust/`               | ownership-safe implementations, zero dependencies   |
| Python    | `src/ads/`                      | regular (`problems`/`structures`) + advanced (`*_advanced`, optimized DP/graph/iterative comments, mypy strict) |

The existing `src/algo_discovery` package (65 tests) is preserved as the
advanced Python pattern-discovery showcase.

### Run everything

```sh
python engine/gen_tests.py        # (re)generate identical test vectors + --check to verify
python engine/runner.py test      # build + run the catalog suite in all 4 languages
python engine/runner.py build     # compile every tier without executing
python engine/runner.py bench     # benchmark all tiers and print a comparison table
python engine/runner.py check     # assert committed vectors are in sync with the catalog
python engine/runner.py discover  # run the local algorithm synthesizer (smoke pass)
```

Sample benchmark output (microseconds, lower is better):

```
algorithm             Python        Java         C++        Rust
merge_sort           928,850      85,358      66,972      39,647
quick_sort           702,918      41,562      22,942      17,610
max_subarray         444,168      17,881       9,702          78
two_sum               32,847      30,393     582,269     659,066
lcs                  901,711      53,888      21,300      24,979
knapsack_01            1,595      25,732      17,617      23,390
```

> Each language may choose a different algorithm strategy for the same problem
> (e.g. Java's two-sum uses a hash map while C++/Rust use the quadratic scan),
> so raw times are a showcase of trade-offs, not an exact contest.

### Per-language testing

```sh
# Python
uv run pytest -q
uv run ruff check src tests
uv run mypy -p algo_discovery -p ads -p synth

# Java
cd languages/java && javac -d out $(find src -name '*.java') && java -cp out ads.TestRunner

# C++
cd languages/cpp && g++ -std=c++17 -O2 -I include tests/test_runner.cpp -o build/runner && ./build/runner

# Rust
cd languages/rust && cargo test --quiet

# Local synthesis
uv run python -m synth discover --smoke   # CI-friendly reduced-budget pass
uv run python -m synth discover           # full pass (>20k candidates/target)
```

## Pattern discovery (original framework)

### Install & use

```python
from algo_discovery import DiscoveryEngine

engine = DiscoveryEngine()

# Squares
result = engine.discover((1, 4, 9, 16, 25))
print(result.best.name)       # "quadratic"
print(result.best.prediction) # 36

# Subset of hypotheses only
from algo_discovery.engine import hypotheses_by_name
engine = DiscoveryEngine(hypotheses=hypotheses_by_name(["arithmetic", "fibonacci-like"]))
```

- **10 built-in hypotheses**: constant, arithmetic, geometric, quadratic,
  cubic, powers-of-two, Fibonacci-like, affine linear recurrence, prime, and
  alternating-sign — each yields a confidence, an explanation, and a
  predicted next term when it fits.
- **Feature extraction**: differences, ratios, sign patterns, monotonicity,
  palindromicity, growth rate, gcd, and a normalized numeric vector.

```sh
uv run python -m algo_discovery 1 4 9 16
```

## Local algorithm synthesis (discovery)

`src/synth/` searches for candidate algorithms from input/output examples and
verifies them out-of-sample before reporting any discovery. It is fully local —
no external APIs, no model calls.

- **Grammar search** (`scan` kind): enumerates single-pass "scanner" programs
  (a handful of running state variables updated per element) until one matches
  the curated examples *and* survives fuzz verification against an independent
  reference oracle. Kadane, buy-and-sell, and jump-game style algorithms
  emerge from examples alone.
- **Strategy templates** (`vote`, `seen`, `fib`, `template:circular-kadane`):
  parametric skeletons (Boyer-Moore voting, hash-set membership, Fibonacci
  pumping, circular Kadane) that are still fuzz-verified like everything else.
- **Novelty classification**: every verified candidate is tagged
  `rediscovered` (already in `catalog/problems.json`) or `new-to-catalog`
  (a candidate worth porting to the four language tiers).

Targets live in `catalog/discovery_targets.json`; each entry has curated I/O
examples plus an oracle + fuzz generator in `src/synth/corpus.py`.

```sh
uv run python -m synth discover --smoke    # ~2 min, CI-friendly
uv run python -m synth discover            # full pass
```

Output is written to `catalog/discoveries/`:

- `report.json` — machine-readable results per target
- `report.md` — human-readable table + verified sources
- `solutions/<id>.py` — runnable discovered algorithms

The CLI exits non-zero if any target is rejected or missing, so it plugs
straight into CI. The discovery pass is also exposed as
`python engine/runner.py discover`.

## Development

Requires Python ≥ 3.10 + [uv](https://docs.astral.sh/uv/), plus a JDK (≥ 17),
a C++17 compiler, and the Rust toolchain for the non-Python tiers.

```sh
uv sync --group dev
uv run pytest -q
uv run ruff check src tests
uv run mypy -p algo_discovery -p ads -p synth
```

Run `python engine/runner.py check` before committing to keep generated test
vectors in sync with the catalog.

## Structure

```
catalog/problems.json         single source of truth (tests + examples)
catalog/discovery_targets.json  discovery targets (curated examples + oracle names)
catalog/discoveries/          synthesizer reports + discovered solutions
engine/gen_tests.py           generates identical test vectors per language
engine/runner.py              build / test / benchmark / synthesize dispatcher
src/ads/                      Python solving engine (regular + advanced)
src/algo_discovery/           pattern-discovery framework (original)
src/synth/                    local algorithm synthesizer (grammar + templates)
languages/java/src/ads/       Java tier (+ TestRunner, Benchmark)
languages/cpp/include/ads/    C++17 headers (+ tests/test_runner.cpp, bench/)
languages/rust/src/           Rust tier (+ examples/benchmark.rs)
```

## License

MIT — see [LICENSE](LICENSE).