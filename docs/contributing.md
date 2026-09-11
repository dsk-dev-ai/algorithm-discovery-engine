# Contributing

Thanks for your interest in contributing to the Algorithm Discovery Engine.

## Setup

Requires Python ≥ 3.10 and [uv](https://docs.astral.sh/uv/), plus a JDK
(≥ 17), a C++17 compiler, and the Rust toolchain for the non-Python tiers.

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
uv run pytest -q
uv run python -m gui --selftest         # headless GUI core smoke test
uv run mkdocs build --strict            # documentation builds cleanly
```

### Per-language quick checks

```bash
cd languages/java && javac -d out $(find src -name '*.java') && java -cp out ads.TestRunner
cd languages/cpp && g++ -std=c++17 -O2 -I include tests/test_runner.cpp -o build/runner && ./build/runner
cd languages/rust && cargo test --quiet
```

## Adding a catalog problem

1. Add the problem to `catalog/problems.json` with empty `tests`.
2. Implement it in every tier: `src/ads/`, `languages/java/`, `languages/cpp/`,
   `languages/rust/` (following the existing per-problem conventions).
3. Run `uv run pytest -q` to auto-generate and fill the test vectors, then run
   `python engine/runner.py check` to confirm they are committed in sync.
4. Wire it into `engine/runner.py` `BENCH_ALGOS` and each tier's benchmark if
   you want it benchmarked.

## Adding a discovery target

1. Add a target entry to `catalog/discovery_targets.json` (id, kind, signature,
   `arg_types`) with curated I/O examples.
2. Provide an oracle + fuzz generator in `src/synth/corpus.py` (see
   `oracle_jump_game` / `fuzz_reach` for a template).
3. Verify with `uv run python -m synth discover --smoke` — the fully-verified
   target should join the report as `verified`.

## Documentation

The site uses [MkDocs Material](https://squidfunk.github.io/mkdocs-material/):

```bash
uv run mkdocs serve    # local preview at http://127.0.0.1:8000
uv run mkdocs build --strict   # CI gate — must stay warnings-free
```

Documentation lives in `docs/`; pages map to the nav in `mkdocs.yml`. The CI
`docs` job builds with `--strict`, so dead links and broken fences block merges.

## CI

`.github/workflows/ci.yml` runs: ruff + mypy (all packages, including `gui`),
pytest on Python 3.10/3.12/3.13, Java/C++/Rust tests, `gen_tests --check`, a
discovery-smoke job, and a strict MkDocs build. `.github/workflows/pages.yml`
deploys the docs to GitHub Pages on every push to `main`.

## Releasing

Version bumps bump `pyproject.toml`, add a GitHub tag matching the version, and
a release with the changelog collated from the merged pull requests.