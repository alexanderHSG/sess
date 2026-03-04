# Architecture

This project now uses a layered architecture with explicit boundaries.

## 1. Layers

### Interfaces (`src/sess/interfaces`)

- Gradio UI composition (`gradio_ui.py`)
- Output renderers (`renderers/quality_dimension_renderer.py`)

Responsibilities:

- Collect user input
- Trigger use cases
- Render results/errors for users

### Application (`src/sess/application`)

- Use cases:
  - `predict_views.py`
  - `check_factuality.py`
  - `generate_slide_feedback.py`
  - `process_slide_deck.py`

Responsibilities:

- Orchestrate workflows
- Coordinate concurrency (`asyncio`)
- Keep business flow independent from UI details

### Domain (`src/sess/domain`)

- Typed models (`models.py`)
- Constants (`constants.py`)
- Exceptions (`errors.py`)
- Pure services:
  - feature extraction
  - quality aggregation
  - PDF rendering

Responsibilities:

- Core business concepts
- Deterministic logic without infra concerns

### Infrastructure (`src/sess/infrastructure`)

- DB repository (`db/sqlite_repo.py`)
- Model loading (`ml/model_registry.py`)
- External API clients:
  - OpenAI
  - LlamaParse
  - Hugging Face fact-check endpoint

Responsibilities:

- Talk to external systems
- Isolate file/network dependencies

### Config + Bootstrap

- Typed settings: `src/sess/config/settings.py`
- Composition root: `src/sess/bootstrap.py`

Responsibilities:

- Read env vars/paths
- Build dependency graph once

## 2. Runtime Flow

1. `app.py` loads `src` and calls `build_container()`.
2. `create_demo(container)` builds the Gradio app with injected use cases.
3. User uploads PDF and clicks process.
4. `ProcessSlideDeckUseCase` runs in parallel:
   - `PredictViewsUseCase`
   - `CheckFactualityUseCase`
5. UI receives:
   - Predicted view card HTML
   - Quality dimension HTML
   - Factuality markdown table
6. User requests single-slide feedback.
7. `GenerateSlideFeedbackUseCase` calls OpenAI adapter and returns critique text.

## 3. Professionalization Decisions

- Thin entrypoint (`app.py`) instead of monolithic logic.
- Typed request/response models for use-case boundaries.
- Singleton `ModelRegistry` so large artifacts are loaded once.
- Explicit error types for cleaner handling.
- Logging configured centrally.
- Testable modules with adapter boundaries.

## 4. Compatibility

Legacy module files remain as wrappers:

- `featureExtractorPDF.py`
- `gradioQualityDimensionWrapper.py`
- `PDFparser.py`

They forward to `src/sess` implementations for backward compatibility.

## 5. CI and Quality Gates

CI workflow (`.github/workflows/ci.yml`) runs:

- `ruff check .`
- `mypy src`
- `pytest -q`

