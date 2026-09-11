# Multi-language engine

## Catalog

`catalog/problems.json` is the single source of truth. Every algorithm and
structure carries a shared test-vector set that is checked in **all four
languages**.

| Algorithms (10)                                          | Data structures (6)            |
| -------------------------------------------------------- | ------------------------------ |
| `two_sum`, `binary_search`, `merge_sort`, `quick_sort`    | `stack`, `queue`, `linked_list` |
| `max_subarray`, `lcs`, `knapsack_01`, `edit_distance`     | `bst`, `trie`, `min_heap`       |
| `graph_bfs`, `graph_dfs`                                  |                                |

`engine/gen_tests.py` expands these into identical per-language test vectors,
which are committed so every tier runs the exact same dataset.

## Language tiers

| Tier   | Location                 | Approach                                       |
| ------ | ------------------------ | ---------------------------------------------- |
| Java   | `languages/java/`        | OO reference implementations                   |
| C++    | `languages/cpp/`         | modern C++17, RAII, iterators                  |
| Rust   | `languages/rust/`        | ownership-safe, zero dependencies              |
| Python | `src/ads/`               | regular + advanced (`*_advanced`, mypy strict) |

## Running the engine

```sh
python engine/runner.py check     # assert committed vectors match the catalog
python engine/runner.py build     # compile every tier (no execution)
python engine/runner.py test      # run the catalog suite in all 4 languages
python engine/runner.py bench     # benchmark all tiers, print comparison table
```

## Sample benchmark

Microseconds, lower is better:

```
algorithm             Python        Java         C++        Rust
merge_sort           928,850      85,358      66,972      39,647
quick_sort           702,918      41,562      22,942      17,610
max_subarray         444,168      17,881       9,702          78
two_sum               32,847      30,393     582,269     659,066
lcs                  901,711      53,888      21,300      24,979
knapsack_01            1,595      25,732      17,617      23,390
```

!!! note
    Languages may pick different strategies for the same problem — Java's
    `two_sum` uses a hash map while C++/Rust use a quadratic scan — so the table
    showcases trade-offs rather than an exact contest.

## Per-language checks

```sh
# Python
uv run pytest -q
uv run ruff check src tests
uv run mypy -p algo_discovery -p ads -p synth -p gui

# Java
cd languages/java && javac -d out $(find src -name '*.java') && java -cp out ads.TestRunner

# C++
cd languages/cpp && g++ -std=c++17 -O2 -I include tests/test_runner.cpp -o build/runner && ./build/runner

# Rust
cd languages/rust && cargo test --quiet
```