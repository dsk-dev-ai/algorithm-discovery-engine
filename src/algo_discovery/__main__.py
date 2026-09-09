"""Command-line interface: `python -m algo_discovery 1 4 9 16`."""

from __future__ import annotations

import argparse
import sys

from algo_discovery.engine import default_engine


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="algo_discovery",
        description="Discover mathematical patterns in an integer sequence.",
    )
    parser.add_argument(
        "terms",
        type=int,
        nargs="+",
        help="sequence terms, e.g. 1 4 9 16 25",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    engine = default_engine()
    result = engine.discover(args.terms)
    print(f"sequence: {result.sequence.terms}")
    print(f"ranked hypotheses for {result.sequence.terms}:")
    for score in result.scores:
        prediction = f", next={score.prediction}" if score.prediction is not None else ""
        print(f"  {score.name:16s} conf={score.confidence:1.2f}  {score.detail}{prediction}")
    return 0


if __name__ == "__main__":
    sys.exit(main())