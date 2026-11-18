.PHONY: install lint test verify-source inspect check

install:
	uv sync

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest -q

verify-source:
	uv run python scripts/verify_source.py

inspect: verify-source
	uv run python scripts/inspect_pdf.py

check: lint test
