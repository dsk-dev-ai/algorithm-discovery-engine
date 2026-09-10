package ads;

import java.util.ArrayList;
import java.util.List;

/**
 * Data-structure implementations (Java).
 *
 * Operation contracts match catalog/problems.json. Sentinel value for
 * missing/empty reads is -1 and is used consistently across all languages.
 */
public final class Structures {

    private Structures() {
    }

    /** LIFO stack backed by an array list. */
    public static final class Stack {
        private final List<Integer> items = new ArrayList<>();

        public void push(int value) {
            items.add(value);
        }

        public int pop() {
            return items.isEmpty() ? -1 : items.remove(items.size() - 1);
        }

        public int peek() {
            return items.isEmpty() ? -1 : items.get(items.size() - 1);
        }

        public boolean isEmpty() {
            return items.isEmpty();
        }

        public int size() {
            return items.size();
        }
    }

    /** FIFO queue backed by an array list ring offset. */
    public static final class Queue {
        private final List<Integer> items = new ArrayList<>();
        private int head;

        public void enqueue(int value) {
            items.add(value);
        }

        public int dequeue() {
            if (size() == 0) {
                return -1;
            }
            return items.get(head++);
        }

        public int peek() {
            return size() == 0 ? -1 : items.get(head);
        }

        public boolean isEmpty() {
            return size() == 0;
        }

        public int size() {
            return items.size() - head;
        }
    }

    /** Singly linked list. */
    public static final class LinkedList {
        private static final class Node {
            int value;
            Node next;

            Node(int value) {
                this.value = value;
            }
        }

        private Node head;
        private Node tail;
        private int count;

        public void append(int value) {
            Node node = new Node(value);
            if (tail == null) {
                head = tail = node;
            } else {
                tail.next = node;
                tail = node;
            }
            count++;
        }

        public void prepend(int value) {
            Node node = new Node(value);
            node.next = head;
            head = node;
            if (tail == null) {
                tail = node;
            }
            count++;
        }

        public int get(int index) {
            if (index < 0 || index >= count) {
                return -1;
            }
            Node node = head;
            for (int i = 0; i < index; i++) {
                node = node.next;
            }
            return node == null ? -1 : node.value;
        }

        public boolean contains(int value) {
            Node node = head;
            while (node != null) {
                if (node.value == value) {
                    return true;
                }
                node = node.next;
            }
            return false;
        }

        public boolean remove(int value) {
            Node previous = null;
            Node node = head;
            while (node != null) {
                if (node.value == value) {
                    if (previous == null) {
                        head = node.next;
                    } else {
                        previous.next = node.next;
                    }
                    if (node == tail) {
                        tail = previous;
                    }
                    count--;
                    return true;
                }
                previous = node;
                node = node.next;
            }
            return false;
        }

        public int size() {
            return count;
        }

        public List<Integer> toList() {
            List<Integer> out = new ArrayList<>();
            Node node = head;
            while (node != null) {
                out.add(node.value);
                node = node.next;
            }
            return out;
        }
    }

    /** Binary search tree. */
    public static final class BST {
        private static final class Node {
            int value;
            Node left;
            Node right;

            Node(int value) {
                this.value = value;
            }
        }

        private Node root;
        private int count;

        public void insert(int value) {
            if (root == null) {
                root = new Node(value);
                count = 1;
                return;
            }
            Node node = root;
            while (true) {
                if (value < node.value) {
                    if (node.left == null) {
                        node.left = new Node(value);
                        break;
                    }
                    node = node.left;
                } else if (value > node.value) {
                    if (node.right == null) {
                        node.right = new Node(value);
                        break;
                    }
                    node = node.right;
                } else {
                    return;
                }
            }
            count++;
        }

        public boolean contains(int value) {
            Node node = root;
            while (node != null) {
                if (value == node.value) {
                    return true;
                }
                node = value < node.value ? node.left : node.right;
            }
            return false;
        }

        public int min() {
            Node node = root;
            if (node == null) {
                return -1;
            }
            while (node.left != null) {
                node = node.left;
            }
            return node.value;
        }

        public int max() {
            Node node = root;
            if (node == null) {
                return -1;
            }
            while (node.right != null) {
                node = node.right;
            }
            return node.value;
        }

        public int height() {
            return heightOf(root);
        }

        private static int heightOf(Node node) {
            if (node == null) {
                return -1;
            }
            return 1 + Math.max(heightOf(node.left), heightOf(node.right));
        }

        public int size() {
            return count;
        }

        public List<Integer> inOrder() {
            List<Integer> out = new ArrayList<>();
            inOrderOf(root, out);
            return out;
        }

        private static void inOrderOf(Node node, List<Integer> out) {
            if (node == null) {
                return;
            }
            inOrderOf(node.left, out);
            out.add(node.value);
            inOrderOf(node.right, out);
        }

        public boolean remove(int value) {
            if (!contains(value)) {
                return false;
            }
            root = removeNode(root, value);
            count--;
            return true;
        }

        private static Node removeNode(Node node, int value) {
            if (node == null) {
                return null;
            }
            if (value < node.value) {
                node.left = removeNode(node.left, value);
            } else if (value > node.value) {
                node.right = removeNode(node.right, value);
            } else {
                if (node.left == null) {
                    return node.right;
                }
                if (node.right == null) {
                    return node.left;
                }
                Node successor = node.right;
                while (successor.left != null) {
                    successor = successor.left;
                }
                node.value = successor.value;
                node.right = removeNode(node.right, successor.value);
            }
            return node;
        }
    }

    /** Prefix trie. */
    public static final class Trie {
        private static final class Node {
            final java.util.HashMap<Character, Node> children = new java.util.HashMap<>();
            boolean terminal;
        }

        private final Node root = new Node();
        private int count;

        public void insert(String word) {
            Node node = root;
            for (int i = 0; i < word.length(); i++) {
                char ch = word.charAt(i);
                Node child = node.children.get(ch);
                if (child == null) {
                    child = new Node();
                    node.children.put(ch, child);
                }
                node = child;
            }
            if (!node.terminal) {
                node.terminal = true;
                count++;
            }
        }

        public boolean search(String word) {
            Node node = root;
            for (int i = 0; i < word.length(); i++) {
                Node child = node.children.get(word.charAt(i));
                if (child == null) {
                    return false;
                }
                node = child;
            }
            return node.terminal;
        }

        public boolean startsWith(String prefix) {
            Node node = root;
            for (int i = 0; i < prefix.length(); i++) {
                Node child = node.children.get(prefix.charAt(i));
                if (child == null) {
                    return false;
                }
                node = child;
            }
            return true;
        }

        public int size() {
            return count;
        }
    }

    /** Binary min-heap. */
    public static final class MinHeap {
        private final List<Integer> items = new ArrayList<>();

        public void push(int value) {
            items.add(value);
            siftUp(items.size() - 1);
        }

        public int pop() {
            if (items.isEmpty()) {
                return -1;
            }
            int top = items.get(0);
            int last = items.remove(items.size() - 1);
            if (!items.isEmpty()) {
                items.set(0, last);
                siftDown(0);
            }
            return top;
        }

        public int peek() {
            return items.isEmpty() ? -1 : items.get(0);
        }

        public boolean isEmpty() {
            return items.isEmpty();
        }

        public int size() {
            return items.size();
        }

        private void siftUp(int index) {
            while (index > 0) {
                int parent = (index - 1) / 2;
                if (items.get(parent) <= items.get(index)) {
                    return;
                }
                swap(parent, index);
                index = parent;
            }
        }

        private void siftDown(int index) {
            int size = items.size();
            while (true) {
                int left = 2 * index + 1;
                int right = left + 1;
                int smallest = index;
                if (left < size && items.get(left) < items.get(smallest)) {
                    smallest = left;
                }
                if (right < size && items.get(right) < items.get(smallest)) {
                    smallest = right;
                }
                if (smallest == index) {
                    return;
                }
                swap(index, smallest);
                index = smallest;
            }
        }

        private void swap(int i, int j) {
            int tmp = items.get(i);
            items.set(i, items.get(j));
            items.set(j, tmp);
        }
    }
}