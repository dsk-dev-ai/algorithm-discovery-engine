# Contributing

Thanks for your interest in contributing to the Algorithm Discovery Engine.

## Setup

Requires Python >= 3.10 and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/dsk-dev-ai/algorithm-discovery-engine.git
cd algorithm-discovery-engine
uv sync --extra dev
```

## Quality gates

Run the full check suite before submitting:

```bash
uv run ruff check src tests
uv run mypy src
uv run pytest
```

## Process

1. Branch from `main`: `feat/my-feature` or `fix/my-bug`.
2. Add a hypothesis in `src/algo_discovery/hypotheses.py` with unit tests in
   `tests/`.
3. Document new hypotheses in the README.
4. Run the quality gates above.
5. Commit with a Conventional Commit message and open a PR.

## PR checklist

- [ ] `ruff check` passes
- [ ] `mypy` passes (strict)
- [ ] Tests added/updated and passing
- [ ] README updated if behavior changed