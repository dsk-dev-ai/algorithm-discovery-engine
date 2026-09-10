"""Cross-language benchmark workload (mirrors Java/C++/Rust benches).

Fixed seed + fixed sizes so `engine/runner.py bench` can tabulate per-algorithm
wall time. Run directly with `python -m ads.benchmark`.
"""

from __future__ import annotations

import random
import time
from collections.abc import Callable

from ads import problems, problems_advanced


def _random_ints(count: int, seed: int) -> list[int]:
    rng = random.Random(seed)
    return [rng.randrange(1_000_000_000) for _ in range(count)]


def _random_string(length: int, seed: int) -> str:
    rng = random.Random(seed)
    return "".join(rng.choice("abcdefgh") for _ in range(length))


def _chain_graph(size: int) -> list[list[int]]:
    return [
        [neighbor for neighbor in (i - 1, i + 1) if 0 <= neighbor < size]
        for i in range(size)
    ]


def _time_it(label: str, task: Callable[[], object]) -> None:
    started = time.perf_counter()
    task()
    elapsed_us = (time.perf_counter() - started) * 1_000_000
    print(f"{label}: {elapsed_us:.0f} us")


def run() -> None:
    data = _random_ints(200_000, 42)
    sorted_data = list(range(1_000_000))

    _time_it("merge_sort", lambda: problems.merge_sort(data))
    _time_it("quick_sort", lambda: problems.quick_sort(_random_ints(200_000, 42)))
    _time_it(
        "max_subarray",
        lambda: problems_advanced.max_subarray_advanced(_random_ints(500_000, 7)),
    )
    _time_it("two_sum", lambda: problems.two_sum(_random_ints(50_000, 9), -1))
    _time_it(
        "binary_search",
        lambda: problems.binary_search(sorted_data, sorted_data[len(sorted_data) // 2]),
    )
    _time_it(
        "lcs",
        lambda: problems_advanced.lcs_advanced(
            _random_string(2_000, 11), _random_string(2_000, 13)
        ),
    )
    _time_it(
        "knapsack_01",
        lambda: problems_advanced.knapsack_01_advanced(
            5_000, _random_ints(1_000, 21), _random_ints(1_000, 31)
        ),
    )
    _time_it(
        "edit_distance",
        lambda: problems_advanced.edit_distance_advanced(
            _random_string(1_000, 41), _random_string(1_000, 43)
        ),
    )
    _time_it(
        "graph_bfs",
        lambda: problems_advanced.graph_bfs_advanced(_chain_graph(100_000), 0, 99_999),
    )
    _time_it(
        "graph_dfs",
        lambda: problems_advanced.graph_dfs_advanced(_chain_graph(100_000), 0, 99_999),
    )


if __name__ == "__main__":
    run()