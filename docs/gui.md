# Desktop GUI

A small **Tkinter** desktop app (pure standard library — no third-party
dependencies) wraps the three engines behind buttons.

## Launch

```sh
python -m gui              # from the repo root
uv run python -m gui
python engine/runner.py gui
```

`pip install algorithm-discovery-engine` won't include the GUI — the app is
meant to run from a checkout — but nothing beyond Python ≥ 3.10 with `tkinter`
is required.

## Tabs

### Discover

Drives the [algorithm synthesizer](synthesis.md) from the UI.

- **Run smoke pass** — CI-friendly reduced-budget pass (~2 min).
- **Run full pass** — the full 600k-candidate budget.
- **Refresh** — reload the latest `catalog/discoveries/report.json`.
- **Open report (markdown)** / **Open solutions folder** — jump straight to the
  generated report and `solutions/*.py`.

The table shows per-target id, kind, status, novelty, search time, and strategy.
Status colors mirror the CLI contract: green = verified, red = rejected.

### Pattern discovery

Type any integer sequence (spaces or commas, negatives welcome) and hit
**Discover**. The ranked hypotheses render as a table with confidence, predicted
next term, and the explanation from the [pattern discovery](patterns.md)
framework.

### Engine

A scratch terminal for the multi-language engine:

- **Check vectors** — assert committed vectors match the catalog.
- **Run pytest** — the Python quality suite.
- **Run build** — compile Java, C++17, and Rust tiers.
- **Benchmark** — full cross-language benchmark table.
- **Open docs / Open GitHub** — external links.

Long-running actions run in a background thread with the buttons disabled; the
status bar reports readiness and failures. The GUI is fully functional on a
headless box only for the *core* logic (see `gui/core.py`); rendering needs a
display.

## Architecture

```
src/gui/core.py     pure logic (no tkinter) — tested headlessly in CI
src/gui/app.py      Tkinter rendering + background worker thread
src/gui/__main__.py launcher (python -m gui)
```