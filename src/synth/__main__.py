"""CLI: ``python -m synth discover [--smoke] [--scan-budget N] [--fuzz N]``."""

from __future__ import annotations

import argparse
import json
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="synth", description="Local algorithm discovery"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    discover_parser = sub.add_parser("discover", help="run the discovery pass")
    discover_parser.add_argument(
        "--smoke", action="store_true", help="reduced budget (CI-friendly)"
    )
    discover_parser.add_argument(
        "--scan-budget",
        type=int,
        default=None,
        help="grammar search candidate cap",
    )
    discover_parser.add_argument(
        "--fuzz", type=int, default=None, help="fuzz cases per target"
    )
    discover_parser.add_argument(
        "--print", action="store_true", help="print report JSON to stdout"
    )

    args = parser.parse_args()

    if args.command == "discover":
        from synth.discovery import DISCOVERIES_DIR, discover

        report = discover(
            smoke=args.smoke,
            scan_budget=args.scan_budget,
            fuzz_count=args.fuzz,
        )
        verified = [
            e for e in report["targets"] if e["status"] == "verified"
        ]
        rejected = [
            e for e in report["targets"] if e["status"] == "candidate-rejected"
        ]
        missing = [
            e for e in report["targets"] if e["status"] == "no-candidate-found"
        ]
        print(
            f"targets={len(report['targets'])} verified={len(verified)} "
            f"rejected={len(rejected)} missing={len(missing)}"
        )
        print(f"report: {DISCOVERIES_DIR / 'report.md'}")
        if args.print:
            print(json.dumps(report, indent=2))
        return 0 if not missing and not rejected else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
