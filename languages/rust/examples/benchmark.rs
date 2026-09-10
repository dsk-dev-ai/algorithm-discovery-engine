//! Cross-language benchmark workload (mirrors Java/C++/Python benches).
//! Fixed seed + fixed sizes so runner.py can tabulate per-algorithm wall time.
//! Run: `cargo run --release --example benchmark`

use ads::solutions;
use std::time::Instant;

fn random_ints(count: usize, seed: u64) -> Vec<i32> {
    let mut state = seed;
    let mut next = move || {
        state = state.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        (state.wrapping_shr(33) as u32) % 1_000_000_000
    };
    (0..count).map(|_| next() as i32).collect()
}

fn sorted_ints(count: usize) -> Vec<i32> {
    (0..count as i32).collect()
}

fn random_string(length: usize, seed: u64) -> String {
    let mut state = seed;
    let mut next = move || {
        state = state.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        (state.wrapping_shr(33) as u32) % 8
    };
    (0..length).map(|_| (b'a' + next() as u8) as char).collect()
}

fn chain_graph(size: usize) -> Vec<Vec<usize>> {
    (0..size)
        .map(|i| {
            let mut neighbors = Vec::with_capacity(2);
            if i > 0 {
                neighbors.push(i - 1);
            }
            if i < size - 1 {
                neighbors.push(i + 1);
            }
            neighbors
        })
        .collect()
}

fn time_it(label: &str, task: impl FnOnce()) {
    let start = Instant::now();
    task();
    println!("{label}: {} us", start.elapsed().as_micros());
}

fn main() {
    let data = random_ints(200_000, 42);
    let sorted = sorted_ints(1_000_000);

    time_it("merge_sort", || {
        solutions::merge_sort(&data);
    });
    time_it("quick_sort", || {
        solutions::quick_sort(&random_ints(200_000, 42));
    });
    time_it("max_subarray", || {
        solutions::max_subarray(&random_ints(500_000, 7));
    });
    time_it("two_sum", || {
        solutions::two_sum(&random_ints(50_000, 9), -1);
    });
    time_it("binary_search", || {
        solutions::binary_search(&sorted, sorted[sorted.len() / 2]);
    });
    time_it("lcs", || {
        solutions::lcs(&random_string(2_000, 11), &random_string(2_000, 13));
    });
    time_it("knapsack_01", || {
        solutions::knapsack_01(5_000, &random_ints(1_000, 21), &random_ints(1_000, 31));
    });
    time_it("edit_distance", || {
        solutions::edit_distance(&random_string(1_000, 41), &random_string(1_000, 43));
    });
    time_it("graph_bfs", || {
        solutions::graph_bfs(&chain_graph(100_000), 0, 99_999);
    });
    time_it("graph_dfs", || {
        solutions::graph_dfs(&chain_graph(100_000), 0, 99_999);
    });
}