# Contributing

## Data and secrets

- Do **not** commit datasets (Sharadar files, exported PDFs, vendor data dumps) to this repo.
- Do **not** commit secrets (API keys, tokens) or any personal data.

## Reproducibility

- Prefer changes that keep results reproducible (document assumptions, parameters, and dataset provenance).
- If you add a strategy:
  - add a YAML entry under `strategies/`
  - implement a corresponding `kind` in `src/paper_strategy_lab/strategies/builtins.py`
  - regenerate `docs/COVERAGE.md` via `python scripts/generate_coverage.py`

## Style

- Run `ruff` and `pyright` before opening a PR:
  - `uv sync --all-extras`
  - `.venv/bin/ruff check src`
  - `.venv/bin/pyright`

