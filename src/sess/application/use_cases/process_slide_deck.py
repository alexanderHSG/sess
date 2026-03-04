"""Use case for end-to-end slide deck processing."""

from __future__ import annotations

import asyncio

from sess.application.use_cases.check_factuality import CheckFactualityUseCase
from sess.application.use_cases.predict_views import PredictViewsUseCase
from sess.domain.models import SlideDeckProcessingResult, SlideDeckRequest


class ProcessSlideDeckUseCase:
    def __init__(
        self,
        predict_views_use_case: PredictViewsUseCase,
        factuality_use_case: CheckFactualityUseCase,
    ) -> None:
        self._predict_views_use_case = predict_views_use_case
        self._factuality_use_case = factuality_use_case

    async def execute(self, request: SlideDeckRequest) -> SlideDeckProcessingResult:
        view_task = asyncio.create_task(self._predict_views_use_case.execute(request))
        factuality_task = asyncio.create_task(self._factuality_use_case.execute(request.uploaded_file))

        factuality_markdown = await factuality_task
        view_prediction = await view_task

        return SlideDeckProcessingResult(
            quality_dimensions_html=view_prediction.quality_dimensions_html,
            predicted_views_html=view_prediction.predicted_views_html,
            factuality_markdown=factuality_markdown,
        )

