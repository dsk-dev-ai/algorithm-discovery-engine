"""Cross-language build/test/benchmark runner for the solving engine.

Usage:
    python engine/runner.py <command>

Commands:
    test        Run the catalog test suite in every language.
    bench       Build and run each language's benchmark, then print a table.
    build       Compile every language tier (no execution).
    check       Verify committed test vectors are in sync with the catalog.
    discover    Run the algorithm synthesizer (smoke pass, ~2 min).
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGS = ROOT / "languages"
JAVA = LANGS / "java"
CPP = LANGS / "cpp"
RUST = LANGS / "rust"

BENCH_ALGOS = [
    "merge_sort",
    "quick_sort",
    "max_subarray",
    "two_sum",
    "binary_search",
    "lcs",
    "knapsack_01",
    "edit_distance",
    "graph_bfs",
    "graph_dfs",
]


def run(cmd: list[str], cwd: Path, timeout: int = 600) -> subprocess.CompletedProcess[str]:
    print(f"$ {' '.join(cmd)}  (in {cwd.name})")
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    return subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False, env=env
    )


def describe(result: subprocess.CompletedProcess[str]) -> str:
    if result.returncode == 0:
        return "OK"
    return "FAILED"


def check(cmd: list[str], cwd: Path, label: str, timeout: int = 900) -> None:
    started = time.monotonic()
    result = run(cmd, cwd, timeout)
    elapsed = time.monotonic() - started
    status = describe(result)
    marker = f"[{status}] {label} ({elapsed:.1f}s)"
    print(marker)
    if result.returncode != 0:
        tail = "".join(
            (result.stdout or "")[-4000:]
        ) + "".join((result.stderr or "")[-4000:])
        print(tail)
    if result.returncode != 0:
        sys.exit(f"FAILED: {label}")


def cmd_test_python() -> None:
    check([sys.executable, "-m", "pytest", "-q"], ROOT, "python pytest")


def cmd_test_java() -> None:
    compile_java()
    check(["java", "-cp", str(JAVA / "out"), "ads.TestRunner"], JAVA, "java TestRunner")


def cmd_test_cpp() -> None:
    cmd_build_cpp()
    runner = CPP / "build" / "test_runner"
    check([str(runner)], CPP, "cpp test runner")


def cmd_test_rust() -> None:
    check(["cargo", "test", "--quiet"], RUST, "rust cargo test")


def cmd_test() -> None:
    cmd_test_python()
    cmd_test_java()
    cmd_test_cpp()
    cmd_test_rust()
    print("\nAll language tiers PASS.")


def cmd_check() -> None:
    check([sys.executable, "engine/gen_tests.py", "--check"], ROOT, "vectors in sync")


def compile_java() -> None:
    check(["javac", "-d", str(JAVA / "out"), *project("java", "*.java")], JAVA, "java compile")


def cmd_build_cpp() -> None:
    build = CPP / "build"
    build.mkdir(exist_ok=True)
    check(
        ["g++", "-std=c++17", "-O2", "-I", str(CPP / "include"),
         str(CPP / "tests/test_runner.cpp"), "-o", str(build / "test_runner")],
        CPP, "cpp compile",
    )
    check(
        ["g++", "-std=c++17", "-O2", "-I", str(CPP / "include"),
         str(CPP / "bench/benchmark.cpp"), "-o", str(build / "benchmark")],
        CPP, "cpp bench compile",
    )


def cmd_build() -> None:
    check([sys.executable, "-m", "compileall", "-q", "src"], ROOT, "python compileall")
    compile_java()
    cmd_build_cpp()
    check(["cargo", "build", "--quiet"], RUST, "rust cargo build")
    print("\nAll language tiers build OK.")


def cmd_bench() -> None:
    results: dict[str, dict[str, int]] = defaultdict(dict)

    def parse(stream: str) -> dict[str, int]:
        out = {}
        for line in stream.splitlines():
            match_ = re.match(r"^(\w+):\s+(\d+)\s+us$", line.strip())
            if match_:
                out[match_[1]] = int(match_[2])
        return out

    # Python
    started = time.monotonic()
    result = run([sys.executable, "-m", "ads.benchmark"], ROOT, 600)
    print(f"[{describe(result)}] python benchmark ({time.monotonic() - started:.1f}s)")
    results["Python"] = parse(result.stdout)

    # Java
    compile_java()
    started = time.monotonic()
    result = run(["java", "-cp", str(JAVA / "out"), "ads.Benchmark"], JAVA, 600)
    print(f"[{describe(result)}] java benchmark ({time.monotonic() - started:.1f}s)")
    results["Java"] = parse(result.stdout)

    # C++
    cmd_build_cpp()
    bench_bin = CPP / "build" / "benchmark"
    started = time.monotonic()
    result = run([str(bench_bin)], CPP, 600)
    print(f"[{describe(result)}] cpp benchmark ({time.monotonic() - started:.1f}s)")
    results["C++"] = parse(result.stdout)

    # Rust
    started = time.monotonic()
    result = run(["cargo", "run", "--quiet", "--release", "--example", "benchmark"], RUST, 900)
    print(f"[{describe(result)}] rust benchmark ({time.monotonic() - started:.1f}s)")
    results["Rust"] = parse(result.stdout)

    print_table(results)


def print_table(results: dict[str, dict[str, int]]) -> None:
    langs = list(results)
    header = f"{'algorithm':<16}" + "".join(f"{name:>12}" for name in langs)
    print(f"\nBenchmark (microseconds, lower is better)\n{header}")
    for algo in BENCH_ALGOS:
        row = [algo.ljust(16)]
        for lang in langs:
            value = results[lang].get(algo)
            row.append(f"{value:>12,}" if value is not None else f"{'n/a':>12}")
        print("".join(row))
    totals = {lang: sum(results[lang].values()) for lang in langs}
    worst = max(totals.values(), default=1)
    print("".join(["total".ljust(16)] + [f"{totals[lang]:>12,}" for lang in langs]))
    print("".join(["relative".ljust(16)] + [f"{totals[lang] / worst:>12.2f}x" for lang in langs]))


def project(lang: str, pattern: str) -> list[str]:
    base = {"java": JAVA, "cpp": CPP, "rust": RUST}[lang]
    files = sorted(str(p) for p in base.rglob(pattern) if "build" not in p.parts and "out" not in p.parts)
    return files


def cmd_discover_smoke() -> None:
    check(
        [sys.executable, "-m", "synth", "discover", "--smoke"],
        ROOT, "synth discover --smoke", timeout=300,
    )


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    command = sys.argv[1]
    handlers = {
        "test": cmd_test,
        "bench": cmd_bench,
        "build": cmd_build,
        "check": cmd_check,
        "discover": cmd_discover_smoke,
    }
    handlers[command]()


if __name__ == "__main__":
    main()