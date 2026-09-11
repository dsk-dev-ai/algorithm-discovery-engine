"""Tests for the headless GUI core (no display required)."""

from __future__ import annotations

import pytest

from gui import core


class TestCatalogSummary:
    def test_counts(self) -> None:
        summary = core.catalog_summary()
        assert summary["algorithms"]
        assert summary["data_structures"]
        assert summary["solved_problems"] == len(summary["algorithms"])

    def test_version_readable(self) -> None:
        assert core.version()


class TestParseSequence:
    def test_spaced(self) -> None:
        assert core.parse_sequence("1 4 9 16 25") == [1, 4, 9, 16, 25]

    def test_comma_and_negatives(self) -> None:
        assert core.parse_sequence("2, -4, 8, -16") == [2, -4, 8, -16]

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            core.parse_sequence("abc")


class TestRunPatterns:
    def test_quadratic(self) -> None:
        rows = core.run_patterns("1 4 9 16 25", top=1)
        assert rows
        assert rows[0]["name"] in ("quadratic", "polynomial", "perfect-squares")
        assert rows[0]["prediction"] == 36
        assert rows[0]["confidence"] > 0

    def test_ordering_by_confidence(self) -> None:
        rows = core.run_patterns("1 1 2 3 5 8 13 21", top=20)
        confidences = [r["confidence"] for r in rows]
        assert confidences == sorted(confidences, reverse=True)


class TestSynth:
    def test_smoke_run_and_report(self) -> None:
        summary = core.run_synth(smoke=True, fuzz_count=10)
        assert summary["verified"] >= 1
        assert summary["rejected"] == 0
        assert summary["missing"] == 0
        assert core.REPORT_JSON.exists()
        assert core.REPORT_MD.exists()

    def test_summary_reflects_disk(self) -> None:
        on_disk = core.synth_summary()
        assert on_disk["exists"]
        assert set(on_disk) >= {"verified", "rejected", "missing", "targets"}

    def test_targets_listed(self) -> None:
        targets = core.discovery_targets()
        assert targets
        assert all("id" in t and "kind" in t for t in targets)

    def test_report_schema(self) -> None:
        report = core.load_report()
        assert report is not None
        entries = report["targets"]
        assert entries
        assert all(
            {"status", "id", "source"} <= set(e)
            for e in entries
        )