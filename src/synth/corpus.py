"""Discovery targets, reference oracles, and fuzz generators.

Curated targets live in ``catalog/discovery_targets.json``; every target maps
to an oracle here (used as the truth source for fuzz verification) and a fuzz
input generator.
"""

from __future__ import annotations

import json
import random
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent

PARSE_DELIM = "|"


def parse_input(
    spec: str, arg_types: list[str] | None = None
) -> list[Any]:
    """Parse a '|'-delimited spec into typed arguments.

    Without ``arg_types`` a scalar token is parsed as ``int`` and multiple
    tokens become a ``list[int]``. With ``arg_types`` each segment is read per
    its declared type, so a single-element list like ``"0|"`` correctly
    produces ``[0]`` (a one-arg list, not the scalar ``0``).
    """
    if arg_types is None:
        return _parse_input_legacy(spec)
    raw = spec.split(PARSE_DELIM)
    if raw and raw[-1] == "":
        raw.pop()
    parsed: list[Any] = []
    for piece, atype in zip(raw, arg_types, strict=True):
        if atype == "int":
            parsed.append(int(piece))
        else:
            parsed.append([] if not piece.strip() else [int(t) for t in piece.split()])
    return parsed


def _parse_input_legacy(spec: str) -> list[Any]:
    """Legacy whitespace heuristic (scalar token -> int, more -> list)."""
    parsed: list[Any] = []
    for part in spec.split(PARSE_DELIM):
        tokens = part.split()
        if not tokens:
            continue
        if len(tokens) == 1:
            token = tokens[0]
            if token.lower() in {"true", "false"}:
                parsed.append(token.lower() == "true")
            else:
                parsed.append(int(token))
        else:
            parsed.append([int(token) for token in tokens])
    return parsed


# --- oracles --------------------------------------------------------------------


def _kadane(nums: list[int]) -> int:
    best = nums[0] if nums else 0
    running = 0
    for value in nums:
        running = max(value, running + value)
        best = max(best, running)
    return best


def oracle_max_circular_subarray(nums: list[int]) -> int:
    """Maximum circular subarray sum (empty selection allowed -> 0)."""
    if not nums:
        return 0
    total = sum(nums)
    if all(value < 0 for value in nums):
        return 0
    min_sub = _kadane([-value for value in nums])
    return max(_kadane(nums), total + min_sub)


def oracle_best_time_buy_sell(prices: list[int]) -> int:
    """Maximum profit from one buy/sell; 0 if none possible."""
    if len(prices) < 2:
        return 0
    best = 0
    low = prices[0]
    for price in prices[1:]:
        low = min(low, price)
        best = max(best, price - low)
    return best


def oracle_jump_game(nums: list[int]) -> bool:
    """Whether the last index is reachable by jumping nums[i] steps."""
    reach = 0
    for i, value in enumerate(nums):
        if i > reach:
            return False
        reach = max(reach, i + value)
    return True


def oracle_majority_element(nums: list[int]) -> int:
    """Element appearing more than n//2 times (guaranteed in test inputs)."""
    return sorted(nums)[len(nums) // 2]


def oracle_contains_duplicate(nums: list[int]) -> bool:
    """Whether any value appears more than once."""
    return len(nums) != len(set(nums))


def oracle_climbing_stairs(n: int) -> int:
    """Ways to climb n stairs taking 1 or 2 steps."""
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


ORACLES: dict[str, Callable[..., Any]] = {
    "max_circular_subarray": oracle_max_circular_subarray,
    "best_time_buy_sell": oracle_best_time_buy_sell,
    "jump_game": oracle_jump_game,
    "majority_element": oracle_majority_element,
    "contains_duplicate": oracle_contains_duplicate,
    "climbing_stairs": oracle_climbing_stairs,
    "max_subarray": _kadane,
}


# --- fuzz generators -------------------------------------------------------------

def _small_int_list(rng: random.Random, low: int, high: int) -> list[int]:
    length = rng.randrange(0, 13)
    return [rng.randrange(low, high + 1) for _ in range(length)]


def fuzz_int_list(rng: random.Random) -> list[int]:
    return _small_int_list(rng, -12, 12)


def fuzz_prices(rng: random.Random) -> list[int]:
    return _small_int_list(rng, 0, 12)


def fuzz_reach(rng: random.Random) -> list[int]:
    return _small_int_list(rng, 0, 5)


def fuzz_majority(rng: random.Random) -> list[int]:
    length = rng.randrange(1, 9)
    token = rng.randrange(-6, 6)
    majority_count = length // 2 + 1
    fill = [rng.randrange(-6, 6) for _ in range(length - majority_count)]
    out = [token] * majority_count + fill
    rng.shuffle(out)
    return out


def fuzz_small_int(rng: random.Random) -> int:
    return rng.randrange(0, 16)


FUZZ: dict[str, Callable[[random.Random], Any]] = {
    "max_circular_subarray": fuzz_int_list,
    "best_time_buy_sell": fuzz_prices,
    "jump_game": fuzz_reach,
    "majority_element": fuzz_majority,
    "contains_duplicate": fuzz_int_list,
    "climbing_stairs": fuzz_small_int,
    "max_subarray": fuzz_int_list,
}

# --- loading ----------------------------------------------------------------------

DISCOVERY_TARGETS: dict[str, dict[str, Any]] = {}


def parse_output(spec: str) -> Any:
    """Parse an expected output token into bool/int."""
    token = spec.strip()
    if token.lower() in {"true", "false"}:
        return token.lower() == "true"
    return int(token)


def load_targets() -> dict[str, dict[str, Any]]:
    """Load ``catalog/discovery_targets.json`` once."""
    if DISCOVERY_TARGETS:
        return DISCOVERY_TARGETS
    path = ROOT / "catalog" / "discovery_targets.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    for target in payload["targets"]:
        oracle_name = target.get("oracle", target["id"])
        fuzz_name = target.get("fuzz", target["id"])
        target["oracle"] = ORACLES[oracle_name]
        target["fuzz"] = FUZZ[fuzz_name]
        target["examples"] = [
            (parse_input(case["in"], target.get("arg_types")), parse_output(case["out"]))
            for case in target["cases"]
        ]
        DISCOVERY_TARGETS[target["id"]] = target
    return DISCOVERY_TARGETS


def fuzz_cases(target_id: str, count: int) -> list[tuple[list[Any], Any]]:
    """Draw ``count`` fuzz cases verified against the target's oracle."""
    target = load_targets()[target_id]
    oracle = target["oracle"]
    generator = target["fuzz"]
    rng = random.Random(target_id + str(count))
    cases: list[tuple[list[Any], Any]] = []
    for _ in range(count):
        inputs = [generator(rng)]
        cases.append((inputs, oracle(*inputs)))
    return cases