//! Classic data structures (mirrors the Java/C++/Python tiers).

use std::collections::{HashMap, VecDeque};

use crate::solutions::SENTINEL;

// --- stack ---

#[derive(Default)]
pub struct Stack {
    items: Vec<i32>,
}

impl Stack {
    pub fn push(&mut self, value: i32) {
        self.items.push(value);
    }

    pub fn pop(&mut self) -> i32 {
        self.items.pop().unwrap_or(SENTINEL)
    }

    pub fn peek(&self) -> i32 {
        self.items.last().copied().unwrap_or(SENTINEL)
    }

    pub fn is_empty(&self) -> bool {
        self.items.is_empty()
    }

    pub fn size(&self) -> usize {
        self.items.len()
    }
}

// --- queue ---

#[derive(Default)]
pub struct Queue {
    items: VecDeque<i32>,
}

impl Queue {
    pub fn enqueue(&mut self, value: i32) {
        self.items.push_back(value);
    }

    pub fn dequeue(&mut self) -> i32 {
        self.items.pop_front().unwrap_or(SENTINEL)
    }

    pub fn peek(&self) -> i32 {
        self.items.front().copied().unwrap_or(SENTINEL)
    }

    pub fn is_empty(&self) -> bool {
        self.items.is_empty()
    }

    pub fn size(&self) -> usize {
        self.items.len()
    }
}

// --- singly linked list ---

#[derive(Default)]
pub struct LinkedList {
    head: Option<Box<Node>>,
    size: usize,
}

struct Node {
    value: i32,
    next: Option<Box<Node>>,
}

impl LinkedList {
    pub fn append(&mut self, value: i32) {
        let mut slot = &mut self.head;
        while let Some(node) = slot {
            slot = &mut node.next;
        }
        *slot = Some(Box::new(Node { value, next: None }));
        self.size += 1;
    }

    pub fn prepend(&mut self, value: i32) {
        let head = self.head.take();
        self.head = Some(Box::new(Node { value, next: head }));
        self.size += 1;
    }

    pub fn get(&self, index: usize) -> i32 {
        let mut node = self.head.as_deref();
        for _ in 0..index {
            node = match node {
                Some(current) => current.next.as_deref(),
                None => return SENTINEL,
            };
        }
        node.map(|current| current.value).unwrap_or(SENTINEL)
    }

    pub fn contains(&self, value: i32) -> bool {
        let mut node = self.head.as_deref();
        while let Some(current) = node {
            if current.value == value {
                return true;
            }
            node = current.next.as_deref();
        }
        false
    }

    pub fn remove(&mut self, value: i32) -> bool {
        let mut current = &mut self.head;
        loop {
            if current.is_none() {
                return false;
            }
            if current.as_ref().unwrap().value == value {
                let next = current.as_mut().unwrap().next.take();
                *current = next;
                self.size -= 1;
                return true;
            }
            current = &mut current.as_mut().unwrap().next;
        }
    }

    pub fn size(&self) -> usize {
        self.size
    }

    pub fn to_list(&self) -> Vec<i32> {
        let mut values = Vec::with_capacity(self.size);
        let mut node = self.head.as_deref();
        while let Some(current) = node {
            values.push(current.value);
            node = current.next.as_deref();
        }
        values
    }
}

// --- binary search tree ---

#[derive(Default)]
pub struct BST {
    root: Option<Box<TreeNode>>,
    size: usize,
}

struct TreeNode {
    value: i32,
    left: Option<Box<TreeNode>>,
    right: Option<Box<TreeNode>>,
}

impl BST {
    pub fn insert(&mut self, value: i32) {
        let mut slot = &mut self.root;
        while let Some(node) = slot {
            if value < node.value {
                slot = &mut node.left;
            } else if value > node.value {
                slot = &mut node.right;
            } else {
                return;
            }
        }
        *slot = Some(Box::new(TreeNode {
            value,
            left: None,
            right: None,
        }));
        self.size += 1;
    }

    pub fn contains(&self, value: i32) -> bool {
        let mut node = self.root.as_deref();
        while let Some(current) = node {
            if value == current.value {
                return true;
            }
            node = if value < current.value {
                current.left.as_deref()
            } else {
                current.right.as_deref()
            };
        }
        false
    }

    pub fn min(&self) -> i32 {
        let mut node = self.root.as_deref();
        while let Some(current) = node {
            if current.left.is_none() {
                return current.value;
            }
            node = current.left.as_deref();
        }
        SENTINEL
    }

    pub fn max(&self) -> i32 {
        let mut node = self.root.as_deref();
        while let Some(current) = node {
            if current.right.is_none() {
                return current.value;
            }
            node = current.right.as_deref();
        }
        SENTINEL
    }

    pub fn height(&self) -> i32 {
        fn height_of(node: Option<&Box<TreeNode>>) -> i32 {
            match node {
                None => SENTINEL,
                Some(current) => {
                    1 + height_of(current.left.as_ref()).max(height_of(current.right.as_ref()))
                }
            }
        }
        height_of(self.root.as_ref())
    }

    pub fn size(&self) -> usize {
        self.size
    }

    pub fn in_order(&self) -> Vec<i32> {
        fn collect(node: Option<&Box<TreeNode>>, out: &mut Vec<i32>) {
            if let Some(current) = node {
                collect(current.left.as_ref(), out);
                out.push(current.value);
                collect(current.right.as_ref(), out);
            }
        }
        let mut values = Vec::with_capacity(self.size);
        collect(self.root.as_ref(), &mut values);
        values
    }

    pub fn remove(&mut self, value: i32) -> bool {
        if !self.contains(value) {
            return false;
        }
        Self::remove_node(&mut self.root, value);
        self.size -= 1;
        true
    }

    fn remove_node(node: &mut Option<Box<TreeNode>>, value: i32) {
        let Some(current) = node.as_mut() else {
            return;
        };
        if value < current.value {
            Self::remove_node(&mut current.left, value);
        } else if value > current.value {
            Self::remove_node(&mut current.right, value);
        } else if current.left.is_none() {
            *node = current.right.take();
        } else if current.right.is_none() {
            *node = current.left.take();
        } else {
            let mut successor = current.right.as_mut().unwrap();
            while successor.left.is_some() {
                successor = successor.left.as_mut().unwrap();
            }
            current.value = successor.value;
            Self::remove_node(&mut current.right, current.value);
        }
    }
}

// --- trie ---

#[derive(Default)]
pub struct Trie {
    root: TrieNode,
    size: usize,
}

#[derive(Default)]
struct TrieNode {
    children: HashMap<char, TrieNode>,
    terminal: bool,
}

impl Trie {
    pub fn insert(&mut self, word: &str) {
        let mut node = &mut self.root;
        for ch in word.chars() {
            node = node.children.entry(ch).or_default();
        }
        if !node.terminal {
            node.terminal = true;
            self.size += 1;
        }
    }

    pub fn search(&self, word: &str) -> bool {
        match self.find(word) {
            Some(node) => node.terminal,
            None => false,
        }
    }

    pub fn starts_with(&self, prefix: &str) -> bool {
        self.find(prefix).is_some()
    }

    fn find(&self, word: &str) -> Option<&TrieNode> {
        let mut node = &self.root;
        for ch in word.chars() {
            node = node.children.get(&ch)?;
        }
        Some(node)
    }

    pub fn size(&self) -> usize {
        self.size
    }
}

// --- min-heap ---

#[derive(Default)]
pub struct MinHeap {
    items: Vec<i32>,
}

impl MinHeap {
    pub fn push(&mut self, value: i32) {
        self.items.push(value);
        let mut index = self.items.len() - 1;
        while index > 0 {
            let parent = (index - 1) / 2;
            if self.items[parent] <= self.items[index] {
                return;
            }
            self.items.swap(parent, index);
            index = parent;
        }
    }

    pub fn pop(&mut self) -> i32 {
        if self.items.is_empty() {
            return SENTINEL;
        }
        let top = self.items[0];
        let last = self.items.pop().unwrap();
        if !self.items.is_empty() {
            self.items[0] = last;
            let mut index = 0usize;
            loop {
                let left = 2 * index + 1;
                let right = left + 1;
                let mut smallest = index;
                if left < self.items.len() && self.items[left] < self.items[smallest] {
                    smallest = left;
                }
                if right < self.items.len() && self.items[right] < self.items[smallest] {
                    smallest = right;
                }
                if smallest == index {
                    return top;
                }
                self.items.swap(index, smallest);
                index = smallest;
            }
        }
        top
    }

    pub fn peek(&self) -> i32 {
        self.items.first().copied().unwrap_or(SENTINEL)
    }

    pub fn is_empty(&self) -> bool {
        self.items.is_empty()
    }

    pub fn size(&self) -> usize {
        self.items.len()
    }
}