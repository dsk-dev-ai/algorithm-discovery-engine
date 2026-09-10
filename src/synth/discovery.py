"""Discovery orchestrator: search, verify, classify, and report.

For every target in ``catalog/discovery_targets.json``:

1. Search for a candidate algorithm (grammar search or strategy template).
2. Verify it on the curated examples **and** on out-of-sample fuzz inputs
   whose expected outputs come from an independent reference oracle.
3. Classify novelty (rediscovered vs. new to the solved catalog) and estimate
   complexity.
4. Persist ``catalog/discoveries/report.json``, ``report.md``, and a runnable
   per-target solution module.
"""

from __future__ import annotations

import json
import time
from typing import Any

from synth import corpus, search

ROOT = corpus.ROOT
DISCOVERIES_DIR = ROOT / "catalog" / "discoveries"
SOLUTIONS_DIR = DISCOVERIES_DIR / "solutions"

FUZZ_COUNT = 60


def _solved_catalog_ids() -> set[str]:
    payload = json.loads((ROOT / "catalog" / "problems.json").read_text(encoding="utf-8"))
    ids = {entry["id"] for entry in payload.get("algorithms", [])}
    ids.update({entry["id"] for entry in payload.get("structures", [])})
    return ids


def _verify_curated(candidate: search.Candidate, target: dict[str, Any]) -> bool:
    namespace: dict[str, Any] = {}
    exec(compile(candidate.source, "<synth>", "exec"), namespace)
    fn = namespace[candidate.function_name]
    for inputs, expected in target["examples"]:
        try:
            if fn(*inputs) != expected:
                return False
        except Exception:  # pragma: no cover - defensive
            return False
    return True


def _verify_fuzz(candidate: search.Candidate, target_id: str) -> tuple[bool, int]:
    cases = corpus.fuzz_cases(target_id, FUZZ_COUNT)
    namespace: dict[str, Any] = {}
    exec(compile(candidate.source, "<synth>", "exec"), namespace)
    fn = namespace[candidate.function_name]
    for inputs, expected in cases:
        try:
            if fn(*inputs) != expected:
                return False, -1
        except Exception:  # pragma: no cover - defensive
            return False, -1
    return True, len(cases)


def _classify(target_id: str, kind: str) -> dict[str, str]:
        solved = _solved_catalog_ids()
        if target_id in solved:
            status = (
                "rediscovered" if kind == "scan" else "rediscovered-via-template"
            )
            note = (
                "target already solved in the shared (4-language) catalog; "
                "this candidate matches the same contract all tier runners assert"
            )
        else:
            status = "new-to-catalog"
            note = (
                "not part of the shared catalog yet "
                "- a candidate worth porting to the language tiers"
            )
        return {"status": status, "note": note}


def discover(
    smoke: bool = False, scan_budget: int | None = None, fuzz_count: int | None = None
) -> dict[str, Any]:
    """Run the full discovery pass over every target."""
    targets = corpus.load_targets()
    solved = _solved_catalog_ids()
    global FUZZ_COUNT
    if fuzz_count is not None:
        FUZZ_COUNT = fuzz_count

    entries: list[dict[str, Any]] = []
    for target_id, target in targets.items():
        started = time.monotonic()
        budget = 200_000 if smoke else (scan_budget or 600_000)
        candidate = search.discover_for_target(target, scan_budget=budget)
        elapsed = time.monotonic() - started
        if candidate is None:
            entries.append(
                {
                    "id": target_id,
                    "status": "no-candidate-found",
                    "kind": target["kind"],
                    "search_ms": round(elapsed * 1000),
                }
            )
            continue
        curated_ok = _verify_curated(candidate, target)
        fuzz_ok, fuzz_run = _verify_fuzz(candidate, target_id)
        classification = _classify(target_id, candidate.kind)
        entries.append(
            {
                "id": target_id,
                "status": (
                    "verified" if (curated_ok and fuzz_ok) else "candidate-rejected"
                ),
                "hidden": False,
                "search_ms": round(elapsed * 1000),
                "curated_examples_pass": curated_ok,
                "fuzz_examples_pass": fuzz_ok,
                "fuzz_run": fuzz_run,
                "source": candidate.source.strip(),
                "size_metric": candidate.nodes,
                "kind": candidate.kind,
                "strategy": candidate.params.get("strategy", ""),
                "time_class": candidate.time_class,
                "novelty": classification["status"],
                "novelty_note": classification["note"],
                "signature": target["signature"],
            }
        )

    report: dict[str, Any] = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "fuzz_per_target": FUZZ_COUNT,
        "solved_catalog_problems": len(solved),
        "targets": entries,
    }
    _write_report(report)
    return report


def _write_report(report: dict[str, Any]) -> None:
    DISCOVERIES_DIR.mkdir(parents=True, exist_ok=True)
    SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)
    (DISCOVERIES_DIR / "report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    for entry in report["targets"]:
        if "source" in entry:
            (SOLUTIONS_DIR / f"{entry['id']}.py").write_text(
                entry["source"] + "\n", encoding="utf-8"
            )
    (DISCOVERIES_DIR / "report.md").write_text(_render_markdown(report), encoding="utf-8")


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Discovery report",
        "",
        f"Fuzz cases per target: {report['fuzz_per_target']}  ·  "
        f"solved catalog problems: {report['solved_catalog_problems']}",
        "",
        "| target | status | strategy | size | novelty |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for entry in report["targets"]:
        lines.append(
            "| {} | {} | {} | {} | {} |".format(
                entry["id"],
                entry["status"],
                entry.get("strategy", "-"),
                entry.get("size_metric", "-"),
                entry.get("novelty", "-"),
            )
        )
    lines.append("")
    for entry in report["targets"]:
        if "source" not in entry or entry["status"] != "verified":
            continue
        lines.extend(
            [
                f"## {entry['id']}  (`{entry['kind']}`)",
                "",
                f"`{entry['signature']}`",
                "",
                f"- Complexity: {entry['time_class']}",
                f"- Novelty: {entry['novelty']} — {entry['novelty_note']}",
                f"- Verified on {entry['curated_examples_pass'] and 'all curated examples'}"
                f" and {entry['fuzz_run']} fuzz inputs.",
                "",
                "```python",
                entry["source"],
                "```",
                "",
            ]
        )
    return "\n".join(lines) + "\n"