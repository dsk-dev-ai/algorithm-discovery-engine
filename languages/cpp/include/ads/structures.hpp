#pragma once

#include <deque>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

namespace ads {

constexpr int kSentinel = -1;

// --- stack --------------------------------------------------------------------

class Stack {
public:
    void push(int value) { items_.push_back(value); }

    int pop() {
        if (items_.empty()) {
            return kSentinel;
        }
        int value = items_.back();
        items_.pop_back();
        return value;
    }

    int peek() const { return items_.empty() ? kSentinel : items_.back(); }

    bool is_empty() const { return items_.empty(); }

    int size() const { return static_cast<int>(items_.size()); }

private:
    std::vector<int> items_;
};

// --- queue --------------------------------------------------------------------

class Queue {
public:
    void enqueue(int value) { items_.push_back(value); }

    int dequeue() {
        if (items_.empty()) {
            return kSentinel;
        }
        int value = items_.front();
        items_.pop_front();
        return value;
    }

    int peek() const { return items_.empty() ? kSentinel : items_.front(); }

    bool is_empty() const { return items_.empty(); }

    int size() const { return static_cast<int>(items_.size()); }

private:
    std::deque<int> items_;
};

// --- singly linked list ---------------------------------------------------------

class LinkedList {
public:
    void append(int value) {
        Node* node = new Node{value, nullptr};
        if (tail_ == nullptr) {
            head_ = tail_ = node;
        } else {
            tail_->next = node;
            tail_ = node;
        }
        ++size_;
    }

    void prepend(int value) {
        Node* node = new Node{value, head_};
        head_ = node;
        if (tail_ == nullptr) {
            tail_ = node;
        }
        ++size_;
    }

    int get(int index) const {
        if (index < 0 || index >= size_) {
            return kSentinel;
        }
        const Node* node = head_;
        for (int i = 0; i < index; ++i) {
            node = node->next;
        }
        return node->value;
    }

    bool contains(int value) const {
        for (const Node* node = head_; node != nullptr; node = node->next) {
            if (node->value == value) {
                return true;
            }
        }
        return false;
    }

    bool remove(int value) {
        Node* previous = nullptr;
        for (Node* node = head_; node != nullptr; node = node->next) {
            if (node->value == value) {
                if (previous == nullptr) {
                    head_ = node->next;
                } else {
                    previous->next = node->next;
                }
                if (node == tail_) {
                    tail_ = previous;
                }
                delete node;
                --size_;
                return true;
            }
            previous = node;
        }
        return false;
    }

    int size() const { return size_; }

    std::vector<int> to_list() const {
        std::vector<int> out;
        for (const Node* node = head_; node != nullptr; node = node->next) {
            out.push_back(node->value);
        }
        return out;
    }

    ~LinkedList() {
        Node* node = head_;
        while (node != nullptr) {
            Node* next = node->next;
            delete node;
            node = next;
        }
    }

    LinkedList() = default;
    LinkedList(const LinkedList&) = delete;
    LinkedList& operator=(const LinkedList&) = delete;

private:
    struct Node {
        int value;
        Node* next;
    };
    Node* head_ = nullptr;
    Node* tail_ = nullptr;
    int size_ = 0;
};

// --- binary search tree ---------------------------------------------------------

class BST {
public:
    ~BST() { clear(root_); }

    void insert(int value) {
        Node** slot = &root_;
        while (*slot != nullptr) {
            if (value < (*slot)->value) {
                slot = &(*slot)->left;
            } else if (value > (*slot)->value) {
                slot = &(*slot)->right;
            } else {
                return;
            }
        }
        *slot = new Node{value, nullptr, nullptr};
        ++size_;
    }

    bool contains(int value) const {
        const Node* node = root_;
        while (node != nullptr) {
            if (value == node->value) {
                return true;
            }
            node = value < node->value ? node->left : node->right;
        }
        return false;
    }

    int min() const {
        const Node* node = root_;
        if (node == nullptr) {
            return kSentinel;
        }
        while (node->left != nullptr) {
            node = node->left;
        }
        return node->value;
    }

    int max() const {
        const Node* node = root_;
        if (node == nullptr) {
            return kSentinel;
        }
        while (node->right != nullptr) {
            node = node->right;
        }
        return node->value;
    }

    int height() const { return height_of(root_); }

    int size() const { return size_; }

    std::vector<int> in_order() const {
        std::vector<int> out;
        in_order_of(root_, out);
        return out;
    }

    bool remove(int value) {
        if (!contains(value)) {
            return false;
        }
        remove_node(root_, value);
        --size_;
        return true;
    }

    BST() = default;
    BST(const BST&) = delete;
    BST& operator=(const BST&) = delete;

private:
    struct Node {
        int value;
        Node* left;
        Node* right;
    };

    static int height_of(const Node* node) {
        if (node == nullptr) {
            return -1;
        }
        return 1 + std::max(height_of(node->left), height_of(node->right));
    }

    static void in_order_of(const Node* node, std::vector<int>& out) {
        if (node == nullptr) {
            return;
        }
        in_order_of(node->left, out);
        out.push_back(node->value);
        in_order_of(node->right, out);
    }

    static Node* remove_node(Node* node, int value) {
        if (node == nullptr) {
            return nullptr;
        }
        if (value < node->value) {
            node->left = remove_node(node->left, value);
        } else if (value > node->value) {
            node->right = remove_node(node->right, value);
        } else {
            if (node->left == nullptr) {
                Node* right = node->right;
                delete node;
                return right;
            }
            if (node->right == nullptr) {
                Node* left = node->left;
                delete node;
                return left;
            }
            Node* successor = node->right;
            while (successor->left != nullptr) {
                successor = successor->left;
            }
            node->value = successor->value;
            node->right = remove_node(node->right, successor->value);
        }
        return node;
    }

    static void clear(Node* node) {
        if (node == nullptr) {
            return;
        }
        clear(node->left);
        clear(node->right);
        delete node;
    }

    Node* root_ = nullptr;
    int size_ = 0;
};

// --- trie -----------------------------------------------------------------------

class Trie {
public:
    void insert(const std::string& word) {
        Node* node = &root_;
        for (char ch : word) {
            auto [it, inserted] = node->children.try_emplace(ch);
            node = &it->second;
            (void)inserted;
        }
        if (!node->terminal) {
            node->terminal = true;
            ++size_;
        }
    }

    bool search(const std::string& word) const {
        const Node* node = &root_;
        for (char ch : word) {
            auto it = node->children.find(ch);
            if (it == node->children.end()) {
                return false;
            }
            node = &it->second;
        }
        return node->terminal;
    }

    bool starts_with(const std::string& prefix) const {
        const Node* node = &root_;
        for (char ch : prefix) {
            auto it = node->children.find(ch);
            if (it == node->children.end()) {
                return false;
            }
            node = &it->second;
        }
        return true;
    }

    int size() const { return size_; }

private:
    struct Node {
        std::unordered_map<char, Node> children;
        bool terminal = false;
    };

    Node root_;
    int size_ = 0;
};

// --- min-heap -------------------------------------------------------------------

class MinHeap {
public:
    void push(int value) {
        items_.push_back(value);
        sift_up(items_.size() - 1);
    }

    int pop() {
        if (items_.empty()) {
            return kSentinel;
        }
        int top = items_.front();
        int last = items_.back();
        items_.pop_back();
        if (!items_.empty()) {
            items_[0] = last;
            sift_down(0);
        }
        return top;
    }

    int peek() const { return items_.empty() ? kSentinel : items_.front(); }

    bool is_empty() const { return items_.empty(); }

    int size() const { return static_cast<int>(items_.size()); }

private:
    void sift_up(std::size_t index) {
        while (index > 0) {
            std::size_t parent = (index - 1) / 2;
            if (items_[parent] <= items_[index]) {
                return;
            }
            std::swap(items_[parent], items_[index]);
            index = parent;
        }
    }

    void sift_down(std::size_t index) {
        std::size_t size = items_.size();
        while (true) {
            std::size_t left = 2 * index + 1;
            std::size_t right = left + 1;
            std::size_t smallest = index;
            if (left < size && items_[left] < items_[smallest]) {
                smallest = left;
            }
            if (right < size && items_[right] < items_[smallest]) {
                smallest = right;
            }
            if (smallest == index) {
                return;
            }
            std::swap(items_[index], items_[smallest]);
            index = smallest;
        }
    }

    std::vector<int> items_;
};

}  // namespace ads