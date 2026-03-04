"""OpenAI adapter."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from sess.domain.errors import ExternalServiceError


@dataclass
class OpenAISlideFeedbackClient:
    api_key: str
    model_name: str

    def generate_slide_feedback(self, image_path: str | Path, prompt: str, max_tokens: int = 2048) -> str:
        if not self.api_key:
            raise ExternalServiceError("Missing OpenAI API key in environment variable `OpenAI`.")

        image_file_path = Path(image_path)
        with image_file_path.open("rb") as file_handle:
            base64_image = base64.b64encode(file_handle.read()).decode("utf-8")

        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                    ],
                }
            ],
            "max_tokens": max_tokens,
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            json=payload,
            timeout=120,
        )

        if response.status_code >= 400:
            raise ExternalServiceError(
                f"OpenAI API request failed with status {response.status_code}: {response.text}"
            )

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise ExternalServiceError("Unexpected OpenAI response schema.") from error

