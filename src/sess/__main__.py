"""Module entrypoint for `python -m sess`."""

from __future__ import annotations

from sess.bootstrap import build_container
from sess.interfaces.gradio_ui import create_demo


def main() -> None:
    container = build_container()
    demo = create_demo(container)
    demo.launch()


if __name__ == "__main__":
    main()

