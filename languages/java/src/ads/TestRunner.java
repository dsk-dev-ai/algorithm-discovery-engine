package ads;

import ads.gen.TestData;
import java.util.List;

/**
 * Runs every catalog vector against the Java implementations and asserts the
 * expected output. Exit status 0 == all pass; 1 == any failure.
 */
public final class TestRunner {

    private static int failures;
    private static int passed;

    private TestRunner() {
    }

    public static void main(String[] args) {
        runAlgorithms();
        runStructures();
        System.out.printf("Java: %d passed, %d failed.%n", passed, failures);
        if (failures > 0) {
            System.exit(1);
        }
    }

    // ---- parsing helpers ----------------------------------------------------

    private static int[] parseInts(String token) {
        if (token == null || token.isBlank()) {
            return new int[0];
        }
        String[] parts = token.trim().split("\\s+");
        int[] out = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            out[i] = Integer.parseInt(parts[i]);
        }
        return out;
    }

    private static List<List<Integer>> parseGraph(String token) {
        return Solutions.parseGraph(token);
    }

    // ---- algorithm dispatch -------------------------------------------------

    private static String[] ids = {
        "two_sum", "binary_search", "merge_sort", "quick_sort",
        "max_subarray", "lcs", "knapsack_01", "edit_distance",
        "graph_bfs", "graph_dfs"
    };

    private static void runAlgorithms() {
        String[][][] data = TestData.ALGORITHMS;
        for (int p = 0; p < ids.length; p++) {
            for (String[] caseVec : data[p]) {
                check(ids[p], caseVec[0], caseVec[1]);
            }
        }
    }

    private static void check(String id, String input, String expected) {
        String[] parts = input.split("\\|", -1);
        try {
            switch (id) {
                case "two_sum": {
                    int[] got = Solutions.twoSum(parseInts(parts[0]), Integer.parseInt(parts[1]));
                    checkIntArr(id, input, expected, got, parseInts(expected));
                    break;
                }
                case "binary_search": {
                    int got = Solutions.binarySearch(parseInts(parts[0]), Integer.parseInt(parts[1]));
                    checkInt(id, input, expected, got, Integer.parseInt(expected));
                    break;
                }
                case "merge_sort":
                case "quick_sort": {
                    int[] got = id.equals("merge_sort")
                            ? Solutions.mergeSort(parseInts(input))
                            : Solutions.quickSort(parseInts(input));
                    checkIntArr(id, input, expected, got, parseInts(expected));
                    break;
                }
                case "max_subarray": {
                    int got = Solutions.maxSubarray(parseInts(parts[0]));
                    checkInt(id, input, expected, got, Integer.parseInt(expected));
                    break;
                }
                case "lcs": {
                    int got = Solutions.lcs(parts[0], parts[1]);
                    checkInt(id, input, expected, got, Integer.parseInt(expected));
                    break;
                }
                case "knapsack_01": {
                    int got = Solutions.knapsack01(
                            Integer.parseInt(parts[0]), parseInts(parts[1]), parseInts(parts[2]));
                    checkInt(id, input, expected, got, Integer.parseInt(expected));
                    break;
                }
                case "edit_distance": {
                    int got = Solutions.editDistance(parts[0], parts[1]);
                    checkInt(id, input, expected, got, Integer.parseInt(expected));
                    break;
                }
                case "graph_bfs": {
                    int got = Solutions.graphBfs(
                            parseGraph(parts[0]), Integer.parseInt(parts[1]), Integer.parseInt(parts[2]));
                    checkInt(id, input, expected, got, Integer.parseInt(expected));
                    break;
                }
                case "graph_dfs": {
                    boolean got = Solutions.graphDfs(
                            parseGraph(parts[0]), Integer.parseInt(parts[1]), Integer.parseInt(parts[2]));
                    boolean want = expected.equals("true");
                    if (got != want) {
                        recordFailure(id, input, String.valueOf(got), expected);
                    } else {
                        passed++;
                    }
                    break;
                }
                default:
                    throw new IllegalStateException("unhandled " + id);
            }
        } catch (RuntimeException e) {
            recordFailure(id, input, "<exception>", expected);
        }
    }

    private static void checkInt(String id, String input, String expected, int got, int want) {
        if (got != want) {
            recordFailure(id, input, String.valueOf(got), expected);
        } else {
            passed++;
        }
    }

    private static void checkIntArr(
            String id, String input, String expected, int[] got, int[] want) {
        if (got.length != want.length) {
            recordFailure(id, input, java.util.Arrays.toString(got), expected);
            return;
        }
        for (int i = 0; i < got.length; i++) {
            if (got[i] != want[i]) {
                recordFailure(id, input, java.util.Arrays.toString(got), expected);
                return;
            }
        }
        passed++;
    }

    private static void recordFailure(String id, String input, String got, String expected) {
        failures++;
        System.out.printf(
                "FAIL %s input=%s -> got %s, expected %s%n", id, input, got, expected);
    }

    // ---- structures ----------------------------------------------------------

    private static String[] structIds = {
        "stack", "queue", "linked_list", "bst", "trie", "min_heap"
    };

    private static void runStructures() {
        String[][][] data = TestData.STRUCTURES;
        for (int i = 0; i < structIds.length; i++) {
            for (String[] caseVec : data[i]) {
                checkOps(structIds[i], caseVec[0]);
            }
        }
    }

    private static void checkOps(String id, String encoded) {
        Object instance = newInstance(id);
        for (String token : encoded.split(",", -1)) {
            if (token.isBlank()) {
                continue;
            }
            String[] parts = token.split(":", -1);
            String op = parts[0];
            String arg = "";
            String expected = "";
            if (voidOps().contains(op)) {
                arg = parts.length > 1 ? parts[1] : "";
            } else if (resultOps().contains(op)) {
                expected = parts.length > 1 ? parts[1] : "";
            } else {
                arg = parts.length > 1 ? parts[1] : "";
                expected = parts.length > 2 ? parts[2] : "";
            }
            applyOp(instance, op, arg, expected);
        }
    }

    private static java.util.Set<String> voidOps() {
        return java.util.Set.of("push", "enqueue", "append", "prepend", "insert");
    }

    private static java.util.Set<String> resultOps() {
        return java.util.Set.of(
                "pop", "dequeue", "peek", "size", "is_empty",
                "min", "max", "height", "to_list", "in_order");
    }

    private static Object newInstance(String id) {
        switch (id) {
            case "stack":
                return new Structures.Stack();
            case "queue":
                return new Structures.Queue();
            case "linked_list":
                return new Structures.LinkedList();
            case "bst":
                return new Structures.BST();
            case "trie":
                return new Structures.Trie();
            case "min_heap":
                return new Structures.MinHeap();
            default:
                throw new IllegalStateException("unhandled structure " + id);
        }
    }

    private static void applyOp(Object instance, String op, String arg, String expected) {
        if (instance instanceof Structures.Stack stack) {
            applyStack(stack, op, arg, expected);
        } else if (instance instanceof Structures.Queue queue) {
            applyQueue(queue, op, arg, expected);
        } else if (instance instanceof Structures.LinkedList list) {
            applyList(list, op, arg, expected);
        } else if (instance instanceof Structures.BST bst) {
            applyBst(bst, op, arg, expected);
        } else if (instance instanceof Structures.Trie trie) {
            applyTrie(trie, op, arg, expected);
        } else if (instance instanceof Structures.MinHeap heap) {
            applyHeap(heap, op, arg, expected);
        } else {
            throw new IllegalStateException("no handler for " + instance.getClass());
        }
    }

    private static boolean hasExpected(String expected) {
        return !expected.isEmpty();
    }

    private static void applyStack(Structures.Stack stack, String op, String arg, String expected) {
        switch (op) {
            case "push":
                stack.push(Integer.parseInt(arg));
                break;
            case "pop":
                expect(result(stack.pop()), expected, "stack.pop");
                break;
            case "peek":
                expect(result(stack.peek()), expected, "stack.peek");
                break;
            case "is_empty":
                expect(stack.isEmpty() ? "true" : "false", expected, "stack.is_empty");
                break;
            case "size":
                expect(result(stack.size()), expected, "stack.size");
                break;
            default:
                throw new IllegalStateException("stack op " + op);
        }
    }

    private static void applyQueue(Structures.Queue queue, String op, String arg, String expected) {
        switch (op) {
            case "enqueue":
                queue.enqueue(Integer.parseInt(arg));
                break;
            case "dequeue":
                expect(result(queue.dequeue()), expected, "queue.dequeue");
                break;
            case "peek":
                expect(result(queue.peek()), expected, "queue.peek");
                break;
            case "is_empty":
                expect(queue.isEmpty() ? "true" : "false", expected, "queue.is_empty");
                break;
            case "size":
                expect(result(queue.size()), expected, "queue.size");
                break;
            default:
                throw new IllegalStateException("queue op " + op);
        }
    }

    private static void applyList(Structures.LinkedList list, String op, String arg, String expected) {
        switch (op) {
            case "append":
                list.append(Integer.parseInt(arg));
                break;
            case "prepend":
                list.prepend(Integer.parseInt(arg));
                break;
            case "get":
                expect(result(list.get(Integer.parseInt(arg))), expected, "list.get");
                break;
            case "contains":
                expect(list.contains(Integer.parseInt(arg)) ? "true" : "false", expected, "list.contains");
                break;
            case "remove":
                expect(list.remove(Integer.parseInt(arg)) ? "true" : "false", expected, "list.remove");
                break;
            case "size":
                expect(result(list.size()), expected, "list.size");
                break;
            case "to_list":
                expectes(ListToStr(list.toList()), expected, "list.to_list");
                break;
            default:
                throw new IllegalStateException("list op " + op);
        }
    }

    private static void applyBst(Structures.BST bst, String op, String arg, String expected) {
        switch (op) {
            case "insert":
                bst.insert(Integer.parseInt(arg));
                break;
            case "contains":
                expect(bst.contains(Integer.parseInt(arg)) ? "true" : "false", expected, "bst.contains");
                break;
            case "remove":
                expect(bst.remove(Integer.parseInt(arg)) ? "true" : "false", expected, "bst.remove");
                break;
            case "min":
                expect(result(bst.min()), expected, "bst.min");
                break;
            case "max":
                expect(result(bst.max()), expected, "bst.max");
                break;
            case "height":
                expect(result(bst.height()), expected, "bst.height");
                break;
            case "size":
                expect(result(bst.size()), expected, "bst.size");
                break;
            case "in_order":
                expectes(ListToStr(bst.inOrder()), expected, "bst.in_order");
                break;
            default:
                throw new IllegalStateException("bst op " + op);
        }
    }

    private static void applyTrie(Structures.Trie trie, String op, String arg, String expected) {
        switch (op) {
            case "insert":
                trie.insert(arg);
                break;
            case "search":
                expect(trie.search(arg) ? "true" : "false", expected, "trie.search");
                break;
            case "starts_with":
                expect(trie.startsWith(arg) ? "true" : "false", expected, "trie.starts_with");
                break;
            case "size":
                expect(result(trie.size()), expected, "trie.size");
                break;
            default:
                throw new IllegalStateException("trie op " + op);
        }
    }

    private static void applyHeap(Structures.MinHeap heap, String op, String arg, String expected) {
        switch (op) {
            case "push":
                heap.push(Integer.parseInt(arg));
                break;
            case "pop":
                expect(result(heap.pop()), expected, "heap.pop");
                break;
            case "peek":
                expect(result(heap.peek()), expected, "heap.peek");
                break;
            case "is_empty":
                expect(heap.isEmpty() ? "true" : "false", expected, "heap.is_empty");
                break;
            case "size":
                expect(result(heap.size()), expected, "heap.size");
                break;
            default:
                throw new IllegalStateException("heap op " + op);
        }
    }

    private static String result(int value) {
        return String.valueOf(value);
    }

    private static String ListToStr(List<Integer> values) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < values.size(); i++) {
            if (i > 0) {
                sb.append(' ');
            }
            sb.append(values.get(i));
        }
        return sb.toString();
    }

    private static void expect(String got, String expected, String label) {
        if (got.equals(expected)) {
            passed++;
        } else {
            recordFailure(label, "<op>", got, expected);
        }
    }

    private static void expectes(String got, String expected, String label) {
        expect(got.trim(), expected.trim(), label);
    }
}