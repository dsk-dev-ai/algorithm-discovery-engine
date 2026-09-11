"""Headless logic powering the desktop GUI.

Everything here avoids ``tkinter`` so it can run (and be tested) without a
display. The Tk layer in :mod:`gui.app` only renders what these helpers return.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, cast

from algo_discovery import DiscoveryEngine
from synth import discovery as synth_discovery

ROOT: Path = Path(__file__).resolve().parent.parent.parent
CATALOG_PATH: Path = ROOT / "catalog" / "problems.json"
TARGETS_PATH: Path = ROOT / "catalog" / "discovery_targets.json"
DISCOVERIES_DIR: Path = ROOT / "catalog" / "discoveries"
REPORT_JSON: Path = DISCOVERIES_DIR / "report.json"
REPORT_MD: Path = DISCOVERIES_DIR / "report.md"
SOLUTIONS_DIR: Path = DISCOVERIES_DIR / "solutions"

_INT_RE = re.compile(r"-?\d+")


def _load_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def version() -> str:
    """Read the package version from the project metadata."""
    try:
        from importlib import metadata

        return metadata.version("algorithm-discovery-engine")
    except Exception:  # pragma: no cover - source tree fallback
        root_toml = ROOT / "pyproject.toml"
        if root_toml.exists():
            for line in root_toml.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("version"):
                    return line.split("=")[1].strip().strip('"')
        return "0.0.0"


def catalog_summary() -> dict[str, Any]:
    """Summary of the shared multi-language catalog."""
    data = _load_json(CATALOG_PATH)
    return {
        "version": data.get("version", "?"),
        "algorithms": list(data.get("algorithms", [])),
        "data_structures": list(data.get("data_structures", [])),
        "solved_problems": len(data.get("algorithms", [])),
    }


def parse_sequence(text: str) -> list[int]:
    """Parse a spaced/comma separated integer sequence for pattern discovery."""
    terms = [int(m) for m in _INT_RE.findall(text)]
    if not terms:
        raise ValueError("Enter at least one integer (e.g. 1, 4, 9, 16).")
    return terms


def run_patterns(text: str, top: int = 8) -> list[dict[str, Any]]:
    """Discover ranked hypotheses for a user-supplied integer sequence."""
    terms = parse_sequence(text)
    result = DiscoveryEngine().discover(terms)
    ranked = result.ranked[:top]
    return [
        {
            "name": score.name,
            "confidence": score.confidence,
            "prediction": score.prediction,
            "detail": score.detail,
        }
        for score in ranked
    ]


def run_synth(
    smoke: bool = True, fuzz_count: int | None = None, scan_budget: int | None = None
) -> dict[str, Any]:
    """Run the local algorithm synthesizer and return a summarized report.

    Raises ``RuntimeError`` if any target is rejected or missing, mirroring the
    CLI's exit-code contract.
    """
    report = synth_discovery.discover(
        smoke=smoke, scan_budget=scan_budget, fuzz_count=fuzz_count
    )
    summary = synth_summary(report)
    if summary["rejected"] or summary["missing"]:
        raise RuntimeError(
            f"Discovery incomplete: rejected={summary['rejected']} missing={summary['missing']}"
        )
    return summary


def synth_summary(report: dict[str, Any] | None = None) -> dict[str, Any]:
    """Summarize a report dict (or the latest on disk)."""
    if report is None:
        report = load_report()
        if report is None:
            return {
                "verified": 0,
                "rejected": 0,
                "missing": 0,
                "targets": [],
                "exists": False,
            }
    entries = report.get("targets", [])
    verified = [e for e in entries if e.get("status") == "verified"]
    return {
        "verified": len(verified),
        "rejected": sum(1 for e in entries if e.get("status") == "candidate-rejected"),
        "missing": sum(
            1 for e in entries if e.get("status") == "no-candidate-found"
        ),
        "targets": entries,
        "exists": True,
    }


def load_report() -> dict[str, Any] | None:
    """Load the latest discovery report from disk (``None`` if absent)."""
    if not REPORT_JSON.exists():
        return None
    return _load_json(REPORT_JSON)


def discovery_targets() -> list[dict[str, Any]]:
    """The configured discovery targets for display."""
    data = _load_json(TARGETS_PATH)
    return [
        {"id": item["id"], "kind": item.get("kind", "?"), "signature": item.get("signature", "")}
        for item in data["targets"]
    ]


def engine_catalog_counts() -> dict[str, int]:
    """Simple numeric summary for the engine tab."""
    data = _load_json(CATALOG_PATH)
    return {
        "algorithms": len(data.get("algorithms", [])),
        "data_structures": len(data.get("data_structures", [])),
    }