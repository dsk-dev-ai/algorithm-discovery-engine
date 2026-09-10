"""Regular Python data-structure tier: simple, readable implementations.

Mirror the Java / C++ / Rust ports. Each structure exposes the operation
contracts listed in ``catalog/problems.json``.
"""

from __future__ import annotations

from collections import deque as _deque

_SENTINEL = -1


class Stack:
    """LIFO stack backed by a list."""

    __slots__ = ("_items",)

    def __init__(self) -> None:
        self._items: list[int] = []

    def push(self, value: int) -> None:
        self._items.append(value)

    def pop(self) -> int:
        return self._items.pop() if self._items else _SENTINEL

    def peek(self) -> int:
        return self._items[-1] if self._items else _SENTINEL

    def is_empty(self) -> bool:
        return not self._items

    def size(self) -> int:
        return len(self._items)


class Queue:
    """FIFO queue backed by a deque."""

    __slots__ = ("_items",)

    def __init__(self) -> None:
        self._items: _deque[int] = _deque()

    def enqueue(self, value: int) -> None:
        self._items.append(value)

    def dequeue(self) -> int:
        return self._items.popleft() if self._items else _SENTINEL

    def peek(self) -> int:
        return self._items[0] if self._items else _SENTINEL

    def is_empty(self) -> bool:
        return not self._items

    def size(self) -> int:
        return len(self._items)


class _Node:
    __slots__ = ("next", "value")

    def __init__(self, value: int) -> None:
        self.value = value
        self.next: _Node | None = None


class LinkedList:
    """Singly linked list."""

    __slots__ = ("_head", "_size", "_tail")

    def __init__(self) -> None:
        self._head: _Node | None = None
        self._tail: _Node | None = None
        self._size = 0

    def append(self, value: int) -> None:
        node = _Node(value)
        if self._tail is None:
            self._head = self._tail = node
        else:
            self._tail.next = node
            self._tail = node
        self._size += 1

    def prepend(self, value: int) -> None:
        node = _Node(value)
        node.next = self._head
        self._head = node
        if self._tail is None:
            self._tail = node
        self._size += 1

    def get(self, index: int) -> int:
        if index < 0 or index >= self._size:
            return _SENTINEL
        node = self._head
        for _ in range(index):
            node = node.next  # type: ignore[union-attr]
        return node.value  # type: ignore[union-attr]

    def contains(self, value: int) -> bool:
        node = self._head
        while node is not None:
            if node.value == value:
                return True
            node = node.next
        return False

    def remove(self, value: int) -> bool:
        node, previous = self._head, None
        while node is not None:
            if node.value == value:
                if previous is None:
                    self._head = node.next
                else:
                    previous.next = node.next
                if node is self._tail:
                    self._tail = previous
                self._size -= 1
                return True
            previous, node = node, node.next
        return False

    def size(self) -> int:
        return self._size

    def to_list(self) -> list[int]:
        out: list[int] = []
        node = self._head
        while node is not None:
            out.append(node.value)
            node = node.next
        return out


class BST:
    """Binary search tree."""

    __slots__ = ("_root", "_size")

    def __init__(self) -> None:
        self._root: _BSTNode | None = None
        self._size = 0

    def insert(self, value: int) -> None:
        if self._root is None:
            self._root = _BSTNode(value)
            self._size = 1
            return
        node = self._root
        while True:
            if value < node.value:
                if node.left is None:
                    node.left = _BSTNode(value)
                    break
                node = node.left
            elif value > node.value:
                if node.right is None:
                    node.right = _BSTNode(value)
                    break
                node = node.right
            else:
                return
        self._size += 1

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
        return _height(self._root)

    def size(self) -> int:
        return self._size

    def in_order(self) -> list[int]:
        out: list[int] = []
        _in_order(self._root, out)
        return out

    def remove(self, value: int) -> bool:
        found = self._contains(self._root, value)
        if not found:
            return False
        self._root = _remove(self._root, value)
        self._size -= 1
        return True

    @staticmethod
    def _contains(node: _BSTNode | None, value: int) -> bool:
        if node is None:
            return False
        if value == node.value:
            return True
        return BST._contains(node.left if value < node.value else node.right, value)


class _BSTNode:
    __slots__ = ("left", "right", "value")

    def __init__(self, value: int) -> None:
        self.value = value
        self.left: _BSTNode | None = None
        self.right: _BSTNode | None = None


def _height(node: _BSTNode | None) -> int:
    if node is None:
        return -1
    return 1 + max(_height(node.left), _height(node.right))


def _in_order(node: _BSTNode | None, out: list[int]) -> None:
    if node is None:
        return
    _in_order(node.left, out)
    out.append(node.value)
    _in_order(node.right, out)


def _remove(node: _BSTNode | None, value: int) -> _BSTNode | None:
    if node is None:
        return None
    if value < node.value:
        node.left = _remove(node.left, value)
    elif value > node.value:
        node.right = _remove(node.right, value)
    else:
        if node.left is None:
            return node.right
        if node.right is None:
            return node.left
        successor = node.right
        while successor.left is not None:
            successor = successor.left
        node.value = successor.value
        node.right = _remove(node.right, successor.value)
    return node


class Trie:
    """Prefix trie storing unique words."""

    __slots__ = ("_root", "_size")

    def __init__(self) -> None:
        self._root: _TrieNode = _TrieNode()
        self._size = 0

    def insert(self, word: str) -> None:
        node = self._root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = _TrieNode()
            node = node.children[ch]
        if not node.terminal:
            node.terminal = True
            self._size += 1

    def search(self, word: str) -> bool:
        node = self._root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.terminal

    def starts_with(self, prefix: str) -> bool:
        node = self._root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True

    def size(self) -> int:
        return self._size


class _TrieNode:
    __slots__ = ("children", "terminal")

    def __init__(self) -> None:
        self.children: dict[str, _TrieNode] = {}
        self.terminal = False


class MinHeap:
    """Binary min-heap over a list."""

    __slots__ = ("_items",)

    def __init__(self) -> None:
        self._items: list[int] = []

    def push(self, value: int) -> None:
        self._items.append(value)
        self._sift_up(len(self._items) - 1)

    def pop(self) -> int:
        if not self._items:
            return _SENTINEL
        top = self._items[0]
        last = self._items.pop()
        if self._items:
            self._items[0] = last
            self._sift_down(0)
        return top

    def peek(self) -> int:
        return self._items[0] if self._items else _SENTINEL

    def is_empty(self) -> bool:
        return not self._items

    def size(self) -> int:
        return len(self._items)

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent = (index - 1) // 2
            if self._items[parent] <= self._items[index]:
                return
            self._items[parent], self._items[index] = (
                self._items[index],
                self._items[parent],
            )
            index = parent

    def _sift_down(self, index: int) -> None:
        size = len(self._items)
        while True:
            left = 2 * index + 1
            right = left + 1
            smallest = index
            if left < size and self._items[left] < self._items[smallest]:
                smallest = left
            if right < size and self._items[right] < self._items[smallest]:
                smallest = right
            if smallest == index:
                return
            self._items[index], self._items[smallest] = (
                self._items[smallest],
                self._items[index],
            )
            index = smallest