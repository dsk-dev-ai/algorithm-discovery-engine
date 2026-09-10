#pragma once

#include <algorithm>
#include <cstddef>
#include <string>
#include <utility>
#include <vector>

namespace ads {

// --- algorithms --------------------------------------------------------------

/// Indices of the two values summing to target, or {-1, -1}.
inline std::vector<int> two_sum(const std::vector<int>& nums, int target) {
    std::vector<std::pair<int, int>> seen;
    seen.reserve(nums.size());
    for (std::size_t i = 0; i < nums.size(); ++i) {
        for (const auto& [value, index] : seen) {
            if (value == target - nums[i]) {
                std::size_t small = std::min(index, static_cast<int>(i));
                std::size_t large = std::max(index, static_cast<int>(i));
                return {static_cast<int>(small), static_cast<int>(large)};
            }
        }
        seen.emplace_back(nums[i], static_cast<int>(i));
    }
    return {-1, -1};
}

/// First-occurrence index of target (lower bound), or -1.
inline int binary_search(const std::vector<int>& sorted, int target) {
    std::size_t low = 0;
    std::size_t high = sorted.size();
    while (low < high) {
        std::size_t mid = low + (high - low) / 2;
        if (sorted[mid] < target) {
            low = mid + 1;
        } else {
            high = mid;
        }
    }
    if (low < sorted.size() && sorted[low] == target) {
        return static_cast<int>(low);
    }
    return -1;
}

namespace detail {

inline std::vector<int> merge(const std::vector<int>& left,
                              const std::vector<int>& right) {
    std::vector<int> merged;
    merged.reserve(left.size() + right.size());
    std::size_t i = 0;
    std::size_t j = 0;
    while (i < left.size() && j < right.size()) {
        if (left[i] <= right[j]) {
            merged.push_back(left[i++]);
        } else {
            merged.push_back(right[j++]);
        }
    }
    merged.insert(merged.end(), left.begin() + static_cast<ptrdiff_t>(i), left.end());
    merged.insert(merged.end(), right.begin() + static_cast<ptrdiff_t>(j), right.end());
    return merged;
}

inline void quick_sort_range(std::vector<int>& values, int low, int high) {
    if (low >= high) {
        return;
    }
    int pivot = values[static_cast<std::size_t>(high)];
    int i = low;
    for (int j = low; j < high; ++j) {
        if (values[static_cast<std::size_t>(j)] < pivot) {
            std::swap(values[static_cast<std::size_t>(i)],
                      values[static_cast<std::size_t>(j)]);
            ++i;
        }
    }
    std::swap(values[static_cast<std::size_t>(i)],
              values[static_cast<std::size_t>(high)]);
    quick_sort_range(values, low, i - 1);
    quick_sort_range(values, i + 1, high);
}

}  // namespace detail

/// New array sorted ascending via merge sort.
inline std::vector<int> merge_sort(const std::vector<int>& nums) {
    if (nums.size() <= 1) {
        return nums;
    }
    std::size_t mid = nums.size() / 2;
    std::vector<int> left(nums.begin(), nums.begin() + static_cast<ptrdiff_t>(mid));
    std::vector<int> right(nums.begin() + static_cast<ptrdiff_t>(mid), nums.end());
    return detail::merge(merge_sort(left), merge_sort(right));
}

/// New array sorted ascending via quick sort.
inline std::vector<int> quick_sort(const std::vector<int>& nums) {
    std::vector<int> values = nums;
    detail::quick_sort_range(values, 0, static_cast<int>(values.size()) - 1);
    return values;
}

/// Maximum contiguous subarray sum (Kadane); empty -> 0.
inline int max_subarray(const std::vector<int>& nums) {
    if (nums.empty()) {
        return 0;
    }
    int best = nums.front();
    int running = 0;
    for (int value : nums) {
        running = std::max(value, running + value);
        best = std::max(best, running);
    }
    return best;
}

/// Longest common subsequence length (full-table DP).
inline int lcs(const std::string& a, const std::string& b) {
    std::size_t rows = a.size() + 1;
    std::size_t cols = b.size() + 1;
    std::vector<std::vector<int>> table(rows, std::vector<int>(cols, 0));
    for (std::size_t i = 1; i < rows; ++i) {
        for (std::size_t j = 1; j < cols; ++j) {
            if (a[i - 1] == b[j - 1]) {
                table[i][j] = table[i - 1][j - 1] + 1;
            } else {
                table[i][j] = std::max(table[i - 1][j], table[i][j - 1]);
            }
        }
    }
    return table[rows - 1][cols - 1];
}

/// Maximum value under the 0/1 knapsack constraint (full-table DP).
inline int knapsack_01(int capacity, const std::vector<int>& weights,
                       const std::vector<int>& values) {
    std::vector<std::vector<int>> dp(weights.size() + 1,
                                     std::vector<int>(capacity + 1, 0));
    for (std::size_t item = 1; item <= weights.size(); ++item) {
        int weight = weights[item - 1];
        int value = values[item - 1];
        for (int cap = 0; cap <= capacity; ++cap) {
            if (weight <= cap) {
                dp[item][cap] = std::max(
                    dp[item - 1][cap], dp[item - 1][cap - weight] + value);
            } else {
                dp[item][cap] = dp[item - 1][cap];
            }
        }
    }
    return dp[weights.size()][capacity];
}

/// Levenshtein distance (full-table DP).
inline int edit_distance(const std::string& a, const std::string& b) {
    std::size_t rows = a.size() + 1;
    std::size_t cols = b.size() + 1;
    std::vector<std::vector<int>> table(rows, std::vector<int>(cols, 0));
    for (std::size_t i = 0; i < rows; ++i) {
        table[i][0] = static_cast<int>(i);
    }
    for (std::size_t j = 0; j < cols; ++j) {
        table[0][j] = static_cast<int>(j);
    }
    for (std::size_t i = 1; i < rows; ++i) {
        for (std::size_t j = 1; j < cols; ++j) {
            int cost = (a[i - 1] == b[j - 1]) ? 0 : 1;
            table[i][j] = std::min(
                {table[i - 1][j] + 1, table[i][j - 1] + 1, table[i - 1][j - 1] + cost});
        }
    }
    return table[rows - 1][cols - 1];
}

/// Shortest unweighted path length from start to target, or -1.
inline int graph_bfs(const std::vector<std::vector<int>>& graph, int start,
                     int target) {
    if (start == target) {
        return 0;
    }
    if (start < 0 || static_cast<std::size_t>(start) >= graph.size()) {
        return -1;
    }
    std::vector<int> distances(graph.size(), -1);
    distances[static_cast<std::size_t>(start)] = 0;
    std::vector<int> queue{start};
    std::size_t head = 0;
    while (head < queue.size()) {
        int node = queue[head++];
        for (int neighbor : graph[static_cast<std::size_t>(node)]) {
            if (distances[static_cast<std::size_t>(neighbor)] != -1) {
                continue;
            }
            distances[static_cast<std::size_t>(neighbor)] =
                distances[static_cast<std::size_t>(node)] + 1;
            if (neighbor == target) {
                return distances[static_cast<std::size_t>(neighbor)];
            }
            queue.push_back(neighbor);
        }
    }
    return -1;
}

/// Whether target is reachable from start (recursive DFS).
inline bool graph_dfs(const std::vector<std::vector<int>>& graph, int start,
                      int target) {
    std::vector<bool> visited(graph.size(), false);

    auto visit = [&](auto&& self, int node) -> bool {
        if (node == target) {
            return true;
        }
        visited[static_cast<std::size_t>(node)] = true;
        for (int neighbor : graph[static_cast<std::size_t>(node)]) {
            if (!visited[static_cast<std::size_t>(neighbor)] &&
                self(self, neighbor)) {
                return true;
            }
        }
        return false;
    };

    if (graph.empty()) {
        return start == target;
    }
    if (start < 0 || static_cast<std::size_t>(start) >= graph.size()) {
        return false;
    }
    return visit(visit, start);
}

}  // namespace ads