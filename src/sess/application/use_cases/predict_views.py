"""Use case for deck-level view prediction and quality scoring."""

from __future__ import annotations

import numpy as np
import pandas as pd

from sess.domain.constants import AUTHOR_CHOICES, CATEGORY_CHOICES
from sess.domain.errors import FeatureExtractionError
from sess.domain.models import SlideDeckRequest, ViewPredictionResult
from sess.domain.services.feature_extractor import analyze_slidedeck_pdf
from sess.domain.services.quality_scoring import (
    LimeExplainerProvider,
    aggregate_quality_scores,
)
from sess.infrastructure.ml.model_registry import ModelRegistry
from sess.interfaces.renderers.quality_dimension_renderer import html_transformer
from sess.logging import get_logger

logger = get_logger(__name__)


class PredictViewsUseCase:
    def __init__(
        self,
        model_registry: ModelRegistry,
        explainer_provider: LimeExplainerProvider,
    ) -> None:
        self._model_registry = model_registry
        self._explainer_provider = explainer_provider

    async def execute(self, request: SlideDeckRequest) -> ViewPredictionResult:
        logger.info("Starting view prediction for %s", request.uploaded_file)

        raw_features = analyze_slidedeck_pdf(request.uploaded_file)
        if raw_features is None:
            raise FeatureExtractionError("Could not extract features from uploaded PDF.")

        features = pd.DataFrame([raw_features], columns=raw_features.keys())

        for category in CATEGORY_CHOICES:
            features[f"category_{category}"] = False
        for author in AUTHOR_CHOICES:
            features[author] = False

        category_column = f"category_{request.category}"
        if category_column in features.columns:
            features[category_column] = True
        if request.author in features.columns:
            features[request.author] = True

        features["time_elapsed_until_Oct23"] = int(request.prediction_days)
        features = features.reindex(sorted(features.columns), axis=1)

        model_input = features.drop(columns=["content"], errors="ignore")
        svr_predictions = self._model_registry.svr.predict(model_input)

        explainer = self._explainer_provider.get()
        explanation = explainer.explain_instance(
            data_row=model_input.iloc[0],
            predict_fn=self._model_registry.svr.predict,
            num_features=min(400, model_input.shape[1]),
        )

        quality_scores = aggregate_quality_scores(explanation.as_list(), request.author)
        predicted_views = int(np.exp(svr_predictions[0]) - 0.1)
        quality_dimensions_html, predicted_views_html = html_transformer(predicted_views, quality_scores)

        return ViewPredictionResult(
            predicted_views=predicted_views,
            quality_scores=quality_scores,
            quality_dimensions_html=quality_dimensions_html,
            predicted_views_html=predicted_views_html,
        )

