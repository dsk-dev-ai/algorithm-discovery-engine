"""Regular Python tier: readable baseline implementations.

These mirror the Java / C++ / Rust ports 1:1 and favour clarity over raw
performance. The advanced tier (:mod:`ads.problems_advanced`) provides the
memory/speed-optimized variants.
"""

from __future__ import annotations

from collections import deque


def two_sum(nums: list[int], target: int) -> list[int]:
    """Indices of the two numbers summing to *target* (or ``[-1, -1]``)."""
    seen: dict[int, int] = {}
    for i, value in enumerate(nums):
        complement = target - value
        if complement in seen:
            j = seen[complement]
            return [j, i] if j < i else [i, j]
        seen[value] = i
    return [-1, -1]


def binary_search(sorted_nums: list[int], target: int) -> int:
    """Index of the first occurrence of *target* (lower bound), or ``-1``."""
    low, high = 0, len(sorted_nums)
    while low < high:
        mid = (low + high) // 2
        if sorted_nums[mid] < target:
            low = mid + 1
        else:
            high = mid
    if low < len(sorted_nums) and sorted_nums[low] == target:
        return low
    return -1


def _merge(left: list[int], right: list[int]) -> list[int]:
    merged: list[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def merge_sort(nums: list[int]) -> list[int]:
    """Return a new array sorted ascending (classic merge sort)."""
    if len(nums) <= 1:
        return list(nums)
    mid = len(nums) // 2
    return _merge(merge_sort(nums[:mid]), merge_sort(nums[mid:]))


def _partition(nums: list[int], low: int, high: int) -> int:
    pivot = nums[high]
    i = low
    for j in range(low, high):
        if nums[j] < pivot:
            nums[i], nums[j] = nums[j], nums[i]
            i += 1
    nums[i], nums[high] = nums[high], nums[i]
    return i


def quick_sort(nums: list[int]) -> list[int]:
    """Return a new array sorted ascending (in-place quick sort behind the scenes)."""
    values = list(nums)

    def sort_region(low: int, high: int) -> None:
        if low >= high:
            return
        split = _partition(values, low, high)
        sort_region(low, split - 1)
        sort_region(split + 1, high)

    sort_region(0, len(values) - 1)
    return values


def max_subarray(nums: list[int]) -> int:
    """Maximum contiguous subarray sum (Kadane). Empty -> 0."""
    best = 0 if not nums else nums[0]
    running = 0
    for value in nums:
        running = max(value, running + value)
        best = max(best, running)
    return best


def lcs(a: str, b: str) -> int:
    """Longest common subsequence length (full-table DP)."""
    rows, cols = len(a) + 1, len(b) + 1
    table = [[0] * cols for _ in range(rows)]
    for i in range(1, rows):
        for j in range(1, cols):
            if a[i - 1] == b[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1
            else:
                table[i][j] = max(table[i - 1][j], table[i][j - 1])
    return table[rows - 1][cols - 1]


def knapsack_01(capacity: int, weights: list[int], values: list[int]) -> int:
    """Maximum value with the 0/1 knapsack constraint (full-table DP)."""
    dp = [[0] * (capacity + 1) for _ in range(len(weights) + 1)]
    for item in range(1, len(weights) + 1):
        weight, value = weights[item - 1], values[item - 1]
        row_before, row_now = dp[item - 1], dp[item]
        for cap in range(capacity + 1):
            if weight <= cap:
                row_now[cap] = max(row_before[cap], row_before[cap - weight] + value)
            else:
                row_now[cap] = row_before[cap]
    return dp[len(weights)][capacity]


def edit_distance(a: str, b: str) -> int:
    """Levenshtein distance (full-table DP): insert/delete/substitute."""
    rows, cols = len(a) + 1, len(b) + 1
    table = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        table[i][0] = i
    for j in range(cols):
        table[0][j] = j
    for i in range(1, rows):
        for j in range(1, cols):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            table[i][j] = min(
                table[i - 1][j] + 1,
                table[i][j - 1] + 1,
                table[i - 1][j - 1] + cost,
            )
    return table[rows - 1][cols - 1]


def _parse_adjacency(encoded: str) -> list[list[int]]:
    adj: list[list[int]] = []
    for row in encoded.split(";"):
        parts = row.split(":")
        neighbors: list[int] = []
        if parts[1].strip():
            neighbors = [int(n) for n in filter(None, parts[1].split())]
        adj.append(neighbors)
    return adj


def graph_bfs(adj: list[list[int]], start: int, target: int) -> int:
    """Shortest path length in edges from *start* to *target*, ``-1`` unreachable."""
    if start == target:
        return 0
    if start >= len(adj):
        return -1
    distances = [-1] * len(adj)
    distances[start] = 0
    pending = deque([start])
    while pending:
        node = pending.popleft()
        for neighbor in adj[node]:
            if distances[neighbor] != -1:
                continue
            distances[neighbor] = distances[node] + 1
            if neighbor == target:
                return distances[neighbor]
            pending.append(neighbor)
    return -1


def graph_dfs(adj: list[list[int]], start: int, target: int) -> bool:
    """Whether *target* is reachable from *start* (iterative depth-first search)."""

    def visit(node: int, seen: set[int] | None = None) -> bool:
        seen = set() if seen is None else seen
        if node == target:
            return True
        seen.add(node)
        return any(
            neighbor not in seen and visit(neighbor, seen) for neighbor in adj[node]
        )

    if not adj and start != target:
        return False
    return visit(start)