"""Shared catalogue test harness.

Runs every problem in ``catalog/problems.json`` against both the regular
(``ads.problems`` / ``ads.structures``) and advanced (``ads.problems_advanced``
/ ``ads.structures_advanced``) Python tiers, then cross-checks that the two
tiers agree with each other.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

import ads.problems as reg
import ads.problems_advanced as adv
import ads.structures as reg_struct
import ads.structures_advanced as adv_struct

_CATALOG = Path(__file__).resolve().parents[1] / "catalog" / "problems.json"

FUNCTIONS = {
    "regular": {
        "two_sum": reg.two_sum,
        "binary_search": reg.binary_search,
        "merge_sort": reg.merge_sort,
        "quick_sort": reg.quick_sort,
        "max_subarray": reg.max_subarray,
        "lcs": reg.lcs,
        "knapsack_01": reg.knapsack_01,
        "edit_distance": reg.edit_distance,
        "graph_bfs": reg.graph_bfs,
        "graph_dfs": reg.graph_dfs,
    },
    "advanced": {
        "two_sum": adv.two_sum_advanced,
        "binary_search": adv.binary_search_advanced,
        "merge_sort": adv.merge_sort_advanced,
        "quick_sort": adv.quick_sort_advanced,
        "max_subarray": adv.max_subarray_advanced,
        "lcs": adv.lcs_advanced,
        "knapsack_01": adv.knapsack_01_advanced,
        "edit_distance": adv.edit_distance_advanced,
        "graph_bfs": adv.graph_bfs_advanced,
        "graph_dfs": adv.graph_dfs_advanced,
    },
}
STRUCTURES = {
    "regular": {
        "stack": reg_struct.Stack,
        "queue": reg_struct.Queue,
        "linked_list": reg_struct.LinkedList,
        "bst": reg_struct.BST,
        "trie": reg_struct.Trie,
        "min_heap": reg_struct.MinHeap,
    },
    "advanced": {
        "stack": adv_struct.StackAdvanced,
        "queue": adv_struct.QueueAdvanced,
        "linked_list": adv_struct.LinkedListAdvanced,
        "bst": adv_struct.BSTAdvanced,
        "trie": adv_struct.TrieAdvanced,
        "min_heap": adv_struct.MinHeapAdvanced,
    },
}


def load_catalog() -> dict:
    with _CATALOG.open() as handle:
        return json.load(handle)


def parse_ints(token: str) -> list[int]:
    """Space-separated ints ('' -> [])."""
    return [int(t) for t in token.replace("|", " ").split() if t]


def parse_matrix(token: str) -> list[list[int]]:
    """Adjacency rows '0:1 2;1:0' -> [[1,2], [0]]."""
    matrix: list[list[int]] = []
    if not token:
        return matrix
    for row in token.split(";"):
        head, _, tail = row.partition(":")
        if not head:
            continue
        assert head.lstrip("-").isdigit(), f"bad row header {head!r}"
        matrix.append(parse_ints(tail))
    return matrix


def run_algorithm(problem_id: str, fn: Callable[..., object], case: dict[str, str]) -> None:
    raw_in = case["in"]
    raw_out = case["out"]
    if problem_id == "two_sum":
        left, target = raw_in.split("|")
        got = fn(parse_ints(left), int(target))
        want = parse_ints(raw_out)
    elif problem_id in ("binary_search", "max_subarray"):
        left, _, right = raw_in.partition("|")
        if problem_id == "binary_search":
            got = fn(parse_ints(left), int(right))
        else:
            got = fn(parse_ints(left))
        want = parse_ints(raw_out)[0] if raw_out else 0
    elif problem_id in ("merge_sort", "quick_sort"):
        got = fn(parse_ints(raw_in))
        want = parse_ints(raw_out)
    elif problem_id in ("lcs", "edit_distance"):
        a, _, b = raw_in.partition("|")
        got = fn(a, b)
        want = int(raw_out)
    elif problem_id == "knapsack_01":
        cap, weights, values = raw_in.split("|")
        got = fn(int(cap), parse_ints(weights), parse_ints(values))
        want = int(raw_out)
    elif problem_id == "graph_bfs":
        adj, start, target = raw_in.split("|")
        got = fn(parse_matrix(adj), int(start), int(target))
        want = int(raw_out)
    elif problem_id == "graph_dfs":
        adj, start, target = raw_in.split("|")
        got = bool(fn(parse_matrix(adj), int(start), int(target)))
        want = raw_out == "true"
    else:  # pragma: no cover
        raise KeyError(problem_id)
    assert got == want, f"{problem_id} {raw_in!r}: got {got!r}, expected {want!r}"


VOID_INT_OPS = {"push", "enqueue", "append", "prepend"}
INT_ARG_OPS = {"get", "contains", "remove"}
STR_ARG_OPS = {"search", "starts_with"}
NO_ARG_OPS = {
    "pop",
    "dequeue",
    "peek",
    "is_empty",
    "size",
    "to_list",
    "in_order",
    "min",
    "max",
    "height",
}


def _split_token(token: str) -> tuple[str, str | None, str | None]:
    """Return (op, arg, expected) for a catalog op token."""
    op, _, rest = token.partition(":")
    if op in VOID_INT_OPS or op in INT_ARG_OPS or op in STR_ARG_OPS or op == "insert":
        parts = rest.split(":", 1)
        return op, parts[0], parts[1] if len(parts) > 1 else None
    if op in NO_ARG_OPS:
        return op, None, rest
    raise KeyError(f"unknown op: {op}")


def _apply(instance: object, op: str, arg: str | None) -> object:
    if op in VOID_INT_OPS:
        getattr(instance, op)(int(str(arg)))
        return None
    if op in INT_ARG_OPS:
        result = getattr(instance, op)(int(str(arg)))
        return bool(result) if isinstance(result, bool) else result
    if op in STR_ARG_OPS:
        return bool(getattr(instance, op)(str(arg)))
    if op == "insert":
        if hasattr(instance, "starts_with"):
            instance.insert(str(arg))
        else:
            instance.insert(int(str(arg)))
        return None
    if op == "pop":
        return instance.pop()
    if op == "dequeue":
        return instance.dequeue()
    if op == "peek":
        return instance.peek()
    if op == "is_empty":
        return bool(instance.is_empty())
    if op == "size":
        return instance.size()
    if op in ("to_list", "in_order"):
        return list(getattr(instance, op)())
    if op == "min":
        return instance.min()
    if op == "max":
        return instance.max()
    if op == "height":
        return instance.height()
    raise KeyError(op)  # pragma: no cover


def run_ops(struct_cls: type, ops: list[str], trace: list[object]) -> None:
    instance = struct_cls()
    for token in ops:
        op, arg, expected = _split_token(token)
        result = _apply(instance, op, arg)
        trace.append(result)
        if expected is not None:
            want = _normalize(expected)
            if isinstance(result, list):
                rendered = " ".join(str(v) for v in result)
                assert rendered == want, f"{token}: got {rendered}, expected {want}"
            else:
                assert result == want, f"{token}: got {result!r}, expected {want!r}"


def _normalize(value: str) -> object:
    lowered = value.strip().lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered == "none":
        return None
    try:
        return int(lowered)
    except ValueError:
        return value


def _trace(tier: str, struct_id: str, ops: object) -> list[object]:
    tokens = list(ops) if isinstance(ops, list) else str(ops).split(",")
    result: list[object] = []
    run_ops(STRUCTURES[tier][struct_id], [o.strip() for o in tokens if o.strip()], result)
    return result


@pytest.mark.parametrize("tier", ["regular", "advanced"])
def test_algorithms_pass_catalog(tier: str) -> None:
    catalog = load_catalog()
    for problem in catalog["algorithms"]:
        for case in problem["cases"]:
            run_algorithm(problem["id"], FUNCTIONS[tier][problem["id"]], case)


@pytest.mark.parametrize("tier", ["regular", "advanced"])
def test_structures_pass_catalog(tier: str) -> None:
    catalog = load_catalog()
    for struct in catalog["data_structures"]:
        for case in struct["cases"]:
            _trace(tier, struct["id"], case["ops"])


@pytest.mark.parametrize("struct_id", ["stack", "queue", "linked_list", "bst", "trie", "min_heap"])
def test_advanced_matches_regular_structures(struct_id: str) -> None:
    catalog = load_catalog()
    for struct in catalog["data_structures"]:
        if struct["id"] != struct_id:
            continue
        for case in struct["cases"]:
            assert _trace("regular", struct_id, case["ops"]) == _trace(
        "advanced", struct_id, case["ops"]
    )


@pytest.mark.parametrize("problem_id", list(FUNCTIONS["regular"]))
def test_advanced_matches_regular_algorithms(problem_id: str) -> None:
    catalog = load_catalog()
    for case in next(p for p in catalog["algorithms"] if p["id"] == problem_id)["cases"]:
        # both tiers must independently pass the same catalog vector set, which
        # transitively guarantees advanced == regular on shared inputs.
        run_algorithm(problem_id, FUNCTIONS["regular"][problem_id], case)
        run_algorithm(problem_id, FUNCTIONS["advanced"][problem_id], case)