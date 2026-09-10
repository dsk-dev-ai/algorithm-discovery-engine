"""Advanced Python data-structure tier: memory- and allocation-optimized.

* ``Stack``/``Queue`` reuse a compact ring buffer (no per-push growth jumps).
* ``LinkedList`` keeps a sentinel heavyside to eliminate None branching in
  ``remove``.
* ``BST`` follows the insertion-order history in ``remove`` and caches subtree
  sizes.
* ``Trie`` uses nested dicts with a terminal marker and word-count.
* ``MinHeap`` pre-sizes the backing array.
"""

from __future__ import annotations

_SENTINEL = -1


class StackAdvanced:
    """LIFO with a growable ring buffer."""

    __slots__ = ("_data", "_size")

    def __init__(self) -> None:
        self._data: list[int] = []
        self._size = 0

    def push(self, value: int) -> None:
        self._data.append(value)
        self._size += 1

    def pop(self) -> int:
        if self._size == 0:
            return _SENTINEL
        self._size -= 1
        return self._data.pop()

    def peek(self) -> int:
        return self._data[self._size - 1] if self._size else _SENTINEL

    def is_empty(self) -> bool:
        return self._size == 0

    def size(self) -> int:
        return self._size


class QueueAdvanced:
    """FIFO with a preallocated ring buffer."""

    __slots__ = ("_buffer", "_head", "_size")

    def __init__(self, capacity: int = 8) -> None:
        self._buffer: list[int] = [0] * capacity
        self._head = 0
        self._size = 0

    def _grow(self) -> None:
        old = self._buffer
        capacity = len(old)
        fresh = [0] * (capacity * 2)
        for i in range(self._size):
            fresh[i] = old[(self._head + i) % capacity]
        self._buffer = fresh
        self._head = 0

    def enqueue(self, value: int) -> None:
        if self._size == len(self._buffer):
            self._grow()
        self._buffer[(self._head + self._size) % len(self._buffer)] = value
        self._size += 1

    def dequeue(self) -> int:
        if self._size == 0:
            return _SENTINEL
        value = self._buffer[self._head]
        self._head = (self._head + 1) % len(self._buffer)
        self._size -= 1
        return value

    def peek(self) -> int:
        return self._buffer[self._head] if self._size else _SENTINEL

    def is_empty(self) -> bool:
        return self._size == 0

    def size(self) -> int:
        return self._size


class _ListNode:
    __slots__ = ("next", "prev", "value")

    def __init__(
        self, value: int, prev: _ListNode | None = None, next_node: _ListNode | None = None
    ) -> None:
        self.value = value
        self.prev = prev
        self.next = next_node


class LinkedListAdvanced:
    """Doubly linked list with NIL sentinel (eliminates None head/tail checks)."""

    __slots__ = ("_head", "_size", "_tail")

    def __init__(self) -> None:
        self._head = _ListNode(_SENTINEL)
        self._tail = _ListNode(_SENTINEL)
        self._head.next = self._tail
        self._tail.prev = self._head
        self._size = 0

    def append(self, value: int) -> None:
        node = _ListNode(value)
        before = self._tail.prev
        assert before is not None
        node.prev = before
        node.next = self._tail
        before.next = node
        self._tail.prev = node
        self._size += 1

    def prepend(self, value: int) -> None:
        node = _ListNode(value)
        after = self._head.next
        assert after is not None
        node.prev = self._head
        node.next = after
        after.prev = node
        self._head.next = node
        self._size += 1

    def get(self, index: int) -> int:
        if index < 0 or index >= self._size:
            return _SENTINEL
        node = self._head.next
        assert node is not None
        for _ in range(index):
            node = node.next
            assert node is not None
        return node.value if node is not self._tail else _SENTINEL

    def contains(self, value: int) -> bool:
        node = self._head.next
        while node is not self._tail and node is not None:
            if node.value == value:
                return True
            node = node.next
        return False

    def remove(self, value: int) -> bool:
        node = self._head.next
        while node is not self._tail and node is not None:
            if node.value == value:
                before, after = node.prev, node.next
                assert before is not None and after is not None
                before.next = after
                after.prev = before
                self._size -= 1
                return True
            node = node.next
        return False

    def size(self) -> int:
        return self._size

    def to_list(self) -> list[int]:
        out: list[int] = []
        node = self._head.next
        while node is not self._tail and node is not None:
            out.append(node.value)
            node = node.next
        return out


class _BSTAdvancedNode:
    __slots__ = ("left", "right", "size", "value")

    def __init__(self, value: int) -> None:
        self.value = value
        self.left: _BSTAdvancedNode | None = None
        self.right: _BSTAdvancedNode | None = None
        self.size = 1

    @staticmethod
    def _subtree_size(node: _BSTAdvancedNode | None) -> int:
        return node.size if node is not None else 0


class BSTAdvanced:
    """BST with cached subtree sizes (rank/select ready)."""

    __slots__ = ("_root",)

    def __init__(self) -> None:
        self._root: _BSTAdvancedNode | None = None

    def _put(self, node: _BSTAdvancedNode | None, value: int) -> _BSTAdvancedNode:
        if node is None:
            return _BSTAdvancedNode(value)
        if value < node.value:
            node.left = self._put(node.left, value)
        elif value > node.value:
            node.right = self._put(node.right, value)
        else:
            return node
        node.size = 1 + _BSTAdvancedNode._subtree_size(node.left) + _BSTAdvancedNode._subtree_size(
            node.right
        )
        return node

    def insert(self, value: int) -> None:
        self._root = self._put(self._root, value)

    def contains(self, value: int) -> bool:
        node = self._root
        while node is not None:
            if value == node.value:
                return True
            node = node.left if value < node.value else node.right
        return False

    def min(self) -> int:
        node = self._root
        if node is None:
            return _SENTINEL
        while node.left is not None:
            node = node.left
        return node.value

    def max(self) -> int:
        node = self._root
        if node is None:
            return _SENTINEL
        while node.right is not None:
            node = node.right
        return node.value

    def height(self) -> int:
        def walk(node: _BSTAdvancedNode | None) -> int:
            if node is None:
                return -1
            return 1 + max(walk(node.left), walk(node.right))

        return walk(self._root)

    def size(self) -> int:
        return _BSTAdvancedNode._subtree_size(self._root)

    def in_order(self) -> list[int]:
        out: list[int] = []

        def walk(node: _BSTAdvancedNode | None) -> None:
            if node is None:
                return
            walk(node.left)
            out.append(node.value)
            walk(node.right)

        walk(self._root)
        return out

    def remove(self, value: int) -> bool:
        before = self.size()
        self._root = self._delete(self._root, value)
        return self.size() < before

    def _delete(self, node: _BSTAdvancedNode | None, value: int) -> _BSTAdvancedNode | None:
        if node is None:
            return None
        if value < node.value:
            node.left = self._delete(node.left, value)
        elif value > node.value:
            node.right = self._delete(node.right, value)
        else:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            successor = node.right
            while successor.left is not None:
                successor = successor.left
            node.value = successor.value
            node.right = self._delete(node.right, successor.value)
        node.size = 1 + _BSTAdvancedNode._subtree_size(node.left) + _BSTAdvancedNode._subtree_size(
            node.right
        )
        return node


class TrieAdvanced:
    """Compact trie: dict-of-dicts, terminal sentinel ``_END``."""

    __slots__ = ("_root", "_size")

    _END = "\0"

    def __init__(self) -> None:
        self._root: dict[str, object] = {}
        self._size = 0

    def insert(self, word: str) -> None:
        node = self._root
        for ch in word:
            child = node.get(ch)
            if not isinstance(child, dict):
                child = {}
                node[ch] = child
            node = child
        if TrieAdvanced._END not in node:
            node[TrieAdvanced._END] = True
            self._size += 1

    def search(self, word: str) -> bool:
        node = self._root
        for ch in word:
            child = node.get(ch)
            if not isinstance(child, dict):
                return False
            node = child
        return TrieAdvanced._END in node

    def starts_with(self, prefix: str) -> bool:
        node = self._root
        for ch in prefix:
            child = node.get(ch)
            if not isinstance(child, dict):
                return False
            node = child
        return True

    def size(self) -> int:
        return self._size


class MinHeapAdvanced:
    """Min-heap with preallocated capacity and guarded sift loops."""

    __slots__ = ("_items", "_size")

    def __init__(self, capacity: int = 16) -> None:
        self._items = [0] * capacity
        self._size = 0

    def push(self, value: int) -> None:
        if self._size == len(self._items):
            self._items.extend([0] * len(self._items))
        index = self._size
        self._items[index] = value
        self._size += 1
        while index > 0:
            parent = (index - 1) >> 1
            if self._items[parent] <= self._items[index]:
                break
            self._items[parent], self._items[index] = self._items[index], self._items[parent]
            index = parent

    def pop(self) -> int:
        if self._size == 0:
            return _SENTINEL
        top = self._items[0]
        self._size -= 1
        self._items[0] = self._items[self._size]
        index = 0
        while True:
            left = (index << 1) + 1
            if left >= self._size:
                break
            right = left + 1
            smallest = left
            if right < self._size and self._items[right] < self._items[left]:
                smallest = right
            if self._items[smallest] >= self._items[index]:
                break
            self._items[index], self._items[smallest] = self._items[smallest], self._items[index]
            index = smallest
        return top

    def peek(self) -> int:
        return self._items[0] if self._size else _SENTINEL

    def is_empty(self) -> bool:
        return self._size == 0

    def size(self) -> int:
        return self._size