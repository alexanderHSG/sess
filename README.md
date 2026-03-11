# Slide Deck Evaluation Dashboard

AI-powered evaluation for presentation slide decks (PDF), including:

- View prediction using local ML artifacts
- Four quality dimensions (intrinsic, contextual, representational, reputational)
- Claim-level factuality checking
- Single-slide multimodal feedback

## Architecture at a glance

This repository now follows a layered structure:

- `interfaces` for Gradio UI and HTML rendering
- `application` for use-case orchestration
- `domain` for core models, constants, and business logic
- `infrastructure` for external adapters (DB, model loading, APIs)
- `config` for typed environment configuration

The app launcher (`app.py`) is now a thin composition root caller.

## Repository Structure

```text
.
|- app.py
|- requirements.txt
|- pyproject.toml
|- .env.example
|- CONTRIBUTING.md
|- docs/
|  |- ARCHITECTURE.md
|  |- CONFIGURATION.md
|  `- MODULES.md
|- src/
|  `- sess/
|     |- __main__.py
|     |- bootstrap.py
|     |- logging.py
|     |- config/
|     |- interfaces/
|     |- application/
|     |- domain/
|     `- infrastructure/
|- tests/
|  |- application/
|  |- config/
|  |- domain/
|  `- interfaces/
`- .github/workflows/ci.yml
```

## Quick Start

### 1) Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2) Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

or install as a package:

```bash
pip install -e .[dev]
```

### 3) Configure environment variables

Copy `.env.example` to `.env` and set values:

- `OpenAI`
- `LLAMA_CLOUD_API_KEY`
- `token`

### 4) Add required local artifacts

Place these files in repository root (or override via env vars):

- `all_talks.db` (with table `filtered_speakerdeckfeatures`)
- `mlp_ensemble.sav`
- `svr.sav`
- `rfr_embeddings.sav`

### 5) Run

```bash
python app.py
```

or:

```bash
python -m sess
```

## Quality Standards

This repo includes professional engineering scaffolding:

- Typed settings via `pydantic-settings`
- Singleton model registry
- Explicit exception hierarchy
- Structured logging
- Unit tests (`pytest`)
- Linting (`ruff`)
- Type checks (`mypy`)
- GitHub Actions CI

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Configuration](docs/CONFIGURATION.md)
- [Module Reference](docs/MODULES.md)
- [Contributing](CONTRIBUTING.md)

## Research Background

This tool is built on a research programme on AI-assisted slide evaluation. If you use this work, please consider citing the relevant papers below.

### System Design

> Alexander Meier, Roman Rietsche, Ivo Blohm (2024). **Towards Assisted Excellence: Designing an AI-Based System for Presentation Slide Evaluation.** In *Proceedings of the 19th International Conference on Design Science Research in Information Systems and Technology (DESRIST 2024)*, Trollhättan, Sweden, 3–5 June 2024.
> [https://www.alexandria.unisg.ch/handle/20.500.14171/120285](https://www.alexandria.unisg.ch/handle/20.500.14171/120285)

A full paper extending this work is forthcoming in the **HCI International 2026 Conference Proceedings** (Alexander Meier & Maren Cordts).

The figure below illustrates the interface and design features (DF) of the system:

![Interface and design features of the slide evaluation system](docs/Figure2.svg)

### Audience Reach Prediction Model

> Alexander Meier, Roman Rietsche, Ivo Blohm (2024). **An AI Approach for Predicting Audience Reach of Presentation Slides.** *ECIS 2024 Proceedings*, Short Paper 2322.
> [https://aisel.aisnet.org/ecis2024/track04_impactai/track04_impactai/9](https://aisel.aisnet.org/ecis2024/track04_impactai/track04_impactai/9)

## Security Note

Uploaded deck content can be sent to third-party services (OpenAI, LlamaParse, Hugging Face Space API). Only process sensitive material if this is acceptable under your compliance requirements.

