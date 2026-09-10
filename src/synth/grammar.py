"""Expression grammar for synthesized algorithms.

A tiny, typed-free expression language used by the search backends. Every
expression can be evaluated over a binding environment and printed back as
Python source, so discovered candidates are always runnable and reviewable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Hard negative/positive sentinels far from real inputs.
NEG_INF = -(1 << 30)
POS_INF = 1 << 30


@dataclass(frozen=True)
class Node:
    """Immutable expression tree node.

    ``op`` is either a literal value (int/str) or one of the operator names
    below. ``args`` holds child nodes.
    """

    op: str | int
    args: tuple[Node, ...] = ()


def const(value: int | str) -> Node:
    return Node(value)


def var(name: str) -> Node:
    return Node("var", (Node(name),))


def call(name: str, *args: Node) -> Node:
    return Node(name, args)


# nodes available to a scanner program ---------------------------------------

UNARY_OPS = {"neg", "abs"}
BINARY_OPS = {"add", "sub", "mul", "fdiv", "mod", "min", "max"}
CMP_OPS = {"lt", "gt", "le", "ge", "eq"}

ALL_OPS = UNARY_OPS | BINARY_OPS | CMP_OPS

# simple canonical variables a scan understands
VARIABLES = {"i", "n", "x"}

_OPERATOR_TO_PY = {
    "neg": "(-{})",
    "abs": "abs({})",
    "add": "({} + {})",
    "sub": "({} - {})",
    "mul": "({} * {})",
    "fdiv": "({} // {})",
    "mod": "({} % {})",
    "min": "min({}, {})",
    "max": "max({}, {})",
    "lt": "({} < {})",
    "gt": "({} > {})",
    "le": "({} <= {})",
    "ge": "({} >= {})",
    "eq": "({} == {})",
}


def evaluate(node: Node, env: dict[str, Any]) -> Any:
    """Evaluate the expression tree over ``env``.

    Division by zero and mod-by-zero short-circuit to a benign neutral value
    so search does not crash on degenerate candidates.
    """
    op = node.op
    if isinstance(op, int):
        return op
    if op == "var":
        key = node.args[0].op
        assert isinstance(key, str)
        return env[key]
    if op == "neg":
        return -evaluate(node.args[0], env)
    if op == "abs":
        return abs(evaluate(node.args[0], env))
    if op in BINARY_OPS or op in CMP_OPS:
        left = evaluate(node.args[0], env)
        right = evaluate(node.args[1], env)
        if op == "add":
            return left + right
        if op == "sub":
            return left - right
        if op == "mul":
            return left * right
        if op == "fdiv":
            if right == 0:
                return left
            sign = -1 if (left < 0) != (right < 0) else 1
            return sign * (abs(left) // abs(right))
        if op == "mod":
            if right == 0:
                return 0
            sign = 1 if right > 0 else -1
            return sign * (((left % abs(right)) + abs(right)) % abs(right))
        if op == "min":
            return min(left, right)
        if op == "max":
            return max(left, right)
        if op == "lt":
            return left < right
        if op == "gt":
            return left > right
        if op == "le":
            return left <= right
        if op == "ge":
            return left >= right
        return left == right
    raise ValueError(f"unknown node: {node}")


def to_python(node: Node) -> str:
    """Render the expression tree as Python source."""
    op = node.op
    if isinstance(op, int):
        return repr(op)
    if op == "var":
        return str(node.args[0].op)
    if op in UNARY_OPS:
        return _OPERATOR_TO_PY[op].format(to_python(node.args[0]))
    if op in BINARY_OPS or op in CMP_OPS:
        return _OPERATOR_TO_PY[op].format(
            to_python(node.args[0]), to_python(node.args[1])
        )
    raise ValueError(f"unknown node: {node}")


def size(node: Node) -> int:
    """Number of nodes in the tree (a cheap complexity metric)."""
    return 1 + sum(size(child) for child in node.args)


def tree_depth(node: Node) -> int:
    """Tree depth (used for search budget pruning)."""
    return 1 + max((tree_depth(child) for child in node.args), default=0)


def grow(depth: int, variables: tuple[str, ...], constants: tuple[int, ...]) -> list[Node]:
    """Enumerate all expressions up to ``depth`` over the given leaves."""
    if depth <= 1:
        return [var(name) for name in variables] + [const(c) for c in constants]
    results = [var(name) for name in variables] + [const(c) for c in constants]
    below = grow(depth - 1, variables, constants)
    for name in UNARY_OPS:
        for child in below:
            results.append(call(name, child))
    for name in BINARY_OPS | CMP_OPS:
        for left in below:
            for right in below:
                results.append(call(name, left, right))
    return results


def dedupe_python(nodes: list[Node]) -> list[Node]:
    """Drop nodes whose rendered Python source is identical (dedup + normalize)."""
    seen: set[str] = set()
    out: list[Node] = []
    for node in nodes:
        key = to_python(node)
        if key not in seen:
            seen.add(key)
            out.append(node)
    return out