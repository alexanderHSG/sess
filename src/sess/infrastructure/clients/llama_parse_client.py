"""LlamaParse adapter."""

from __future__ import annotations

from dataclasses import dataclass

import nest_asyncio
from llama_parse import LlamaParse

from sess.domain.errors import ExternalServiceError, ParsingError


@dataclass
class LlamaParseClient:
    api_key: str
    parsing_instruction: str
    language: str = "en"
    num_workers: int = 4

    def parse_to_markdown(self, file_path: str) -> str:
        if not self.api_key:
            raise ExternalServiceError("Missing LlamaParse key in `LLAMA_CLOUD_API_KEY`.")

        nest_asyncio.apply()
        parser = LlamaParse(
            api_key=self.api_key,
            result_type="markdown",
            num_workers=self.num_workers,
            verbose=True,
            language=self.language,
            parsing_instruction=self.parsing_instruction,
        )
        try:
            parsed_document = parser.load_data(file_path)
        except Exception as error:
            raise ExternalServiceError("LlamaParse request failed.") from error

        if not parsed_document:
            raise ParsingError("LlamaParse returned no parsed content.")
        return str(parsed_document)

