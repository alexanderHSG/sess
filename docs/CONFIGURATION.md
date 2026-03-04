# Configuration

This file describes runtime configuration for local execution and deployment.

## 1. Python and dependencies

- Python: `>=3.10`
- Runtime deps: `requirements.txt`
- Package metadata + dev tooling: `pyproject.toml`

Install runtime:

```bash
pip install -r requirements.txt
```

Install package + dev tools:

```bash
pip install -e .[dev]
```

## 2. Environment variables

The app reads settings via `pydantic-settings` from env vars (and optional `.env`).

Required:

- `OpenAI`
- `LLAMA_CLOUD_API_KEY`
- `token`

Optional overrides:

- `LOG_LEVEL` (default: `INFO`)
- `FACT_CHECK_SPACE` (default: `IWIHSG/fact_check`)
- `FACT_CHECK_API_NAME` (default: `/factuality_check`)
- `OPENAI_MODEL_NAME` (default: `gpt-4o`)
- `ALL_TALKS_DB` (default: `all_talks.db`)
- `DB_TABLE_NAME` (default: `filtered_speakerdeckfeatures`)
- `MLP_MODEL_PATH` (default: `mlp_ensemble.sav`)
- `SVR_MODEL_PATH` (default: `svr.sav`)
- `RFR_MODEL_PATH` (default: `rfr_embeddings.sav`)

Use `.env.example` as template.

## 3. Required local artifacts

The following files must be present (or overridden by env):

- `all_talks.db`
- `mlp_ensemble.sav`
- `svr.sav`
- `rfr_embeddings.sav`

DB requirements:

- table name must match `DB_TABLE_NAME`
- default expected table is `filtered_speakerdeckfeatures`

## 4. Launch modes

From repo root:

```bash
python app.py
```

or package entrypoint:

```bash
python -m sess
```

## 5. CI settings

Workflow: `.github/workflows/ci.yml`

Checks:

- Ruff lint
- Mypy type checks
- Pytest unit tests

