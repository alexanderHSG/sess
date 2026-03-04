"""Thin launcher for the Sess Gradio app."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sess.bootstrap import build_container  # noqa: E402
from sess.interfaces.gradio_ui import create_demo  # noqa: E402


def main() -> None:
    container = build_container()
    demo = create_demo(container)
    demo.launch()


if __name__ == "__main__":
    main()

