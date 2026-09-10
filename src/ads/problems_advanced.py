"""Advanced Python tier: performance-optimized variants.

Each function is behaviorally equivalent to its :mod:`ads.problems`
counterpart but trades verbosity for lower constant factors and better
space usage (rolling DP rows, in-place sorts, iterative graph walks).
"""

from __future__ import annotations

from bisect import bisect_left
from collections import deque


def two_sum_advanced(nums: list[int], target: int) -> list[int]:
    """Two-sum with a single pass and early exit (same contract)."""
    seen: dict[int, int] = {}
    for i, value in enumerate(nums):
        other = target - value
        if other in seen:
            j = seen[other]
            return [min(j, i), max(j, i)]
        seen[value] = i
    return [-1, -1]


def binary_search_advanced(sorted_nums: list[int], target: int) -> int:
    """Lower-bound binary search delegated to the C-accelerated bisect module."""
    index = bisect_left(sorted_nums, target)
    if index < len(sorted_nums) and sorted_nums[index] == target:
        return index
    return -1


def _merge_into(
    source: list[int], left: int, mid: int, right: int, buffer: list[int]
) -> None:
    buffer[left:right] = source[left:right]
    i, j, k = left, mid, left
    while i < mid and j < right:
        if buffer[i] <= buffer[j]:
            source[k] = buffer[i]
            i += 1
        else:
            source[k] = buffer[j]
            j += 1
        k += 1
    while i < mid:
        source[k] = buffer[i]
        i += 1
        k += 1


def merge_sort_advanced(nums: list[int]) -> list[int]:
    """In-place merge sort over a private copy using a single aux buffer."""
    values = list(nums)
    buffer = [0] * len(values)

    width = 1
    while width < len(values):
        left = 0
        while left < len(values):
            mid = min(left + width, len(values))
            right = min(left + 2 * width, len(values))
            if mid < right:
                _merge_into(values, left, mid, right, buffer)
            left += 2 * width
        width *= 2
    return values


def quick_sort_advanced(nums: list[int]) -> list[int]:
    """Iterative in-place quick sort with median-of-three pivot (Lomuto)."""
    values = list(nums)
    stack: list[tuple[int, int]] = [(0, len(values) - 1)]

    def median_of_three(lo: int, hi: int) -> int:
        mid = (lo + hi) // 2
        a, b, c = values[lo], values[mid], values[hi]
        if (a < b) != (a < c):
            return lo
        if (b < a) != (b < c):
            return mid
        return hi

    while stack:
        low, high = stack.pop()
        while low < high:
            pivot_index = median_of_three(low, high)
            values[pivot_index], values[high] = values[high], values[pivot_index]
            pivot = values[high]
            i = low
            for j in range(low, high):
                if values[j] < pivot:
                    values[i], values[j] = values[j], values[i]
                    i += 1
            values[i], values[high] = values[high], values[i]
            if i - low < high - i:
                stack.append((i + 1, high))
                high = i - 1
            else:
                stack.append((low, i - 1))
                low = i + 1
    return values


def max_subarray_advanced(nums: list[int]) -> int:
    """Kadane with stream-friendly fold (same contract, no pre-scan)."""
    best: int | None = None
    running = 0
    for value in nums:
        running = max(value, running + value)
        best = running if best is None else max(best, running)
    return 0 if best is None else best


def lcs_advanced(a: str, b: str) -> int:
    """LCS with O(min(m, n)) space via two rolling rows."""
    if len(a) < len(b):
        a, b = b, a
    previous = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        current = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                current[j] = previous[j - 1] + 1
            else:
                up, left = previous[j], current[j - 1]
                current[j] = up if up >= left else left
        previous = current
    return previous[len(b)]


def knapsack_01_advanced(capacity: int, weights: list[int], values: list[int]) -> int:
    """0/1 knapsack with O(capacity) space via a single rolling row."""
    row = [0] * (capacity + 1)
    for weight, value in zip(weights, values, strict=False):
        if weight > capacity:
            continue
        for cap in range(capacity, weight - 1, -1):
            candidate = row[cap - weight] + value
            if candidate > row[cap]:
                row[cap] = candidate
    return row[capacity]


def edit_distance_advanced(a: str, b: str) -> int:
    """Levenshtein distance with O(min(m, n)) space via two rolling rows."""
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        current = [0] * (len(b) + 1)
        current[0] = i
        for j in range(1, len(b) + 1):
            insert_cost = current[j - 1] + 1
            delete_cost = previous[j] + 1
            substitute = previous[j - 1] + (0 if a[i - 1] == b[j - 1] else 1)
            current[j] = min(insert_cost, delete_cost, substitute)
        previous = current
    return previous[len(b)]


def graph_bfs_advanced(adj: list[list[int]], start: int, target: int) -> int:
    """BFS shortest path using a preallocated distance array and deque."""
    if start == target:
        return 0
    if not adj or not (0 <= start < len(adj)):
        return -1 if target != start else 0
    distances = [-1] * len(adj)
    distances[start] = 0
    pending = deque([start])
    while pending:
        node = pending.popleft()
        steps = distances[node] + 1
        for neighbor in adj[node]:
            if distances[neighbor] != -1:
                continue
            distances[neighbor] = steps
            if neighbor == target:
                return steps
            pending.append(neighbor)
    return -1


def graph_dfs_advanced(adj: list[list[int]], start: int, target: int) -> bool:
    """Iterative DFS with an explicit stack (avoids recursion limits)."""
    if not adj:
        return start == target
    if not (0 <= start < len(adj)):
        return False
    visited = [False] * len(adj)
    pending = [start]
    while pending:
        node = pending.pop()
        if node == target:
            return True
        if visited[node]:
            continue
        visited[node] = True
        for neighbor in adj[node]:
            if not visited[neighbor]:
                pending.append(neighbor)
    return False