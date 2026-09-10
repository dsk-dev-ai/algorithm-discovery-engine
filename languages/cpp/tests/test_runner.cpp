// Cross-language catalog test runner (C++17).
// Reads generated test vectors, runs each through ads::solutions / ads::structures.

#include <cstdlib>
#include <iostream>
#include <set>
#include <sstream>
#include <string>
#include <vector>

#include "generated_test_data.hpp"
#include "ads/solutions.hpp"
#include "ads/structures.hpp"

namespace {

int failures = 0;
int passed = 0;

void report_fail(const std::string& label, const std::string& input,
                 const std::string& got, const std::string& expected) {
    ++failures;
    std::cerr << "FAIL " << label << " input=" << input << " -> got " << got
              << ", expected " << expected << '\n';
}

std::vector<int> parse_ints(const std::string& token) {
    std::vector<int> out;
    std::istringstream stream(token);
    int value = 0;
    while (stream >> value) {
        out.push_back(value);
    }
    return out;
}

std::vector<std::string> split(const std::string& text, char delimiter) {
    std::vector<std::string> parts;
    std::string current;
    std::istringstream stream(text);
    while (std::getline(stream, current, delimiter)) {
        parts.push_back(current);
    }
    return parts;
}

std::vector<std::vector<int>> parse_graph(const std::string& encoded) {
    std::vector<std::vector<int>> graph;
    if (encoded.empty()) {
        return graph;
    }
    for (const std::string& row : split(encoded, ';')) {
        auto pair = split(row, ':');
        if (pair.empty()) {
            continue;
        }
        graph.push_back(pair.size() > 1 ? parse_ints(pair[1])
                                        : std::vector<int>{});
    }
    return graph;
}

void check_int(const std::string& id, const std::string& input, int got,
               int expectedish) {
    if (got != expectedish) {
        report_fail(id, input, std::to_string(got), std::to_string(expectedish));
    } else {
        ++passed;
    }
}

void check_int_vector(const std::string& id, const std::string& input,
                      const std::vector<int>& got,
                      const std::vector<int>& expected) {
    if (got != expected) {
        std::ostringstream a;
        std::ostringstream b;
        for (size_t i = 0; i < got.size(); ++i) {
            if (i > 0) a << ' ';
            a << got[i];
        }
        for (size_t i = 0; i < expected.size(); ++i) {
            if (i > 0) b << ' ';
            b << expected[i];
        }
        report_fail(id, input, a.str(), b.str());
    } else {
        ++passed;
    }
}

void check_algorithms() {
    const auto& data = ads::gen::ALGORITHMS;
    const std::vector<std::string> ids = {
        "two_sum",       "binary_search", "merge_sort",     "quick_sort",
        "max_subarray",  "lcs",           "knapsack_01",    "edit_distance",
        "graph_bfs",     "graph_dfs",
    };
    for (size_t p = 0; p < ids.size(); ++p) {
        for (const auto& testcase : data[p]) {
            const std::string& input = testcase[0];
            const std::string& expected = testcase[1];
            auto parts = split(input, '|');
            const std::string& id = ids[p];
            if (id == "two_sum") {
                auto nums = parse_ints(parts[0]);
                int target = std::atoi(parts[1].c_str());
                check_int_vector(id, input, ads::two_sum(nums, target),
                                 parse_ints(expected));
            } else if (id == "binary_search") {
                int got = ads::binary_search(parse_ints(parts[0]),
                                             std::atoi(parts[1].c_str()));
                check_int(id, input, got, std::atoi(expected.c_str()));
            } else if (id == "merge_sort" || id == "quick_sort") {
                auto nums = parse_ints(input);
                auto got = id == "merge_sort" ? ads::merge_sort(nums)
                                              : ads::quick_sort(nums);
                check_int_vector(id, input, got, parse_ints(expected));
            } else if (id == "max_subarray") {
                check_int(id, input, ads::max_subarray(parse_ints(input)),
                          std::atoi(expected.c_str()));
            } else if (id == "lcs") {
                check_int(id, input, ads::lcs(parts[0], parts[1]),
                          std::atoi(expected.c_str()));
            } else if (id == "knapsack_01") {
                int got = ads::knapsack_01(std::atoi(parts[0].c_str()),
                                           parse_ints(parts[1]),
                                           parse_ints(parts[2]));
                check_int(id, input, got, std::atoi(expected.c_str()));
            } else if (id == "edit_distance") {
                check_int(id, input, ads::edit_distance(parts[0], parts[1]),
                          std::atoi(expected.c_str()));
            } else if (id == "graph_bfs") {
                int got = ads::graph_bfs(parse_graph(parts[0]),
                                         std::atoi(parts[1].c_str()),
                                         std::atoi(parts[2].c_str()));
                check_int(id, input, got, std::atoi(expected.c_str()));
            } else if (id == "graph_dfs") {
                bool got = ads::graph_dfs(parse_graph(parts[0]),
                                          std::atoi(parts[1].c_str()),
                                          std::atoi(parts[2].c_str()));
                bool want = expected == "true";
                if (got != want) {
                    report_fail(id, input, got ? "true" : "false", expected);
                } else {
                    ++passed;
                }
            }
        }
    }
}

const std::set<std::string> kVoidOps = {"push",  "enqueue", "append",
                                        "prepend", "insert"};
const std::set<std::string> kResultOps = {
    "pop",      "dequeue",       "peek",     "is_empty", "size",
    "min",      "max",           "height",   "to_list",  "in_order"};

void run_structure_case(const std::string& id, const std::string& encoded) {
    ads::Stack stack;
    ads::Queue queue;
    ads::LinkedList list;
    ads::BST bst;
    ads::Trie trie;
    ads::MinHeap heap;

    auto run = [&](const std::string& op, const std::string& arg,
                   const std::string& expected) {
        auto check = [&](const std::string& label, std::string got) {
            if (expected.empty()) {
                ++passed;
                return;
            }
            if (got == expected) {
                ++passed;
            } else {
                report_fail(label, id + ":" + op, got, expected);
            }
        };

        if (id == "stack") {
            if (op == "push") {
                stack.push(std::atoi(arg.c_str()));
                ++passed;
            } else if (op == "pop") {
                check("stack.pop", std::to_string(stack.pop()));
            } else if (op == "peek") {
                check("stack.peek", std::to_string(stack.peek()));
            } else if (op == "is_empty") {
                check("stack.is_empty", stack.is_empty() ? "true" : "false");
            } else if (op == "size") {
                check("stack.size", std::to_string(stack.size()));
            }
        } else if (id == "queue") {
            if (op == "enqueue") {
                queue.enqueue(std::atoi(arg.c_str()));
                ++passed;
            } else if (op == "dequeue") {
                check("queue.dequeue", std::to_string(queue.dequeue()));
            } else if (op == "peek") {
                check("queue.peek", std::to_string(queue.peek()));
            } else if (op == "is_empty") {
                check("queue.is_empty", queue.is_empty() ? "true" : "false");
            } else if (op == "size") {
                check("queue.size", std::to_string(queue.size()));
            }
        } else if (id == "linked_list") {
            if (op == "append") {
                list.append(std::atoi(arg.c_str()));
                ++passed;
            } else if (op == "prepend") {
                list.prepend(std::atoi(arg.c_str()));
                ++passed;
            } else if (op == "get") {
                check("list.get", std::to_string(list.get(std::atoi(arg.c_str()))));
            } else if (op == "contains") {
                check("list.contains",
                      list.contains(std::atoi(arg.c_str())) ? "true" : "false");
            } else if (op == "remove") {
                check("list.remove",
                      list.remove(std::atoi(arg.c_str())) ? "true" : "false");
            } else if (op == "size") {
                check("list.size", std::to_string(list.size()));
            } else if (op == "to_list") {
                std::ostringstream out;
                auto values = list.to_list();
                for (size_t i = 0; i < values.size(); ++i) {
                    if (i > 0) out << ' ';
                    out << values[i];
                }
                check("list.to_list", out.str());
            }
        } else if (id == "bst") {
            if (op == "insert") {
                bst.insert(std::atoi(arg.c_str()));
                ++passed;
            } else if (op == "contains") {
                check("bst.contains",
                      bst.contains(std::atoi(arg.c_str())) ? "true" : "false");
            } else if (op == "remove") {
                check("bst.remove",
                      bst.remove(std::atoi(arg.c_str())) ? "true" : "false");
            } else if (op == "min") {
                check("bst.min", std::to_string(bst.min()));
            } else if (op == "max") {
                check("bst.max", std::to_string(bst.max()));
            } else if (op == "height") {
                check("bst.height", std::to_string(bst.height()));
            } else if (op == "size") {
                check("bst.size", std::to_string(bst.size()));
            } else if (op == "in_order") {
                std::ostringstream out;
                auto values = bst.in_order();
                for (size_t i = 0; i < values.size(); ++i) {
                    if (i > 0) out << ' ';
                    out << values[i];
                }
                check("bst.in_order", out.str());
            }
        } else if (id == "trie") {
            if (op == "insert") {
                trie.insert(arg);
                ++passed;
            } else if (op == "search") {
                check("trie.search", trie.search(arg) ? "true" : "false");
            } else if (op == "starts_with") {
                check("trie.starts_with", trie.starts_with(arg) ? "true" : "false");
            } else if (op == "size") {
                check("trie.size", std::to_string(trie.size()));
            }
        } else if (id == "min_heap") {
            if (op == "push") {
                heap.push(std::atoi(arg.c_str()));
                ++passed;
            } else if (op == "pop") {
                check("heap.pop", std::to_string(heap.pop()));
            } else if (op == "peek") {
                check("heap.peek", std::to_string(heap.peek()));
            } else if (op == "is_empty") {
                check("heap.is_empty", heap.is_empty() ? "true" : "false");
            } else if (op == "size") {
                check("heap.size", std::to_string(heap.size()));
            }
        }
    };

    for (const std::string& token : split(encoded, ',')) {
        if (token.empty()) {
            continue;
        }
        auto parts = split(token, ':');
        const std::string& op = parts[0];
        std::string arg;
        std::string expected;
        if (kVoidOps.count(op)) {
            arg = parts.size() > 1 ? parts[1] : "";
        } else if (kResultOps.count(op)) {
            expected = parts.size() > 1 ? parts[1] : "";
        } else {
            arg = parts.size() > 1 ? parts[1] : "";
            expected = parts.size() > 2 ? parts[2] : "";
        }
        run(op, arg, expected);
    }
}

void check_structures() {
    const auto& ids = std::vector<std::string>{
        "stack", "queue", "linked_list", "bst", "trie", "min_heap"};
    const auto& data = ads::gen::STRUCTURES;
    for (size_t i = 0; i < ids.size(); ++i) {
        for (const auto& testcase : data[i]) {
            run_structure_case(ids[i], testcase[0]);
        }
    }
}

}  // namespace

int main() {
    check_algorithms();
    check_structures();
    std::cout << "C++: " << passed << " passed, " << failures << " failed.\n";
    return failures == 0 ? 0 : 1;
}