"""Backward-compatible parser utility wrapper."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sess.config.settings import get_settings  # noqa: E402
from sess.domain.constants import FACTUALITY_PARSE_INSTRUCTION  # noqa: E402
from sess.infrastructure.clients.llama_parse_client import LlamaParseClient  # noqa: E402


def parse_pdf(file_path: str) -> str:
    settings = get_settings()
    client = LlamaParseClient(
        api_key=settings.llama_cloud_api_key,
        parsing_instruction=FACTUALITY_PARSE_INSTRUCTION,
    )
    return client.parse_to_markdown(file_path)


if __name__ == "__main__":
    import os

    path = os.path.realpath(__file__)
    target = Path(path).parent / "ChatGPT_BeyondtheHype.pdf"
    print(parse_pdf(str(target)))

