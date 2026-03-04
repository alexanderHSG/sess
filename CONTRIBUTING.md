# Contributing

## Development setup

1. Create a virtual environment.
2. Install package with dev tools.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -e .[dev]
```

3. Copy `.env.example` to `.env` and set credentials.
4. Ensure local artifacts exist (`all_talks.db`, `mlp_ensemble.sav`, `svr.sav`, `rfr_embeddings.sav`).

## Local quality checks

Run before opening a PR:

```bash
ruff check .
mypy src
pytest -q
```

## Branching and commits

- Use small focused branches (`feature/...`, `fix/...`, `docs/...`).
- Keep commits atomic.
- Include clear behavior-oriented commit messages.

## Architecture rules

- Keep UI concerns in `interfaces`.
- Keep orchestration in `application/use_cases`.
- Keep core logic in `domain`.
- Keep external I/O in `infrastructure`.
- Add/update typed models when changing use-case boundaries.

## Pull request checklist

1. Tests pass locally.
2. Lint/type checks pass.
3. Docs are updated (`README.md` and/or `docs/`).
4. No secrets or private keys are committed.
5. PR description includes impact summary and verification steps.

