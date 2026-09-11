"""``python -m gui`` launcher. Runs without a display only when ``--selftest``."""

from __future__ import annotations

import sys


def main() -> int:
    if "--selftest" in sys.argv:
        from gui import core

        print(f"gui selftest ok (catalog: {core.engine_catalog_counts()})")
        return 0
    try:
        import tkinter  # noqa: F401
    except ImportError:
        print("tkinter is not available in this Python build.", file=sys.stderr)
        return 2
    from gui.app import main as app_main

    app_main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())