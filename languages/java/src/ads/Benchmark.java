package ads;

import java.util.List;
import java.util.Random;

/**
 * Cross-language benchmark workloads.
 *
 * Each language ships an equivalent benchmark so runner.py can tabulate wall
 * time per algorithm. Fixed seed + fixed sizes keep results comparable.
 */
public final class Benchmark {

    private Benchmark() {
    }

    public static void main(String[] args) {
        int[] data = randomInts(200_000, 42);
        int[] sorted = sortedInts(1_000_000);

        time("merge_sort", () -> Solutions.mergeSort(data));
        time("quick_sort", () -> Solutions.quickSort(randomInts(200_000, 42)));
        time("max_subarray", () -> Solutions.maxSubarray(randomInts(500_000, 7)));
        time("two_sum", () -> Solutions.twoSum(randomInts(50_000, 9), -1));
        time("binary_search", () -> Solutions.binarySearch(sorted, sorted[sorted.length / 2]));
        time("lcs", () -> Solutions.lcs(randomString(2_000, 11), randomString(2_000, 13)));
        time("knapsack_01", () -> Solutions.knapsack01(5_000, randomInts(1_000, 21), randomInts(1_000, 31)));
        time("edit_distance", () -> Solutions.editDistance(randomString(1_000, 41), randomString(1_000, 43)));
        time("graph_bfs", () -> Solutions.graphBfs(chainGraph(100_000), 0, 99_999));
        time("graph_dfs", () -> Solutions.graphDfs(chainGraph(100_000), 0, 99_999));
    }

    private static void time(String label, Runnable task) {
        long start = System.nanoTime();
        task.run();
        long elapsed = (System.nanoTime() - start) / 1_000;
        System.out.printf("%s: %d us%n", label, elapsed);
    }

    private static int[] randomInts(int n, int seed) {
        Random random = new Random(seed);
        int[] out = new int[n];
        for (int i = 0; i < n; i++) {
            out[i] = random.nextInt(1_000_000_000);
        }
        return out;
    }

    private static int[] sortedInts(int n) {
        int[] out = new int[n];
        for (int i = 0; i < n; i++) {
            out[i] = i;
        }
        return out;
    }

    private static String randomString(int length, int seed) {
        Random random = new Random(seed);
        StringBuilder sb = new StringBuilder(length);
        for (int i = 0; i < length; i++) {
            sb.append((char) ('a' + random.nextInt(8)));
        }
        return sb.toString();
    }

    private static List<List<Integer>> chainGraph(int size) {
        List<List<Integer>> graph = new java.util.ArrayList<>(size);
        for (int i = 0; i < size; i++) {
            List<Integer> neighbors = new java.util.ArrayList<>(2);
            if (i > 0) {
                neighbors.add(i - 1);
            }
            if (i < size - 1) {
                neighbors.add(i + 1);
            }
            graph.add(neighbors);
        }
        return graph;
    }
}