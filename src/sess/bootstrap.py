"""Application composition root."""

from __future__ import annotations

from dataclasses import dataclass

from sess.application.use_cases.check_factuality import CheckFactualityUseCase
from sess.application.use_cases.generate_slide_feedback import GenerateSlideFeedbackUseCase
from sess.application.use_cases.predict_views import PredictViewsUseCase
from sess.application.use_cases.process_slide_deck import ProcessSlideDeckUseCase
from sess.config.settings import Settings, get_settings
from sess.domain.constants import FACTUALITY_PARSE_INSTRUCTION, SLIDE_FEEDBACK_PROMPT
from sess.domain.services.quality_scoring import LimeExplainerProvider
from sess.infrastructure.clients.factcheck_client import FactCheckClient
from sess.infrastructure.clients.llama_parse_client import LlamaParseClient
from sess.infrastructure.clients.openai_client import OpenAISlideFeedbackClient
from sess.infrastructure.db.sqlite_repo import SQLiteFeatureRepository
from sess.infrastructure.ml.model_registry import ModelRegistry
from sess.logging import configure_logging


@dataclass(frozen=True)
class AppContainer:
    settings: Settings
    process_slide_deck_use_case: ProcessSlideDeckUseCase
    generate_slide_feedback_use_case: GenerateSlideFeedbackUseCase


def build_container(settings: Settings | None = None) -> AppContainer:
    resolved_settings = settings or get_settings()
    configure_logging(resolved_settings.log_level)

    repository = SQLiteFeatureRepository(
        db_path=resolved_settings.db_path,
        table_name=resolved_settings.db_table_name,
    )
    explainer_provider = LimeExplainerProvider(loader=repository.load_feature_rows)
    model_registry = ModelRegistry.get_instance(
        mlp_path=resolved_settings.model_mlp_path,
        svr_path=resolved_settings.model_svr_path,
        rfr_path=resolved_settings.model_rfr_path,
    )

    predict_views = PredictViewsUseCase(
        model_registry=model_registry,
        explainer_provider=explainer_provider,
    )

    parser_client = LlamaParseClient(
        api_key=resolved_settings.llama_cloud_api_key,
        parsing_instruction=FACTUALITY_PARSE_INSTRUCTION,
    )
    factcheck_client = FactCheckClient(
        hf_token=resolved_settings.huggingface_token,
        space_name=resolved_settings.fact_check_space,
        api_name=resolved_settings.factuality_api_name,
    )
    factuality = CheckFactualityUseCase(
        parser_client=parser_client,
        factcheck_client=factcheck_client,
    )

    feedback_client = OpenAISlideFeedbackClient(
        api_key=resolved_settings.openai_api_key,
        model_name=resolved_settings.openai_model_name,
    )
    feedback = GenerateSlideFeedbackUseCase(
        openai_client=feedback_client,
        prompt=SLIDE_FEEDBACK_PROMPT,
    )

    process_slide_deck = ProcessSlideDeckUseCase(
        predict_views_use_case=predict_views,
        factuality_use_case=factuality,
    )

    return AppContainer(
        settings=resolved_settings,
        process_slide_deck_use_case=process_slide_deck,
        generate_slide_feedback_use_case=feedback,
    )

