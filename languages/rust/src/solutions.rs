//! Classic algorithm solutions (mirrors the Java/C++/Python tiers).

/// Snippet-sentinel returned by searches that miss.
pub const SENTINEL: i32 = -1;

/// Indices of the two values summing to `target`, or `(-1, -1)`.
pub fn two_sum(nums: &[i32], target: i32) -> (i32, i32) {
    for (i, &left) in nums.iter().enumerate() {
        for (j, &right) in nums.iter().enumerate().skip(i + 1) {
            if left + right == target {
                return (i as i32, j as i32);
            }
        }
    }
    (SENTINEL, SENTINEL)
}

/// First-occurrence index of `target` in a sorted slice (lower bound), or -1.
pub fn binary_search(sorted: &[i32], target: i32) -> i32 {
    let mut low = 0usize;
    let mut high = sorted.len();
    while low < high {
        let mid = low + (high - low) / 2;
        if sorted[mid] < target {
            low = mid + 1;
        } else {
            high = mid;
        }
    }
    if low < sorted.len() && sorted[low] == target {
        low as i32
    } else {
        SENTINEL
    }
}

fn merge(left: &[i32], right: &[i32]) -> Vec<i32> {
    let mut merged = Vec::with_capacity(left.len() + right.len());
    let mut i = 0;
    let mut j = 0;
    while i < left.len() && j < right.len() {
        if left[i] <= right[j] {
            merged.push(left[i]);
            i += 1;
        } else {
            merged.push(right[j]);
            j += 1;
        }
    }
    merged.extend_from_slice(&left[i..]);
    merged.extend_from_slice(&right[j..]);
    merged
}

fn quick_sort_range(values: &mut [i32]) {
    if values.len() <= 1 {
        return;
    }
    let pivot_index = values.len() - 1;
    let pivot = values[pivot_index];
    let mut index = 0usize;
    for j in 0..pivot_index {
        if values[j] < pivot {
            values.swap(index, j);
            index += 1;
        }
    }
    values.swap(index, pivot_index);
    quick_sort_range(&mut values[..index]);
    quick_sort_range(&mut values[index + 1..]);
}

/// New array sorted ascending via merge sort.
pub fn merge_sort(nums: &[i32]) -> Vec<i32> {
    if nums.len() <= 1 {
        return nums.to_vec();
    }
    let mid = nums.len() / 2;
    let left = merge_sort(&nums[..mid]);
    let right = merge_sort(&nums[mid..]);
    merge(&left, &right)
}

/// New array sorted ascending via quick sort.
pub fn quick_sort(nums: &[i32]) -> Vec<i32> {
    let mut values = nums.to_vec();
    quick_sort_range(&mut values);
    values
}

/// Maximum contiguous subarray sum (Kadane); empty -> 0.
pub fn max_subarray(nums: &[i32]) -> i32 {
    if nums.is_empty() {
        return 0;
    }
    let mut best = nums[0];
    let mut running = 0;
    for &value in nums {
        running = value.max(running + value);
        best = best.max(running);
    }
    best
}

/// Longest common subsequence length (full-table DP).
pub fn lcs(a: &str, b: &str) -> i32 {
    let a = a.as_bytes();
    let b = b.as_bytes();
    let rows = a.len() + 1;
    let cols = b.len() + 1;
    let mut table = vec![vec![0; cols]; rows];
    for i in 1..rows {
        for j in 1..cols {
            if a[i - 1] == b[j - 1] {
                table[i][j] = table[i - 1][j - 1] + 1;
            } else {
                table[i][j] = table[i - 1][j].max(table[i][j - 1]);
            }
        }
    }
    table[rows - 1][cols - 1]
}

/// Maximum value under the 0/1 knapsack constraint (full-table DP).
pub fn knapsack_01(capacity: usize, weights: &[i32], values: &[i32]) -> i32 {
    let mut dp = vec![vec![0; capacity + 1]; weights.len() + 1];
    for item in 1..=weights.len() {
        let weight = weights[item - 1] as usize;
        let value = values[item - 1];
        for cap in 0..=capacity {
            if weight <= cap {
                dp[item][cap] = dp[item - 1][cap].max(dp[item - 1][cap - weight] + value);
            } else {
                dp[item][cap] = dp[item - 1][cap];
            }
        }
    }
    dp[weights.len()][capacity]
}

/// Levenshtein distance (full-table DP).
pub fn edit_distance(a: &str, b: &str) -> i32 {
    let a = a.as_bytes();
    let b = b.as_bytes();
    let rows = a.len() + 1;
    let cols = b.len() + 1;
    let mut table = vec![vec![0isize; cols]; rows];
    for i in 0..rows {
        table[i][0] = i as isize;
    }
    for j in 0..cols {
        table[0][j] = j as isize;
    }
    for i in 1..rows {
        for j in 1..cols {
            let cost = if a[i - 1] == b[j - 1] { 0 } else { 1 };
            table[i][j] = (table[i - 1][j] + 1)
                .min(table[i][j - 1] + 1)
                .min(table[i - 1][j - 1] + cost);
        }
    }
    table[rows - 1][cols - 1] as i32
}

/// Adjacency list: rows like `"0:1 2;1:0 2"`.
pub fn parse_graph(encoded: &str) -> Vec<Vec<usize>> {
    if encoded.is_empty() {
        return Vec::new();
    }
    let mut graph = Vec::new();
    for row in encoded.split(';') {
        if let Some((_, neighbors)) = row.split_once(':') {
            let parsed = neighbors
                .split_whitespace()
                .filter_map(|part| part.parse::<usize>().ok())
                .collect();
            graph.push(parsed);
        } else {
            graph.push(Vec::new());
        }
    }
    graph
}

/// Length of the shortest unweighted path between `start` and `target`, or -1.
pub fn graph_bfs(graph: &[Vec<usize>], start: usize, target: usize) -> i32 {
    if start == target {
        return 0;
    }
    if start >= graph.len() {
        return SENTINEL;
    }
    let mut distances = vec![SENTINEL; graph.len()];
    distances[start] = 0;
    let mut queue = std::collections::VecDeque::from([start]);
    while let Some(node) = queue.pop_front() {
        let next_distance = distances[node] + 1;
        for &neighbor in &graph[node] {
            if distances[neighbor] != SENTINEL {
                continue;
            }
            distances[neighbor] = next_distance;
            if neighbor == target {
                return next_distance;
            }
            queue.push_back(neighbor);
        }
    }
    SENTINEL
}

/// Whether `target` is reachable from `start` (recursive DFS).
pub fn graph_dfs(graph: &[Vec<usize>], start: usize, target: usize) -> bool {
    if graph.is_empty() {
        return start == target;
    }
    if start >= graph.len() {
        return false;
    }
    let mut visited = vec![false; graph.len()];

    fn visit(graph: &[Vec<usize>], visited: &mut [bool], node: usize, target: usize) -> bool {
        if node == target {
            return true;
        }
        visited[node] = true;
        for &neighbor in &graph[node] {
            if !visited[neighbor] && visit(graph, visited, neighbor, target) {
                return true;
            }
        }
        false
    }

    visit(graph, &mut visited, start, target)
}