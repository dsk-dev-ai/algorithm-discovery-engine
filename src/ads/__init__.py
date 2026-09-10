"""Algorithms & Data Structures solving engine (Python).

Two tiers are provided for every problem:

* :mod:`ads.problems` / :mod:`ads.structures` — the *regular* tier:
  readable, deliberately simple implementations that mirror the Java, C++
  and Rust ports 1:1.
* :mod:`ads.problems_advanced` / :mod:`ads.structures_advanced` — the
  *advanced* tier: memory- and speed-optimized variants (rolling DP,
  in-place sorts, slot-allocated nodes, manual heaps).

A single catalogue (``catalog/problems.json`` at the repo root) holds the
shared test vectors used by all four languages.
"""

from ads.problems import (
    binary_search,
    edit_distance,
    graph_bfs,
    graph_dfs,
    knapsack_01,
    lcs,
    max_subarray,
    merge_sort,
    quick_sort,
    two_sum,
)
from ads.problems_advanced import (
    binary_search_advanced,
    edit_distance_advanced,
    graph_bfs_advanced,
    graph_dfs_advanced,
    knapsack_01_advanced,
    lcs_advanced,
    max_subarray_advanced,
    merge_sort_advanced,
    quick_sort_advanced,
    two_sum_advanced,
)
from ads.structures import BST, LinkedList, MinHeap, Queue, Stack, Trie
from ads.structures_advanced import (
    BSTAdvanced,
    LinkedListAdvanced,
    MinHeapAdvanced,
    QueueAdvanced,
    StackAdvanced,
    TrieAdvanced,
)

__version__ = "1.0.0"

__all__ = [
    "BST",
    "BSTAdvanced",
    "LinkedList",
    "LinkedListAdvanced",
    "MinHeap",
    "MinHeapAdvanced",
    "Queue",
    "QueueAdvanced",
    "Stack",
    "StackAdvanced",
    "Trie",
    "TrieAdvanced",
    "binary_search",
    "binary_search_advanced",
    "edit_distance",
    "edit_distance_advanced",
    "graph_bfs",
    "graph_bfs_advanced",
    "graph_dfs",
    "graph_dfs_advanced",
    "knapsack_01",
    "knapsack_01_advanced",
    "lcs",
    "lcs_advanced",
    "max_subarray",
    "max_subarray_advanced",
    "merge_sort",
    "merge_sort_advanced",
    "quick_sort",
    "quick_sort_advanced",
    "two_sum",
    "two_sum_advanced",
]