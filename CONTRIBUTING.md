# Contributing

Thanks for your interest in contributing to the Algorithm Discovery Engine.

## Setup

Requires Python >= 3.10 and [uv](https://docs.astral.sh/uv/), plus a JDK
(>= 17), a C++17 compiler, and the Rust toolchain for the non-Python tiers.

```bash
git clone https://github.com/dsk-dev-ai/algorithm-discovery-engine.git
cd algorithm-discovery-engine
uv sync --group dev --group docs
```

## Quality gates

Run the full check suite before submitting:

```bash
python engine/runner.py check          # generated vectors in sync w/ the catalog
python engine/runner.py build           # all four language tiers compile
python engine/runner.py test            # catalog tests pass in all four languages
python engine/runner.py discover        # synthesizer smoke pass (CI-friendly)
uv run ruff check src tests
uv run mypy -p algo_discovery -p ads -p synth -p gui
uv run python -m gui --selftest
uv run mkdocs build --strict
```

### Per-language quick checks

```bash
# Java
cd languages/java && javac -d out $(find src -name '*.java') && java -cp out ads.TestRunner

# C++
cd languages/cpp && g++ -std=c++17 -O2 -I include tests/test_runner.cpp -o build/runner && ./build/runner

# Rust
cd languages/rust && cargo test --quiet
```

## Process

1. Branch from `main`: `feat/my-feature` or `fix/my-bug`.
2. For a new problem: add vectors to `catalog/problems.json`, implement the
   solution in **every** language tier (`src/ads/`, `languages/java/`,
   `languages/cpp/`, `languages/rust/`), and regenerate vectors with
   `python engine/gen_tests.py`.
3. Add/keep unit tests: Python in `tests/`; Java/C++/Rust are covered by the
   generated catalog runners in each `languages/*/`.
4. For a **new discovery target**: add an entry to
   `catalog/discovery_targets.json` (curated I/O examples, `returns` type,
   `arg_types`, and an oracle + fuzz generator in `src/synth/corpus.py`), then
   verify with `python -m synth discover --smoke` and add tests in
   `tests/test_synth.py`.
5. Run the quality gates above.
6. Document behavior changes in the README.
7. Commit with a Conventional Commit message and open a PR.

## PR checklist

- [ ] `python engine/runner.py check` passes
- [ ] `python engine/runner.py test` passes (all tiers)
- [ ] `python engine/runner.py discover` passes (synthesizer smoke)
- [ ] `ruff check` and `mypy` (strict) pass
- [ ] Tests added/updated and passing
- [ ] README updated if behavior changed