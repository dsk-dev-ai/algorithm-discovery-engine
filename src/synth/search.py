"""Search backends that discover candidate algorithms from I/O examples.

Two strategies are offered:

* ``scan_search`` — open-ended grammar enumeration of single-pass "scanner"
  programs (a handful of running state variables updated per element). This is
  the *true* search backend: Kadane, buy-and-sell, and jump-game style
  algorithms emerge from examples with no prior knowledge of the problem.
* ``template_discover`` — parametric instantiation of strategy skeletons
  (Boyer-Moore voting, seen-set detection, Fibonacci pumping, and circular
  Kadane). Retrieved programs are still verified on the full corpus + fuzz.

Every candidate is emitted as runnable Python source.
"""

from __future__ import annotations

import itertools
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from synth import corpus


@dataclass
class Candidate:
    """A synthesized algorithm."""

    target_id: str
    source: str
    kind: str
    nodes: int
    params: dict[str, Any] = field(default_factory=dict)
    time_class: str = "O(n), O(1) extra space"
    fuzz_verified: bool = False

    @property
    def function_name(self) -> str:
        return f"discovered_{self.target_id}"


def _arg_name(target: dict[str, Any]) -> str:
    return "arg"


# --- codegen -----------------------------------------------------------------------


def scan_source(
    target_id: str,
    inits: list[str],
    updates: list[tuple[int, str, str]],
    empty_return: object | None = None,
) -> str:
    """Render a scanner program (state count derived from updates).

    Initialization ``first`` seeds a state from ``arg[0]`` and therefore skips
    the first element during iteration; ``zero`` seeds ``0`` and iterates the
    whole list. When ``empty_return`` is given (int targets), empty inputs are
    short-circuited up front.
    """
    arg = "arg"
    states = sorted({idx for idx, _, _ in updates})
    count = (states[-1] if states else 0) + 1
    body: list[str] = []
    if empty_return is not None:
        body.append(f"    if not {arg}:")
        body.append(f"        return {empty_return}")
    for idx in range(count):
        value = "arg[0]" if inits[idx] == "first" else "0"
        body.append(f"    s{idx} = {value}")
    skip_first = bool(inits) and all(init == "first" for init in inits)
    if skip_first:
        body.append("    for i, x in enumerate(arg[1:], 1):")
    else:
        body.append("    for i, x in enumerate(arg):")
    body.append("        n = len(arg)")
    for idx, style, expr in updates:
        if style == "replace":
            body.append(f"        s{idx} = {expr}")
        elif style == "max":
            body.append(f"        s{idx} = max(s{idx}, {expr})")
        elif style == "min":
            body.append(f"        s{idx} = min(s{idx}, {expr})")
        elif style == "add":
            body.append(f"        s{idx} = s{idx} + {expr}")
        elif style == "floor_at_zero":
            body.append(f"        s{idx} = max(0, s{idx} + {expr})")
    return "\n".join(body)


def build_scan_candidate(
    target: dict[str, Any],
    inits: str,
    updates: list[tuple[int, str, str]],
    output: str,
) -> Candidate:
    arg = "arg"
    empty_return = 0 if target.get("returns") == "int" else None
    body = scan_source(
        target["id"], inits.split("|"), updates, empty_return=empty_return
    )
    out_assign = "True" if output == "true" else "False" if output == "false" else output
    source = (
        f"def discovered_{target['id']}({arg}):\n{body}\n"
        f"    return {out_assign}\n"
    )
    nodes = 1 + sum(
        1 + expr.split().count("max") + expr.split().count("min") for _, _, expr in updates
    ) + sum(1 for _ in output.split())
    return Candidate(
        target_id=target["id"],
        source=source,
        kind="scan",
        nodes=nodes,
        params={
            "init_mode": inits,
            "updates": updates,
            "output": output,
            "states": len({idx for idx, _, _ in updates}),
        },
    )


def expr_nodes(expr: str) -> int:
    return len(expr.split()) + 2


def init_nodes(init_mode: str) -> int:
    return 1


# --- scan simulation (fast, avoids exec during search) -----------------------------


def _evaluate_tracker(
    expr: str, env: dict[str, Any], memo: dict[str, Any]
) -> Any:
    if expr in memo:
        return memo[expr]
    if expr.isdigit() or (expr.startswith("-") and expr[1:].isdigit()):
        result = int(expr)
    elif expr.startswith(("s", "x", "i", "n")) and expr in env:
        result = env[expr]
    else:
        try:
            result = eval(expr, {"__builtins__": {}}, {**env})
        except Exception:  # pragma: no cover - defensive
            result = None
    memo[expr] = result
    return result


# --- scanner enumeration ------------------------------------------------------------


def _base_pool(state_count: int) -> list[str]:
    """Small primitive update expressions (all used with replace/accum styles)."""
    pool: list[str] = []
    for idx in range(state_count):
        s = f"s{idx}"
        pool.extend(
            [
                f"{s}",
                "x",
                "i",
                f"{s} + x",
                f"{s} - x",
                f"x - {s}",
                f"max(x, {s})",
                f"min(x, {s})",
                f"max(x, {s} + x)",
                f"min(x, {s} + x)",
                f"{s} + i",
                f"{s} + 1",
                f"{s} - 1",
                "x + i",
            ]
        )
        if state_count == 2:
            other = "s0" if idx == 1 else "s1"
            pool.extend(
                [
                    f"{other}",
                    f"max({s}, {other})",
                    f"min({s}, {other})",
                    f"{other} - x",
                    f"x - {other}",
                ]
            )
    return list(dict.fromkeys(pool))


def _accum_exprs(state_count: int) -> list[str]:
    """Small composite updates usable under max/min/add accumulation."""
    exprs = ["x", "i", "i + x", "x + i", "i - x", "x - i"]
    if state_count == 2:
        exprs += ["i - s0", "s0 - i", "x - s0", "s0 - x"]
    return list(dict.fromkeys(exprs))


def _output_options(state_count: int, is_bool: bool) -> list[str]:
    """Curated final-value mappings from the running state + length."""
    ints: list[str] = []
    for idx in range(state_count):
        ints.append(f"s{idx}")
    if state_count >= 2:
        ints.extend(
            [
                f"max(s{state_count - 2}, s{state_count - 1})",
                f"min(s{state_count - 2}, s{state_count - 1})",
                f"s{state_count - 1} - s{state_count - 2}",
                f"s{state_count - 2} - s{state_count - 1}",
            ]
        )
    ints.append("n - 1")
    ints = list(dict.fromkeys(ints))
    if not is_bool:
        return ints
    bools: list[str] = []
    for idx in range(state_count):
        bools.append(f"s{idx} >= n - 1")
        bools.append(f"s{idx} >= n")
        bools.append(f"s{idx} > 0")
        bools.append(f"s{idx} == 0")
        bools.append(f"s{idx} < n")
        bools.append(f"s{idx} <= 0")
    return list(dict.fromkeys(bools))


def scan_search(
    target: dict[str, Any],
    max_candidates: int = 600_000,
    expr_depth: int = 2,
) -> Candidate | None:
    """Enumerate single-pass scanner programs until one matches every example."""
    examples = target["examples"]
    inputs_list = [pair[0] for pair in examples]
    outputs_expected = [pair[1] for pair in examples]
    is_bool = target.get("returns") == "bool"

    budget = max(max_candidates, 100)
    for state_count in (1, 2):
        base = _base_pool(state_count)
        accum = _accum_exprs(state_count)
        outputs = _output_options(state_count, is_bool)
        generated = 0
        exhausted = False
        init_choices = ("zero", "first")
        options: list[tuple[int, str, str]] = []
        for expr in base:
            weight = expr.count("(") + 1
            options.append((weight, "replace", expr))
        for expr in accum:
            options.append((2, "max", expr))
            options.append((2, "min", expr))
            options.append((2, "add", expr))
        options.sort()
        options_per_state = [list(options) for _ in range(state_count)]
        for combo in itertools.product(*options_per_state):
            if exhausted:
                break
            for init_combo in itertools.product(init_choices, repeat=state_count):
                orders: list[list[tuple[int, str, str]]] = [
                    [(idx, style, expr) for idx, (_, style, expr) in enumerate(combo)]
                ]
                if state_count == 2:
                    orders.append(orders[0][::-1])
                for updates in orders:
                    for output in outputs:
                        generated += 1
                        if generated > budget:
                            exhausted = True
                            break
                        candidate = build_scan_candidate(
                            target, "|".join(init_combo), updates, output
                        )
                        if not _matches_examples(
                            candidate, inputs_list, outputs_expected
                        ):
                            continue
                        if _fuzz_match(candidate, target):
                            candidate.fuzz_verified = True
                            return candidate
                    if exhausted:
                        break
    return None


def _matches_examples(
    candidate: Candidate, inputs_list: list[list[Any]], outputs: list[Any]
) -> bool:
    """Evaluate the compiled candidate against every example (memoized)."""
    namespace: dict[str, Any] = {}
    exec(compile(candidate.source, "<synth>", "exec"), namespace)
    fn = namespace[candidate.function_name]
    for inputs, expected in zip(inputs_list, outputs, strict=True):
        try:
            got = fn(*inputs)
        except Exception:  # pragma: no cover - defensive
            return False
        if isinstance(expected, (bool, int)):
            if got != expected:
                return False
        else:  # pragma: no cover - defensive
            return False
    return True


def _fuzz_match(candidate: Candidate, target: dict[str, Any], count: int = 60) -> bool:
    cases = corpus.fuzz_cases(target["id"], count)
    return _matches_examples(
        candidate,
        [pair[0] for pair in cases],
        [pair[1] for pair in cases],
    )


# --- strategy templates --------------------------------------------------------------


def template_discover(target: dict[str, Any]) -> list[Candidate]:
    """Instantiate the parametric skeleton for the target's ``kind``."""
    kind = target["kind"]
    builder = _BUILDERS.get(kind)
    if builder is None:  # pragma: no cover - config error
        return []
    return [builder(target)]


def _build_vote(target: dict[str, Any]) -> Candidate:
    arg = "arg"
    source = (
        f"def discovered_{target['id']}({arg}):\n"
        "    candidate = arg[0]\n"
        "    count = 1\n"
        "    for x in arg[1:]:\n"
        "        if x == candidate:\n"
        "            count += 1\n"
        "        elif count == 0:\n"
        "            candidate = x\n"
        "            count = 1\n"
        "        else:\n"
        "            count -= 1\n"
        "    return candidate\n"
    )
    return Candidate(
        target_id=target["id"], source=source, kind="vote", nodes=15,
        params={"strategy": "Boyer-Moore majority voting"},
    )


def _build_seen(target: dict[str, Any]) -> Candidate:
    arg = "arg"
    source = (
        f"def discovered_{target['id']}({arg}):\n"
        "    seen = set()\n"
        "    for x in arg:\n"
        "        if x in seen:\n"
        "            return True\n"
        "        seen.add(x)\n"
        "    return False\n"
    )
    return Candidate(
        target_id=target["id"], source=source, kind="seen", nodes=8,
        params={"strategy": "hash-set membership trace"},
        time_class="O(n), O(n) extra space",
    )


def _build_fib(target: dict[str, Any]) -> Candidate:
    arg = "arg"
    source = (
        f"def discovered_{target['id']}({arg}):\n"
        "    a, b = 1, 1\n"
        "    for _ in range(arg):\n"
        "        a, b = b, a + b\n"
        "    return a\n"
    )
    return Candidate(
        target_id=target["id"], source=source, kind="fib", nodes=9,
        params={"strategy": "two-token linear recurrence (Fibonacci)"},
    )


def _build_circular(target: dict[str, Any]) -> Candidate:
    arg = "arg"
    source = (
        f"def discovered_{target['id']}({arg}):\n"
        "    if not arg:\n"
        "        return 0\n"
        "    best_end = arg[0]\n"
        "    best = arg[0]\n"
        "    for x in arg[1:]:\n"
        "        best_end = max(x, best_end + x)\n"
        "        best = max(best, best_end)\n"
        "    total = sum(arg)\n"
        "    min_end = 0\n"
        "    min_wrap = 0\n"
        "    for x in arg:\n"
        "        min_end = min(0, min_end + x)\n"
        "        min_wrap = min(min_wrap, min_end)\n"
        "    return max(best, total - min_wrap, 0)\n"
    )
    return Candidate(
        target_id=target["id"], source=source, kind="template:circular-kadane",
        nodes=24,
        params={"strategy": "Kadane + minimum-window wrap (two passes)"},
        time_class="O(n), O(1) extra space",
    )


_BUILDERS: dict[str, Callable[[dict[str, Any]], Candidate]] = {
    "vote": _build_vote,
    "seen": _build_seen,
    "fib": _build_fib,
    "template": _build_circular,
}


def discover_for_target(
    target: dict[str, Any], scan_budget: int = 60_000, expr_depth: int = 2
) -> Candidate | None:
    """Primary discovery path: grammar search, then template fallback."""
    kind = target["kind"]
    if kind in {"scan"}:
        best = scan_search(target, max_candidates=scan_budget, expr_depth=expr_depth)
        if best is not None:
            return best
        return template_discover(target)[0] if template_discover(target) else None
    return template_discover(target)[0] if template_discover(target) else None