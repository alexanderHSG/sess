# Module Reference

Current module layout after architecture refactor.

## Entrypoints

- `app.py`
  - Thin launcher, adds `src` to `sys.path`, builds container, launches Gradio.
- `src/sess/__main__.py`
  - Supports `python -m sess`.

## Composition and Config

- `src/sess/bootstrap.py`
  - Builds all dependencies and use-case instances.
- `src/sess/config/settings.py`
  - Typed settings model (`pydantic-settings`) with env aliases and defaults.
- `src/sess/logging.py`
  - Logging setup helpers.

## Domain

- `src/sess/domain/models.py`
  - Dataclasses for requests/results and factuality rows.
- `src/sess/domain/constants.py`
  - Categories, authors, prompts, parser instructions.
- `src/sess/domain/errors.py`
  - Application-specific exception hierarchy.
- `src/sess/domain/services/feature_extractor.py`
  - PDF-to-features extraction.
- `src/sess/domain/services/quality_scoring.py`
  - LIME training prep, explainer provider, quality score aggregation.
- `src/sess/domain/services/pdf_rendering.py`
  - PDF page image rendering for gallery display.

## Application use cases

- `src/sess/application/use_cases/predict_views.py`
  - Predicts views and computes quality dimension outputs.
- `src/sess/application/use_cases/check_factuality.py`
  - Parses deck content and runs fact-check workflow.
- `src/sess/application/use_cases/generate_slide_feedback.py`
  - Generates targeted feedback for selected slide image.
- `src/sess/application/use_cases/process_slide_deck.py`
  - Orchestrates deck processing in parallel.

## Infrastructure

- `src/sess/infrastructure/db/sqlite_repo.py`
  - Loads training rows from SQLite.
- `src/sess/infrastructure/ml/model_registry.py`
  - Singleton lazy loader for `.sav` models.
- `src/sess/infrastructure/clients/openai_client.py`
  - OpenAI image+text request adapter.
- `src/sess/infrastructure/clients/llama_parse_client.py`
  - LlamaParse adapter for markdown parsing.
- `src/sess/infrastructure/clients/factcheck_client.py`
  - Hugging Face Space API adapter for factuality.

## Interface adapters

- `src/sess/interfaces/gradio_ui.py`
  - UI layout and event wiring.
- `src/sess/interfaces/renderers/quality_dimension_renderer.py`
  - Gradient and HTML rendering for quality and view outputs.

## Legacy compatibility wrappers

- `featureExtractorPDF.py`
- `gradioQualityDimensionWrapper.py`
- `PDFparser.py`

These forward to new `src/sess` modules.

