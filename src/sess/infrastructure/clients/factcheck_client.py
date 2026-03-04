"""Fact-checking service adapter."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from gradio_client import Client as GradioClient

from sess.domain.errors import ExternalServiceError
from sess.domain.models import FactualityItem


@dataclass
class FactCheckClient:
    hf_token: str
    space_name: str
    api_name: str

    def verify_markdown(self, markdown_input: str) -> list[FactualityItem]:
        if not self.hf_token:
            raise ExternalServiceError("Missing Hugging Face token in environment variable `token`.")

        try:
            client = GradioClient(self.space_name, hf_token=self.hf_token)
            raw_result = client.predict(input_markdown=markdown_input, api_name=self.api_name)
        except Exception as error:
            raise ExternalServiceError("Fact-check API request failed.") from error

        if isinstance(raw_result, str):
            try:
                payload = json.loads(raw_result)
            except json.JSONDecodeError as error:
                raise ExternalServiceError("Fact-check API returned invalid JSON.") from error
        elif isinstance(raw_result, list):
            payload = raw_result
        else:
            raise ExternalServiceError("Fact-check API returned unsupported response type.")

        return [self._to_item(row) for row in payload]

    def _to_item(self, row: dict[str, Any]) -> FactualityItem:
        statement = str(row.get("statement", ""))
        verification_result = str(row.get("verification_result", ""))
        search_string = str(row.get("searchString", ""))
        return FactualityItem(
            statement=statement,
            verification_result=verification_result,
            search_string=search_string,
        )

