# Algorithm synthesis

`src/synth/` searches for candidate algorithms directly from input/output
examples and verifies them out-of-sample before reporting anything. The scan is
fully local — no external APIs, no model calls.

## How it works

- **Grammar search** (`scan` kind) enumerates single-pass *scanner* programs: a
  handful of running-state variables updated per element, drawn from an
  operator/pool grammar. A candidate must match the curated examples **and**
  survive fuzz verification (60+ inputs) against an independent reference
  oracle.
- **Strategy templates** (`vote`, `seen`, `fib`, `circular-kadane`) supply
  parametric skeletons — Boyer-Moore voting, hash-set membership, Fibonacci
  pumping, circular Kadane — that are fuzz-verified just like grammar results.
- **Novelty classification**: every verified candidate is tagged
  `rediscovered` (already in `catalog/problems.json`) or `new-to-catalog` (a
  candidate worth porting to the four language tiers).

## Running it

```sh
uv run python -m synth discover --smoke   # ~2 min, CI-friendly
uv run python -m synth discover           # full pass (~600k candidates/target cap)
```

Or from the dispatcher: `python engine/runner.py discover`.

## Reading the report

Results land in `catalog/discoveries/`:

- `report.json` — machine-readable results per target
- `report.md` — human-readable table + verified sources
- `solutions/<id>.py` — runnable discovered algorithms

The CLI exits non-zero if any target is rejected or missing, so the discovery
pass plugs straight into CI. Current smoke run: **7 targets · 7 verified ·
0 rejected**.

## Example: a discovered jump-game scanner

```python
def discovered_jump_game(arg):
    s0 = 0
    s1 = 0
    for i, x in enumerate(arg):
        s1 = max(s1, i - s0)   # how far the current reach overshoots index i
        s0 = max(s0, i + x)    # extend the reach
    return s1 == 0
```

This scanner was synthesized from examples alone and verified against a
reference oracle plus fuzz inputs before being reported.