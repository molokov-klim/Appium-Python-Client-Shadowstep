.PHONY: install-uv
install-uv:
	curl -LsSf https://astral.sh/uv/install.sh | sh

.PHONY: sync
sync:
	uv sync --dev

.PHONY: check
check:
	uv run ruff check .
	uv run pyright

.PHONY: unittest
unittest:
	PYTHONPATH=$(PWD) uv run pytest tests/test_unit -svl --log-cli-level INFO --tb=short --setup-show

.PHONY: integrationtest
integrationtest:
	PYTHONPATH=$(PWD) uv run pytest tests/test_integro -svl --log-cli-level INFO --tb=short --setup-show --reruns 2

.PHONY: test
test: unittest

.PHONY: lint
lint:
	uv run ruff check .

.PHONY: format
format:
	uv run ruff format .

.PHONY: typecheck
typecheck:
	uv run pyright

.PHONY: license-check
license-check:
	uv pip install pip-licenses
	uv run pip-licenses --fail-on="GPL" --fail-on="AGPL"

.PHONY: build
build:
	uv build

.PHONY: clean
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

.PHONY: help
help:
	@echo "Available commands:"
    @echo " make install-uv - Install the uv package manager"
    @echo " make sync - Synchronize dependencies"
    @echo " make check - Run lint and typecheck"
    @echo " make unittest - Run unit tests"
    @echo " make integrationtest - Run integration tests"
    @echo " make test - Run unit tests (alias)"
    @echo " make lint - Run ruff linter"
    @echo " make format - Format code with ruff"
    @echo " make typecheck - Run pyright type checker"
    @echo " make license-check - Verify dependency licenses"
    @echo " make build - Build the package"
    @echo " make clean - Remove build artifacts"
    @echo " make help - Show this help message"
