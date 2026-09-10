// Cross-language benchmark workload (mirrors Java/Rust/Python benches).
// Fixed seed + fixed sizes so runner.py can tabulate per-algorithm wall time.

#include <chrono>
#include <iostream>
#include <random>
#include <string>
#include <vector>

#include "ads/solutions.hpp"

namespace {

template <typename Fn>
void time_it(const std::string& label, Fn&& fn) {
    auto start = std::chrono::high_resolution_clock::now();
    fn();
    auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(
                       std::chrono::high_resolution_clock::now() - start)
                       .count();
    std::cout << label << ": " << elapsed << " us\n";
}

std::vector<int> random_ints(int count, int seed) {
    std::mt19937 rng(seed);
    std::uniform_int_distribution<int> dist(0, 1'000'000'000);
    std::vector<int> out;
    out.reserve(count);
    for (int i = 0; i < count; ++i) {
        out.push_back(dist(rng));
    }
    return out;
}

std::vector<int> sorted_ints(int count) {
    std::vector<int> out;
    out.reserve(count);
    for (int i = 0; i < count; ++i) {
        out.push_back(i);
    }
    return out;
}

std::string random_string(int length, int seed) {
    std::mt19937 rng(seed);
    std::uniform_int_distribution<int> dist(0, 7);
    std::string out;
    out.reserve(length);
    for (int i = 0; i < length; ++i) {
        out.push_back(static_cast<char>('a' + dist(rng)));
    }
    return out;
}

std::vector<std::vector<int>> chain_graph(int size) {
    std::vector<std::vector<int>> graph(size);
    for (int i = 0; i < size; ++i) {
        if (i > 0) {
            graph[static_cast<size_t>(i)].push_back(i - 1);
        }
        if (i < size - 1) {
            graph[static_cast<size_t>(i)].push_back(i + 1);
        }
    }
    return graph;
}

}  // namespace

int main() {
    auto data = random_ints(200'000, 42);
    auto sorted = sorted_ints(1'000'000);

    time_it("merge_sort", [&] { ads::merge_sort(data); });
    time_it("quick_sort", [&] { ads::quick_sort(random_ints(200'000, 42)); });
    time_it("max_subarray", [&] { ads::max_subarray(random_ints(500'000, 7)); });
    time_it("two_sum", [&] { ads::two_sum(random_ints(50'000, 9), -1); });
    time_it("binary_search", [&] {
        ads::binary_search(sorted, sorted[sorted.size() / 2]);
    });
    time_it("lcs", [&] {
        ads::lcs(random_string(2'000, 11), random_string(2'000, 13));
    });
    time_it("knapsack_01", [&] {
        ads::knapsack_01(5'000, random_ints(1'000, 21), random_ints(1'000, 31));
    });
    time_it("edit_distance", [&] {
        ads::edit_distance(random_string(1'000, 41), random_string(1'000, 43));
    });
    time_it("graph_bfs", [&] { ads::graph_bfs(chain_graph(100'000), 0, 99'999); });
    time_it("graph_dfs", [&] { ads::graph_dfs(chain_graph(100'000), 0, 99'999); });
    return 0;
}