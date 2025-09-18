# Repository Guidelines

## Project Structure & Module Organization
The Typer CLI scaffold lives in `src/eggphy/cli.py` and will expand into the empty `agents/`, `io/`, `llm/`, and `utils/` packages; add new modules there rather than at repo root. Source code is packaged via `pyproject.toml`, so keep importable code under `src/eggphy/`. Primary data inputs sit in `data/` (e.g., `data/recipes.csv`), generated models land in `models/`, and derived artefacts belong in `output/`. Use `docs/` and `prompts/` for narrative material and prompt templates. Leave local virtual environments such as `eggphy-venv/` untracked.

## Build, Test, and Development Commands
Create an isolated environment, then install the CLI in editable mode with `python -m venv .venv && source .venv/bin/activate && pip install -e .`. The status stub exposes dataset counts via `eggphy status`. Discovery and review stubs append to `models/` for iterative runs: `eggphy discover --engine regex` and `eggphy review`. Regenerate wheels with `python -m build` if publishing packages. Keep scripts reproducible by recording any ad-hoc command sequences in `docs/`.

## Coding Style & Naming Conventions
Follow PEP 8: four-space indentation, snake_case for functions and variables, PascalCase for classes, and hyphen-free module names. Prefer explicit type hints and pydantic models when shaping structured data. Keep Typer command functions small and pure; push heavy lifting into helper modules. Run `python -m compileall src` before commits if you need a quick sanity check.

## Testing Guidelines
Tests live under `tests/` (create subpackages per feature) and should mirror the CLI command names. Use `pytest` with descriptive test function names like `test_discover_appends_record`. Seed fixtures from `data/` subsets rather than the full CSV to keep runs fast. Aim for coverage on new modules; add regression tests whenever a bug is fixed.

## Commit & Pull Request Guidelines
Commits follow the existing short imperative style (`Initial commit: ...`); keep them under 72 characters and scoped to one concern. Reference issue IDs in square brackets when applicable, and include result-oriented bodies. Pull requests should describe the change, list validation steps (commands run, data touched), and attach artefacts or screenshots when outputs in `output/` change. Request review once lint, tests, and CLI stubs all succeed.

## Security & Configuration Tips
Never store credentials in `config/`; rely on environment variables sourced in your shell. Treat `data/recipes.csv` as semi-public: redact sensitive annotations before sharing. Review generated artefacts for embedded tokens before committing, and prefer `.env` files ignored by git for local experimentation.
