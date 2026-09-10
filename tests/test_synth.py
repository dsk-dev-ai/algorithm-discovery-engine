"""Synthesizer test harness.

Covers grammar evaluation/rendering, corpus parsing/fuzzing, search backends
(scan + template), and the discovery orchestrator's verification + reporting
pipeline.
"""

from __future__ import annotations

from synth import corpus, grammar, search
from synth.discovery import _classify, _solved_catalog_ids

# ---------------------------------------------------------------------------
# grammar
# ---------------------------------------------------------------------------

class TestGrammar:
    def test_evaluate_literal(self) -> None:
        assert grammar.evaluate(grammar.const(42), {}) == 42

    def test_evaluate_var(self) -> None:
        env = {"x": 3, "i": 1}
        node = grammar.var("x")
        assert grammar.evaluate(node, env) == 3

    def test_evaluate_add(self) -> None:
        node = grammar.call("add", grammar.var("x"), grammar.const(2))
        assert grammar.evaluate(node, {"x": 5}) == 7

    def test_evaluate_max(self) -> None:
        node = grammar.call("max", grammar.var("x"), grammar.var("i"))
        assert grammar.evaluate(node, {"x": 3, "i": 7}) == 7

    def test_evaluate_div_zero(self) -> None:
        node = grammar.call("fdiv", grammar.const(10), grammar.const(0))
        assert grammar.evaluate(node, {}) == 10  # neutral short-circuit

    def test_to_python_roundtrip(self) -> None:
        node = grammar.call("max", grammar.var("x"), grammar.const(0))
        rendered = grammar.to_python(node)
        assert "max" in rendered
        assert "x" in rendered
        assert "0" in rendered

    def test_size(self) -> None:
        node = grammar.call("add", grammar.var("x"), grammar.const(1))
        # add(x, 1) = add node + var node + x node + const node = 4
        assert grammar.size(node) == 4

    def test_dedupe_python(self) -> None:
        nodes = [
            grammar.call("add", grammar.var("x"), grammar.const(1)),
            grammar.call("add", grammar.var("x"), grammar.const(1)),
            grammar.var("x"),
        ]
        assert len(grammar.dedupe_python(nodes)) == 2

    def test_grow_depth_1(self) -> None:
        nodes = grammar.grow(1, ("x",), (0,))
        python_sources = {grammar.to_python(n) for n in nodes}
        assert "x" in python_sources
        assert "0" in python_sources

    def test_tree_depth(self) -> None:
        node = grammar.call("add", grammar.var("x"), grammar.const(1))
        # add -> var -> x (depth 3); const -> 1 (depth 2); max is 3
        assert grammar.tree_depth(node) == 3


# ---------------------------------------------------------------------------
# corpus
# ---------------------------------------------------------------------------

class TestCorpus:
    def test_parse_input_legacy_multi(self) -> None:
        result = corpus.parse_input("1 2 3|")
        assert result == [[1, 2, 3]]

    def test_parse_input_legacy_scalar(self) -> None:
        result = corpus.parse_input("5|")
        assert result == [5]

    def test_parse_input_typed_list(self) -> None:
        result = corpus.parse_input("0|", ["list"])
        assert result == [[0]]

    def test_parse_input_typed_int(self) -> None:
        result = corpus.parse_input("3|", ["int"])
        assert result == [3]

    def test_parse_input_empty_list(self) -> None:
        result = corpus.parse_input("|", ["list"])
        assert result == [[]]

    def test_parse_output_bool(self) -> None:
        assert corpus.parse_output("true") is True
        assert corpus.parse_output("false") is False

    def test_parse_output_int(self) -> None:
        assert corpus.parse_output("42") == 42

    def test_load_targets_has_all(self) -> None:
        targets = corpus.load_targets()
        expected = {
            "max_subarray", "max_circular_subarray", "best_time_buy_sell",
            "jump_game", "contains_duplicate", "majority_element",
            "climbing_stairs",
        }
        assert set(targets.keys()) == expected

    def test_oracles_correct(self) -> None:
        assert corpus.oracle_jump_game([2, 3, 1, 1, 4]) is True
        assert corpus.oracle_jump_game([3, 2, 1, 0, 4]) is False
        assert corpus.oracle_best_time_buy_sell([7, 1, 5, 3, 6, 4]) == 5
        assert corpus.oracle_max_circular_subarray([5, -3, 5]) == 10
        assert corpus.oracle_climbing_stairs(4) == 5
        assert corpus.oracle_contains_duplicate([1, 2, 3, 1]) is True
        assert corpus.oracle_majority_element([3, 2, 3]) == 3

    def test_fuzz_cases_length(self) -> None:
        cases = corpus.fuzz_cases("jump_game", 5)
        assert len(cases) == 5
        for inputs, expected in cases:
            assert isinstance(inputs, list)
            assert len(inputs) == 1
            assert isinstance(expected, bool)

    def test_fuzz_cases_oracle_agrees(self) -> None:
        cases = corpus.fuzz_cases("climbing_stairs", 20)
        for inputs, expected in cases:
            assert corpus.oracle_climbing_stairs(*inputs) == expected


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------

class TestScanSearch:
    def test_jump_game_verified(self) -> None:
        target = corpus.load_targets()["jump_game"]
        candidate = search.scan_search(target, max_candidates=300_000)
        assert candidate is not None
        assert candidate.fuzz_verified is True
        assert "discovered_jump_game" in candidate.source
        ns: dict = {}
        exec(compile(candidate.source, "<s>", "exec"), ns)
        fn = ns[candidate.function_name]
        assert fn([2, 3, 1, 1, 4]) is True
        assert fn([3, 2, 1, 0, 4]) is False
        assert fn([0]) is True

    def test_best_time_buy_sell_verified(self) -> None:
        target = corpus.load_targets()["best_time_buy_sell"]
        candidate = search.scan_search(target, max_candidates=300_000)
        assert candidate is not None
        assert candidate.fuzz_verified is True
        ns: dict = {}
        exec(compile(candidate.source, "<s>", "exec"), ns)
        fn = ns[candidate.function_name]
        assert fn([7, 1, 5, 3, 6, 4]) == 5
        assert fn([7, 6, 4, 3, 1]) == 0
        assert fn([]) == 0

    def test_max_subarray_verified(self) -> None:
        target = corpus.load_targets()["max_subarray"]
        candidate = search.scan_search(target, max_candidates=300_000)
        assert candidate is not None
        assert candidate.fuzz_verified is True
        ns: dict = {}
        exec(compile(candidate.source, "<s>", "exec"), ns)
        fn = ns[candidate.function_name]
        assert fn([1, -2, 3, 4]) == 7
        assert fn([-1, -2, -3]) == -1
        assert fn([]) == 0


class TestTemplateDiscover:
    def test_vote(self) -> None:
        target = corpus.load_targets()["majority_element"]
        candidates = search.template_discover(target)
        assert len(candidates) == 1
        c = candidates[0]
        ns: dict = {}
        exec(compile(c.source, "<s>", "exec"), ns)
        fn = ns[c.function_name]
        assert fn([3, 2, 3]) == 3
        assert fn([2, 2, 1, 1, 1, 2, 2]) == 2

    def test_seen(self) -> None:
        target = corpus.load_targets()["contains_duplicate"]
        candidates = search.template_discover(target)
        assert len(candidates) == 1
        c = candidates[0]
        ns: dict = {}
        exec(compile(c.source, "<s>", "exec"), ns)
        fn = ns[c.function_name]
        assert fn([1, 2, 3, 1]) is True
        assert fn([1, 2, 3, 4]) is False

    def test_fib(self) -> None:
        target = corpus.load_targets()["climbing_stairs"]
        candidates = search.template_discover(target)
        assert len(candidates) == 1
        c = candidates[0]
        ns: dict = {}
        exec(compile(c.source, "<s>", "exec"), ns)
        fn = ns[c.function_name]
        assert fn(4) == 5
        assert fn(0) == 1

    def test_circular_kadane(self) -> None:
        target = corpus.load_targets()["max_circular_subarray"]
        candidates = search.template_discover(target)
        assert len(candidates) == 1
        c = candidates[0]
        ns: dict = {}
        exec(compile(c.source, "<s>", "exec"), ns)
        fn = ns[c.function_name]
        assert fn([5, -3, 5]) == 10
        assert fn([-3, -2, -1]) == 0


# ---------------------------------------------------------------------------
# novelty classification
# ---------------------------------------------------------------------------

class TestNovelty:
    def test_rediscovered_in_catalog(self) -> None:
        solved = _solved_catalog_ids()
        assert "max_subarray" in solved
        result = _classify("max_subarray", "scan")
        assert result["status"] == "rediscovered"

    def test_new_to_catalog(self) -> None:
        result = _classify("best_time_buy_sell", "scan")
        assert result["status"] == "new-to-catalog"


# ---------------------------------------------------------------------------
# discovery orchestrator (smoke)
# ---------------------------------------------------------------------------

class TestDiscovery:
    def test_smoke_all_verified(self) -> None:
        from synth.discovery import discover

        report = discover(smoke=True, fuzz_count=10)
        assert report["fuzz_per_target"] == 10
        verified = [e for e in report["targets"] if e["status"] == "verified"]
        rejected = [e for e in report["targets"] if e["status"] == "candidate-rejected"]
        missing = [e for e in report["targets"] if e["status"] == "no-candidate-found"]
        assert len(report["targets"]) == 7
        assert len(verified) == 7, (
            f"verified={len(verified)} rejected={len(rejected)} "
            f"missing={len(missing)}"
        )
        assert len(rejected) == 0
        assert len(missing) == 0

    def test_report_schema(self) -> None:
        from synth.discovery import discover

        report = discover(smoke=True, fuzz_count=10)
        assert "generated_at" in report
        assert "targets" in report
        for entry in report["targets"]:
            assert "id" in entry
            assert "status" in entry
            assert "kind" in entry
            assert "source" in entry or entry["status"] == "no-candidate-found"

    def test_solutions_written(self) -> None:
        from synth.discovery import SOLUTIONS_DIR, discover

        discover(smoke=True, fuzz_count=10)
        for pid in ("jump_game", "best_time_buy_sell", "max_subarray"):
            sol = SOLUTIONS_DIR / f"{pid}.py"
            assert sol.exists(), f"missing solution: {sol}"
            content = sol.read_text()
            assert "def discovered_" in content
