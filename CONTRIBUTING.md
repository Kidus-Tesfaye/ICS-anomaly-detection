# Contributing

This is primarily a single-author research portfolio project, but issues and PRs are welcome.

## Development setup

```bash
uv sync --extra dev        # or: pip install -e ".[dev]"
pre-commit install
```

## Ground rules

- All code lives in `src/ics_anomaly/`; notebooks are exploratory only and must not be imported.
- Every experiment is driven by a YAML config in `configs/` — no hardcoded hyperparameters.
- Any change touching data splitting, scaling, or thresholding must keep the leakage tests in
  `tests/data_validation/` passing, and new leakage surfaces need new tests.
- Run `ruff check .`, `ruff format .`, `mypy`, and `pytest` before pushing (CI enforces all four).
- Never commit dataset files — raw data is license-restricted (see `docs/data_card.md`).
