//! Catalog-driven integration tests: every shared test vector from
//! `catalog/problems.json` (generated into `ads::gen`) against the Rust tier.

use ads::gen::*;
use ads::{solutions as s, BST, LinkedList, MinHeap, Queue, Stack, Trie};

fn parse_ints(token: &str) -> Vec<i32> {
    token
        .split_whitespace()
        .filter_map(|part| part.parse::<i32>().ok())
        .collect()
}

fn format_ints(values: &[i32]) -> String {
    values
        .iter()
        .map(i32::to_string)
        .collect::<Vec<_>>()
        .join(" ")
}

fn check_boolean(label: &str, got: bool, expected: &str) {
    let want = expected == "true";
    assert_eq!(got, want, "{label}: got {got}, expected {want}");
}

#[test]
fn algorithms_pass_full_catalog() {
    for (id, cases) in ALGORITHMS {
        for &(input, expected) in *cases {
            let parts: Vec<&str> = input.split('|').collect();
            match *id {
                "two_sum" => {
                    let got = s::two_sum(&parse_ints(parts[0]), parts[1].parse().unwrap());
                    assert_eq!(
                        format_ints(&[got.0, got.1]),
                        expected,
                        "two_sum {:?}",
                        input
                    );
                }
                "binary_search" => {
                    let got =
                        s::binary_search(&parse_ints(parts[0]), parts[1].parse().unwrap());
                    assert_eq!(got.to_string(), expected, "binary_search {:?}", input);
                }
                "merge_sort" => {
                    let got = s::merge_sort(&parse_ints(input));
                    assert_eq!(format_ints(&got), expected, "merge_sort {:?}", input);
                }
                "quick_sort" => {
                    let got = s::quick_sort(&parse_ints(input));
                    assert_eq!(format_ints(&got), expected, "quick_sort {:?}", input);
                }
                "max_subarray" => {
                    let got = s::max_subarray(&parse_ints(input));
                    assert_eq!(got.to_string(), expected, "max_subarray {:?}", input);
                }
                "lcs" => {
                    let got = s::lcs(parts[0], parts[1]);
                    assert_eq!(got.to_string(), expected, "lcs {:?}", input);
                }
                "knapsack_01" => {
                    let capacity: usize = parts[0].parse().unwrap();
                    let got = s::knapsack_01(capacity, &parse_ints(parts[1]), &parse_ints(parts[2]));
                    assert_eq!(got.to_string(), expected, "knapsack_01 {:?}", input);
                }
                "edit_distance" => {
                    let got = s::edit_distance(parts[0], parts[1]);
                    assert_eq!(got.to_string(), expected, "edit_distance {:?}", input);
                }
                "graph_bfs" => {
                    let graph = s::parse_graph(parts[0]);
                    let got =
                        s::graph_bfs(&graph, parts[1].parse().unwrap(), parts[2].parse().unwrap());
                    assert_eq!(got.to_string(), expected, "graph_bfs {:?}", input);
                }
                "graph_dfs" => {
                    let graph = s::parse_graph(parts[0]);
                    let got = s::graph_dfs(
                        &graph,
                        parts[1].parse().unwrap(),
                        parts[2].parse().unwrap(),
                    );
                    check_boolean("graph_dfs", got, expected);
                }
                other => panic!("unknown algorithm: {other}"),
            }
        }
    }
}

const VOID_OPS: &[&str] = &["push", "enqueue", "append", "prepend", "insert"];
const RESULT_OPS: &[&str] = &[
    "pop",
    "dequeue",
    "peek",
    "is_empty",
    "size",
    "min",
    "max",
    "height",
    "to_list",
    "in_order",
];

fn parse_token(token: &str) -> (String, String, Option<&str>) {
    let mut parts = token.splitn(3, ':');
    let op = parts.next().unwrap();
    let first = parts.next().unwrap_or("");
    let (arg, expected) = if VOID_OPS.contains(&op) {
        (first, None)
    } else if RESULT_OPS.contains(&op) {
        ("", Some(first))
    } else {
        (first, parts.next())
    };
    (op.to_string(), arg.to_string(), expected)
}

#[test]
fn structures_pass_full_catalog() {
    let mut stack = Stack::default();
    let mut queue = Queue::default();
    let mut list = LinkedList::default();
    let mut bst = BST::default();
    let mut trie = Trie::default();
    let mut heap = MinHeap::default();

    let mut stack_handler = |op: &str, arg: &str, expected: Option<&str>| match op {
        "push" => stack.push(arg.parse().unwrap()),
        "pop" => assert_eq!(
            stack.pop().to_string(),
            expected.unwrap(),
            "stack.pop"
        ),
        "peek" => assert_eq!(
            stack.peek().to_string(),
            expected.unwrap(),
            "stack.peek"
        ),
        "is_empty" => check_boolean("stack.is_empty", stack.is_empty(), expected.unwrap()),
        "size" => assert_eq!(stack.size().to_string(), expected.unwrap(), "stack.size"),
        other => panic!("unknown stack op: {other}"),
    };

    let mut queue_handler = |op: &str, arg: &str, expected: Option<&str>| match op {
        "enqueue" => queue.enqueue(arg.parse().unwrap()),
        "dequeue" => assert_eq!(
            queue.dequeue().to_string(),
            expected.unwrap(),
            "queue.dequeue"
        ),
        "peek" => assert_eq!(
            queue.peek().to_string(),
            expected.unwrap(),
            "queue.peek"
        ),
        "is_empty" => check_boolean("queue.is_empty", queue.is_empty(), expected.unwrap()),
        "size" => assert_eq!(queue.size().to_string(), expected.unwrap(), "queue.size"),
        other => panic!("unknown queue op: {other}"),
    };

    let mut list_handler = |op: &str, arg: &str, expected: Option<&str>| match op {
        "append" => list.append(arg.parse().unwrap()),
        "prepend" => list.prepend(arg.parse().unwrap()),
        "get" => assert_eq!(
            list.get(arg.parse().unwrap()).to_string(),
            expected.unwrap(),
            "list.get"
        ),
        "contains" => check_boolean(
            "list.contains",
            list.contains(arg.parse().unwrap()),
            expected.unwrap(),
        ),
        "remove" => check_boolean(
            "list.remove",
            list.remove(arg.parse().unwrap()),
            expected.unwrap(),
        ),
        "size" => assert_eq!(list.size().to_string(), expected.unwrap(), "list.size"),
        "to_list" => assert_eq!(
            format_ints(&list.to_list()),
            expected.unwrap(),
            "list.to_list"
        ),
        other => panic!("unknown list op: {other}"),
    };

    let mut bst_handler = |op: &str, arg: &str, expected: Option<&str>| match op {
        "insert" => bst.insert(arg.parse().unwrap()),
        "contains" => check_boolean(
            "bst.contains",
            bst.contains(arg.parse().unwrap()),
            expected.unwrap(),
        ),
        "remove" => check_boolean(
            "bst.remove",
            bst.remove(arg.parse().unwrap()),
            expected.unwrap(),
        ),
        "min" => assert_eq!(bst.min().to_string(), expected.unwrap(), "bst.min"),
        "max" => assert_eq!(bst.max().to_string(), expected.unwrap(), "bst.max"),
        "height" => assert_eq!(bst.height().to_string(), expected.unwrap(), "bst.height"),
        "size" => assert_eq!(bst.size().to_string(), expected.unwrap(), "bst.size"),
        "in_order" => assert_eq!(
            format_ints(&bst.in_order()),
            expected.unwrap(),
            "bst.in_order"
        ),
        other => panic!("unknown bst op: {other}"),
    };

    let mut trie_handler = |op: &str, arg: &str, expected: Option<&str>| match op {
        "insert" => trie.insert(arg),
        "search" => check_boolean("trie.search", trie.search(arg), expected.unwrap()),
        "starts_with" => {
            check_boolean("trie.starts_with", trie.starts_with(arg), expected.unwrap())
        }
        "size" => assert_eq!(trie.size().to_string(), expected.unwrap(), "trie.size"),
        other => panic!("unknown trie op: {other}"),
    };

    let mut heap_handler = |op: &str, arg: &str, expected: Option<&str>| match op {
        "push" => heap.push(arg.parse().unwrap()),
        "pop" => assert_eq!(heap.pop().to_string(), expected.unwrap(), "heap.pop"),
        "peek" => assert_eq!(heap.peek().to_string(), expected.unwrap(), "heap.peek"),
        "is_empty" => check_boolean("heap.is_empty", heap.is_empty(), expected.unwrap()),
        "size" => assert_eq!(heap.size().to_string(), expected.unwrap(), "heap.size"),
        other => panic!("unknown heap op: {other}"),
    };

    let mut handlers: Vec<(&str, &mut dyn FnMut(&str, &str, Option<&str>))> = vec![
        ("stack", &mut stack_handler),
        ("queue", &mut queue_handler),
        ("linked_list", &mut list_handler),
        ("bst", &mut bst_handler),
        ("trie", &mut trie_handler),
        ("min_heap", &mut heap_handler),
    ];

    for (id, cases) in STRUCTURES {
        let h = handlers
            .iter_mut()
            .find(|(name, _)| name == id)
            .map(|(_, h)| h)
            .unwrap_or_else(|| panic!("no handler for {id}"));
        for encoded in *cases {
            for token in encoded.split(',') {
                if token.is_empty() {
                    continue;
                }
                let (op, arg, expected) = parse_token(token);
                (h)(&op, &arg, expected);
            }
        }
    }
}