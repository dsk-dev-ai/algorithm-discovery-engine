"""Tkinter desktop GUI for algorithm-discovery-engine.

Launch with ``python -m gui`` (or ``python engine/runner.py gui``). The UI is
pure stdlib — no third-party runtime dependencies.
"""

from __future__ import annotations

import contextlib
import queue
import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
from collections.abc import Callable
from tkinter import ttk
from typing import Any, Literal

from gui import core

BG = "#0d1117"
PANEL = "#161b22"
BORDER = "#30363d"
TEXT = "#e6edf3"
MUTED = "#8b949e"
ACCENT = "#1f6feb"
GREEN = "#3fb950"
RED = "#f85149"

Report = dict[str, Any]
Message = tuple[Callable[[Any], None], Any]


class App:
    """Main application window."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("algorithm-discovery-engine")
        self.root.geometry("980x640")
        self.root.minsize(800, 540)
        self.root.configure(bg=BG)
        self._style()
        self._messages: queue.Queue[Message] = queue.Queue()
        self._busy = False
        self._tasks: list[ttk.Button] = []
        self.root.after(100, self._poll)
        self._build()

    # ------------------------------------------------------------------ style
    def _style(self) -> None:
        style = ttk.Style(self.root)
        with contextlib.suppress(tk.TclError):
            style.theme_use("clam")
        style.configure(
            "TNotebook", background=BG, borderwidth=0, tabmargins=(4, 4, 4, 0)
        )
        style.configure(
            "TNotebook.Tab",
            background=PANEL, foreground=MUTED, padding=(14, 8), borderwidth=0,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", ACCENT)],
            foreground=[("selected", "#ffffff")],
        )
        style.configure("TFrame", background=BG)
        style.configure(
            "Treeview",
            background=PANEL, fieldbackground=PANEL, foreground=TEXT,
            borderwidth=0, rowheight=24,
        )
        style.configure(
            "Treeview.Heading",
            background=BORDER, foreground=TEXT, relief="flat", padding=(6, 5),
        )
        style.map(
            "Treeview",
            background=[("selected", ACCENT)],
            foreground=[("selected", "#ffffff")],
        )
        style.configure("TLabel", background=BG, foreground=TEXT)
        style.configure("Muted.TLabel", background=BG, foreground=MUTED)
        style.configure(
            "TButton", background=PANEL, foreground=TEXT, borderwidth=1,
            focusthickness=0, padding=(10, 6),
        )
        style.configure(
            "Accent.TButton", background=ACCENT, foreground="#ffffff",
            borderwidth=1, padding=(10, 6),
        )
        style.configure(
            "TEntry", background=PANEL, foreground=TEXT, fieldbackground=PANEL,
            insertcolor=TEXT, bordercolor=BORDER,
        )

    # ------------------------------------------------------------ background
    def _button(
        self,
        parent: ttk.Frame,
        text: str,
        command: Callable[[], None],
        accent: bool = False,
    ) -> ttk.Button:
        button = ttk.Button(
            parent, text=text, command=command, takefocus=False,
            style="Accent.TButton" if accent else "TButton",
        )
        self._tasks.append(button)
        return button

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        for button in self._tasks:
            button.configure(state=tk.DISABLED if busy else tk.NORMAL)

    def _submit(
        self,
        task: Callable[[], Any],
        on_done: Callable[[Any], None],
        *labels: ttk.Label,
    ) -> None:
        def run() -> None:
            try:
                result = task()
            except Exception as exc:  # surfaced to the UI
                result = exc
            self._messages.put((on_done, result))

        self._set_busy(True)
        for label in labels:
            label.configure(text="working…", foreground=ACCENT)
        threading.Thread(target=run, daemon=True).start()

    def _poll(self) -> None:
        try:
            while True:
                callback, payload = self._messages.get_nowait()
                callback(payload)
        except queue.Empty:
            pass
        self.root.after(100, self._poll)

    # ------------------------------------------------------------------ build
    def _build(self) -> None:
        root_frame = ttk.Frame(self.root, padding=(12, 10, 12, 8))
        root_frame.pack(fill=tk.BOTH, expand=True)

        self.status = ttk.Label(root_frame, text="ready", style="Muted.TLabel")
        self.status.pack(side=tk.BOTTOM, anchor=tk.W, pady=(8, 0))

        notebook = ttk.Notebook(root_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        discover = ttk.Frame(notebook, padding=10)
        patterns = ttk.Frame(notebook, padding=10)
        engine = ttk.Frame(notebook, padding=10)
        notebook.add(discover, text=" Discover ")
        notebook.add(patterns, text=" Pattern discovery ")
        notebook.add(engine, text=" Engine ")

        self._build_discover(discover)
        self._build_patterns(patterns)
        self._build_engine(engine)
        self.refresh_report()

    def _build_discover(self, parent: ttk.Frame) -> None:
        top = ttk.Frame(parent)
        top.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(top, text="Local algorithm synthesizer", font=("", 16, "bold")).pack(side=tk.LEFT)
        self.summary_label = ttk.Label(top, text="", style="Muted.TLabel")
        self.summary_label.pack(side=tk.RIGHT)

        self._tree = ttk.Treeview(
            parent, show="headings",
            columns=("target", "kind", "status", "novelty", "ms", "strategy"),
        )
        tree_cols: list[tuple[str, str, int]] = [
            ("target", "Target", 190),
            ("kind", "Kind", 120),
            ("status", "Status", 110),
            ("novelty", "Novelty", 130),
            ("ms", "Search (ms)", 90),
            ("strategy", "Strategy", 120),
        ]
        for col, title, width in tree_cols:
            self._tree.heading(col, text=title)
            anchor: Literal["w", "center"] = (
                "w" if col in ("target", "kind", "strategy") else "center"
            )
            self._tree.column(col, width=width, anchor=anchor)
        self._tree.pack(fill=tk.BOTH, expand=True)

        controls = ttk.Frame(parent)
        controls.pack(fill=tk.X, pady=(8, 0))
        self._button(controls, "Run smoke pass", self.run_smoke, accent=True).pack(side=tk.LEFT)
        self._button(controls, "Run full pass", self.run_full).pack(side=tk.LEFT, padx=6)
        self._button(controls, "Refresh", self.refresh_report).pack(side=tk.LEFT)
        self._button(controls, "Open report (markdown)", self.open_report).pack(
            side=tk.LEFT, padx=6
        )
        self._button(controls, "Open solutions folder", self.open_solutions).pack(side=tk.LEFT)

    def _build_patterns(self, parent: ttk.Frame) -> None:
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(row, text="Integer sequence:").pack(side=tk.LEFT)
        self.sequence_var = tk.StringVar(value="1 4 9 16 25")
        entry = ttk.Entry(row, textvariable=self.sequence_var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        entry.bind("<Return>", lambda _event: self.run_patterns())
        self._button(row, "Discover", self.run_patterns, accent=True).pack(side=tk.LEFT)
        self.pattern_status = ttk.Label(row, text="", style="Muted.TLabel")
        self.pattern_status.pack(side=tk.LEFT, padx=8)

        self._ptree = ttk.Treeview(
            parent, show="headings", columns=("name", "confidence", "prediction", "detail"),
        )
        pat_cols: list[tuple[str, str, int, Literal["w", "center"]]] = [
            ("name", "Hypothesis", 200, "w"),
            ("confidence", "Confidence", 130, "center"),
            ("prediction", "Next term", 120, "center"),
            ("detail", "Detail", 400, "w"),
        ]
        for col, title, width, anchor in pat_cols:
            self._ptree.heading(col, text=title)
            self._ptree.column(col, width=width, anchor=anchor)
        self._ptree.pack(fill=tk.BOTH, expand=True)

    def _build_engine(self, parent: ttk.Frame) -> None:
        self.engine_summary = ttk.Label(
            parent, text="", font=("", 12), style="Muted.TLabel", justify=tk.LEFT,
        )
        self.engine_summary.pack(anchor=tk.W, pady=(0, 10))

        controls = ttk.Frame(parent)
        controls.pack(fill=tk.X)
        self._button(controls, "Check vectors", self.run_check, accent=True).pack(side=tk.LEFT)
        self._button(controls, "Run pytest", self.run_pytest).pack(side=tk.LEFT, padx=6)
        self._button(controls, "Run build", self.run_build).pack(side=tk.LEFT)
        self._button(controls, "Benchmark", self.run_bench).pack(side=tk.LEFT, padx=6)
        self._button(controls, "Open docs", self.open_docs).pack(side=tk.LEFT)
        self._button(controls, "Open GitHub", self.open_github).pack(side=tk.LEFT, padx=6)

        self.output = tk.Text(
            parent, bg=PANEL, fg=TEXT, insertbackground=TEXT, relief=tk.FLAT,
            wrap=tk.NONE, font=("DejaVu Sans Mono", 10), state=tk.DISABLED,
            highlightthickness=1, highlightbackground=BORDER,
        )
        self.output.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

    # ----------------------------------------------------------- discover tab
    def _render_report(self, summary: dict[str, Any]) -> None:
        for item in self._tree.get_children():
            self._tree.delete(item)
        for entry in summary.get("targets", []):
            status = entry.get("status", "?")
            self._tree.insert(
                "", tk.END,
                values=(
                    entry.get("id", ""),
                    entry.get("kind", ""),
                    status,
                    entry.get("novelty", ""),
                    entry.get("search_ms", ""),
                    entry.get("strategy", "") or entry.get("time_class", ""),
                ),
                tags=(status,),
            )
        self._tree.tag_configure("verified", foreground=GREEN)
        self._tree.tag_configure("candidate-rejected", foreground=RED)
        self._tree.tag_configure("no-candidate-found", foreground=MUTED)
        if summary.get("exists"):
            self.summary_label.configure(
                text=f"verified {summary['verified']} · rejected {summary['rejected']} · "
                f"missing {summary['missing']}"
            )
        else:
            self.summary_label.configure(text="no report yet", foreground=MUTED)

    def refresh_report(self) -> None:
        self._render_report(core.synth_summary(load_report()))

    def run_smoke(self) -> None:
        self._submit(
            lambda: core.run_synth(smoke=True),
            self._synth_done,
            self.summary_label,
        )

    def run_full(self) -> None:
        self._submit(
            lambda: core.run_synth(smoke=False),
            self._synth_done,
            self.summary_label,
        )

    def _synth_done(self, payload: Any) -> None:
        self._set_busy(False)
        if isinstance(payload, Exception):
            self.summary_label.configure(text=str(payload), foreground=RED)
            self._render_report(core.synth_summary())
        else:
            self._render_report(payload)
            self.summary_label.configure(text="done", foreground=GREEN)
        self.refresh_report()

    def open_report(self) -> None:
        if core.REPORT_MD.exists():
            webbrowser.open(core.REPORT_MD.resolve().as_uri())

    def open_solutions(self) -> None:
        core.SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)
        webbrowser.open(core.SOLUTIONS_DIR.resolve().as_uri())

    # -------------------------------------------------------- patterns tab
    def run_patterns(self) -> None:
        self._submit(
            lambda: core.run_patterns(self.sequence_var.get()),
            self._patterns_done,
            self.pattern_status,
        )

    def _patterns_done(self, payload: Any) -> None:
        self._set_busy(False)
        if isinstance(payload, Exception):
            self.pattern_status.configure(text=str(payload), foreground=RED)
            return
        for item in self._ptree.get_children():
            self._ptree.delete(item)
        for row in payload:
            self._ptree.insert(
                "", tk.END,
                values=(row["name"], f"{row['confidence']:.2f}", row["prediction"], row["detail"]),
            )
        self.pattern_status.configure(text=f"{len(payload)} hypotheses", foreground=GREEN)

    # ----------------------------------------------------------- engine tab
    def _run_cmd(self, argv: list[str]) -> dict[str, Any]:
        result = subprocess.run(
            argv, cwd=core.ROOT, capture_output=True, text=True, timeout=900, check=False
        )
        output = "".join((result.stdout or "")[-6000:]) + "\n" + "".join(
            (result.stderr or "")[-6000:]
        )
        return {"ok": result.returncode == 0, "output": output.strip() or "(no output)"}

    def run_check(self) -> None:
        self._submit(
            lambda: self._run_cmd([sys.executable, "engine/gen_tests.py", "--check"]),
            self._engine_done,
        )

    def run_pytest(self) -> None:
        self._submit(
            lambda: self._run_cmd([sys.executable, "-m", "pytest", "-q"]),
            self._engine_done,
        )

    def run_build(self) -> None:
        self._submit(
            lambda: self._run_cmd([sys.executable, "engine/runner.py", "build"]),
            self._engine_done,
        )

    def run_bench(self) -> None:
        self._submit(
            lambda: self._run_cmd([sys.executable, "engine/runner.py", "bench"]),
            self._engine_done,
        )

    def _engine_done(self, payload: Any) -> None:
        self._set_busy(False)
        self.output.configure(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        if isinstance(payload, Exception):
            self.output.insert(tk.END, str(payload))
            self.output.configure(state=tk.DISABLED)
            return
        body = payload["output"]
        self.output.insert(tk.END, body)
        self.output.configure(state=tk.DISABLED)
        self.status.configure(
            text="OK" if payload["ok"] else "FAILED",
            foreground=GREEN if payload["ok"] else RED,
        )

    def open_docs(self) -> None:
        webbrowser.open("https://dsk-dev-ai.github.io/algorithm-discovery-engine/")

    def open_github(self) -> None:
        webbrowser.open("https://github.com/dsk-dev-ai/algorithm-discovery-engine")


def load_report() -> Report | None:
    return core.load_report()


def main() -> None:
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()