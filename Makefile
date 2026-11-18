.PHONY: install lint test verify-source inspect crosscheck check

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

crosscheck: verify-source
	uv run python scripts/crosscheck_transcript.py

check: lint test
