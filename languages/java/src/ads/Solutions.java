package ads;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;

/**
 * Reference algorithm implementations (Java).
 *
 * Behavioral contracts match catalog/problems.json exactly.
 * These are deliberately dependency-free and mirror the C++ / Rust / Python
 * ports 1:1.
 */
public final class Solutions {

    private Solutions() {
    }

    /** Indices of the two values summing to target, or {-1, -1}. */
    public static int[] twoSum(int[] nums, int target) {
        java.util.HashMap<Integer, Integer> seen = new java.util.HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            Integer j = seen.get(complement);
            if (j != null) {
                int small = Math.min(j, i);
                int large = Math.max(j, i);
                return new int[] {small, large};
            }
            seen.put(nums[i], i);
        }
        return new int[] {-1, -1};
    }

    /** First-occurrence index of target (lower bound), or -1. */
    public static int binarySearch(int[] sorted, int target) {
        int low = 0;
        int high = sorted.length;
        while (low < high) {
            int mid = (low + high) >>> 1;
            if (sorted[mid] < target) {
                low = mid + 1;
            } else {
                high = mid;
            }
        }
        if (low < sorted.length && sorted[low] == target) {
            return low;
        }
        return -1;
    }

    /** New array sorted ascending via merge sort. */
    public static int[] mergeSort(int[] nums) {
        if (nums.length <= 1) {
            return Arrays.copyOf(nums, nums.length);
        }
        int mid = nums.length / 2;
        int[] left = mergeSort(Arrays.copyOfRange(nums, 0, mid));
        int[] right = mergeSort(Arrays.copyOfRange(nums, mid, nums.length));
        return merge(left, right);
    }

    private static int[] merge(int[] left, int[] right) {
        int[] merged = new int[left.length + right.length];
        int i = 0;
        int j = 0;
        int k = 0;
        while (i < left.length && j < right.length) {
            if (left[i] <= right[j]) {
                merged[k++] = left[i++];
            } else {
                merged[k++] = right[j++];
            }
        }
        while (i < left.length) {
            merged[k++] = left[i++];
        }
        while (j < right.length) {
            merged[k++] = right[j++];
        }
        return merged;
    }

    /** New array sorted ascending via in-place quick sort (Lomuto). */
    public static int[] quickSort(int[] nums) {
        int[] values = Arrays.copyOf(nums, nums.length);
        quickSortRange(values, 0, values.length - 1);
        return values;
    }

    private static void quickSortRange(int[] values, int low, int high) {
        if (low >= high) {
            return;
        }
        int pivot = values[high];
        int i = low;
        for (int j = low; j < high; j++) {
            if (values[j] < pivot) {
                swap(values, i++, j);
            }
        }
        swap(values, i, high);
        quickSortRange(values, low, i - 1);
        quickSortRange(values, i + 1, high);
    }

    private static void swap(int[] values, int i, int j) {
        int tmp = values[i];
        values[i] = values[j];
        values[j] = tmp;
    }

    /** Maximum contiguous subarray sum (Kadane); empty -> 0. */
    public static int maxSubarray(int[] nums) {
        if (nums.length == 0) {
            return 0;
        }
        int best = nums[0];
        int running = 0;
        for (int value : nums) {
            running = Math.max(value, running + value);
            best = Math.max(best, running);
        }
        return best;
    }

    /** Longest common subsequence length (full-table DP). */
    public static int lcs(String a, String b) {
        int rows = a.length() + 1;
        int cols = b.length() + 1;
        int[][] table = new int[rows][cols];
        for (int i = 1; i < rows; i++) {
            for (int j = 1; j < cols; j++) {
                if (a.charAt(i - 1) == b.charAt(j - 1)) {
                    table[i][j] = table[i - 1][j - 1] + 1;
                } else {
                    table[i][j] = Math.max(table[i - 1][j], table[i][j - 1]);
                }
            }
        }
        return table[rows - 1][cols - 1];
    }

    /** Maximum value under the 0/1 knapsack constraint (full-table DP). */
    public static int knapsack01(int capacity, int[] weights, int[] values) {
        int[][] dp = new int[weights.length + 1][capacity + 1];
        for (int item = 1; item <= weights.length; item++) {
            int weight = weights[item - 1];
            int value = values[item - 1];
            for (int cap = 0; cap <= capacity; cap++) {
                if (weight <= cap) {
                    dp[item][cap] = Math.max(
                            dp[item - 1][cap], dp[item - 1][cap - weight] + value);
                } else {
                    dp[item][cap] = dp[item - 1][cap];
                }
            }
        }
        return dp[weights.length][capacity];
    }

    /** Levenshtein distance (full-table DP). */
    public static int editDistance(String a, String b) {
        int rows = a.length() + 1;
        int cols = b.length() + 1;
        int[][] table = new int[rows][cols];
        for (int i = 0; i < rows; i++) {
            table[i][0] = i;
        }
        for (int j = 0; j < cols; j++) {
            table[0][j] = j;
        }
        for (int i = 1; i < rows; i++) {
            for (int j = 1; j < cols; j++) {
                int cost = a.charAt(i - 1) == b.charAt(j - 1) ? 0 : 1;
                table[i][j] = Math.min(
                        table[i - 1][j] + 1,
                        Math.min(table[i][j - 1] + 1, table[i - 1][j - 1] + cost));
            }
        }
        return table[rows - 1][cols - 1];
    }

    /** Shortest unweighted path length from start to target, or -1. */
    public static int graphBfs(List<List<Integer>> graph, int start, int target) {
        if (start == target) {
            return 0;
        }
        if (start < 0 || start >= graph.size()) {
            return -1;
        }
        int[] distances = new int[graph.size()];
        Arrays.fill(distances, -1);
        distances[start] = 0;
        java.util.ArrayDeque<Integer> queue = new java.util.ArrayDeque<>();
        queue.add(start);
        while (!queue.isEmpty()) {
            int node = queue.poll();
            for (int neighbor : graph.get(node)) {
                if (distances[neighbor] != -1) {
                    continue;
                }
                distances[neighbor] = distances[node] + 1;
                if (neighbor == target) {
                    return distances[neighbor];
                }
                queue.add(neighbor);
            }
        }
        return -1;
    }

    /** Whether target is reachable from start (iterative DFS). */
    public static boolean graphDfs(List<List<Integer>> graph, int start, int target) {
        if (graph.isEmpty()) {
            return start == target;
        }
        if (start < 0 || start >= graph.size()) {
            return false;
        }
        boolean[] visited = new boolean[graph.size()];
        java.util.ArrayDeque<Integer> stack = new java.util.ArrayDeque<>();
        stack.push(start);
        while (!stack.isEmpty()) {
            int node = stack.pop();
            if (node == target) {
                return true;
            }
            if (visited[node]) {
                continue;
            }
            visited[node] = true;
            List<Integer> neighbors = graph.get(node);
            for (int i = neighbors.size() - 1; i >= 0; i--) {
                int neighbor = neighbors.get(i);
                if (!visited[neighbor]) {
                    stack.push(neighbor);
                }
            }
        }
        return false;
    }

    /** Parse an adjacency-list string like "0:1 2;1:0 2" into a graph. */
    public static List<List<Integer>> parseGraph(String encoded) {
        List<List<Integer>> graph = new ArrayList<>();
        if (encoded.isEmpty()) {
            return graph;
        }
        String[] rows = encoded.split(";");
        for (String row : rows) {
            String[] parts = row.split(":");
            List<Integer> neighbors = new ArrayList<>();
            if (parts.length > 1 && !parts[1].isBlank()) {
                String[] tokens = parts[1].trim().split("\\s+");
                for (String token : tokens) {
                    neighbors.add(Integer.parseInt(token));
                }
            }
            graph.add(neighbors);
        }
        return graph;
    }
}