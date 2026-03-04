"""Use case for single-slide feedback generation."""

from __future__ import annotations

from sess.infrastructure.clients.openai_client import OpenAISlideFeedbackClient


class GenerateSlideFeedbackUseCase:
    def __init__(self, openai_client: OpenAISlideFeedbackClient, prompt: str) -> None:
        self._openai_client = openai_client
        self._prompt = prompt

    def execute(self, image_path: str) -> str:
        return self._openai_client.generate_slide_feedback(
            image_path=image_path,
            prompt=self._prompt,
        )

