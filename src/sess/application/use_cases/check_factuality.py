"""Use case for factuality verification."""

from __future__ import annotations

import urllib.parse

from sess.domain.models import FactualityItem
from sess.infrastructure.clients.factcheck_client import FactCheckClient
from sess.infrastructure.clients.llama_parse_client import LlamaParseClient
from sess.logging import get_logger

logger = get_logger(__name__)


def format_factuality_markdown(items: list[FactualityItem]) -> str:
    output = "## Verification Results\n\n"
    output += (
        "| Statements Found in the Presentation | Verification Result | "
        "Link to Consensus Research Assistant and Google for Background Info |\n"
    )
    output += (
        "|--------------------------------------|:-------------------:"
        "|----------------------------------------------------|\n"
    )

    for item in items:
        normalized = item.verification_result.strip().lower()
        is_true = normalized in {"t", "true"}
        symbol = "YES" if is_true else "NO"

        consensus_link = ""
        google_link = ""
        if not is_true:
            query = urllib.parse.quote(item.search_string)
            consensus_link = (
                "[Consensus](https://consensus.app/results/"
                f"?q={query}&synthesize=on&copilot=on)"
            )
            google_link = f"[Google](https://www.google.com/search?q={query})"

        statement = item.statement.replace("\n", " ")
        color = "green" if is_true else "red"
        output += (
            f"| {statement} | <span style='color:{color};'>{symbol}</span> | "
            f"{consensus_link} {google_link} |\n"
        )

    return output


class CheckFactualityUseCase:
    def __init__(
        self,
        parser_client: LlamaParseClient,
        factcheck_client: FactCheckClient,
    ) -> None:
        self._parser_client = parser_client
        self._factcheck_client = factcheck_client

    async def execute(self, file_path: str) -> str:
        logger.info("Starting factuality check for %s", file_path)
        parsed_markdown = self._parser_client.parse_to_markdown(file_path)
        items = self._factcheck_client.verify_markdown(parsed_markdown)
        return format_factuality_markdown(items)
