# Contributing Guidelines

## Philosophy
- Code is law. No exceptions.
- Every line must serve a purpose. No dead code, no TODOs, no trash.
- Maintainability, testability, and clarity are non-negotiable.

## Project Structure
- All business logic in `shadowstep/`.
- Tests in `tests/`, mirroring the main structure.
- No empty files or directories. Remove dead weight immediately.
- Scripts and tools in `tools/` if needed.

## Code Style
- Full type annotations everywhere (`from typing import ...`).
- Google style docstrings for all public classes, methods, and modules.
- All comments in English, explaining logic blocks.
- Public methods: scenario only, no logic, only private method calls.
- Private methods: all implementation details.
- No nested logic in public methods (no if, for, while, match, etc.).
- Logging required: at method start and before each step.
- Meaningful names, no transliteration, no abbreviations.
- Constants in ALL_CAPS.

## Testing
- Use `pytest` only.
- 100% coverage for all public methods and classes.
- At least one positive and one negative test per method.
- Fixtures in `conftest.py`.
- Test structure mirrors main logic.

## CI/CD
- Linting (pylint, flake8) on every push.
- Tests and coverage (pytest-cov) on every push. Minimum 80% coverage.
- Build and publish automation for releases.

## Documentation
- `README.md`: description, install, usage, examples.
- `docs/`: architecture, diagrams, FAQ.

## Automation
- Use pre-commit hooks for linting, formatting, and tests.
- Track technical debt in a dedicated file.

## Enforcement
- No code merges without review.
- Standards are not optional. Break them — refactor immediately. 
