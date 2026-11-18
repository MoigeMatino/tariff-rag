# CLAUDE.md

Project rules for Claude Code. Read this before doing anything in this repo.

## What this is

A question-answering assistant over Co-op Bank Kenya's published tariff guide. It answers with
citations to the source, falls back when the answer is not in the guide, and is measured by an
automated evaluation. It is a portfolio project, so clarity of code and honesty of results matter
more than cleverness.

## Commands

- `make install` sets up the environment with uv.
- `make check` runs lint and tests. Run it before saying any task is done.
- `make verify-source` confirms the PDF in `data/raw/` matches the pinned edition.
- `make inspect` writes `reports/inspection.md` and page tiles for visual review.

## Hard rules

- Never read, print, or log the contents of `.env` or any API key.
- Never edit files under `eval/` that hold questions or expected answers, and never change the
  `sha256` in `data/source.json`. If a test or eval fails, fix the code or report the failure.
  Changing the answer key to make a run pass invalidates the whole evaluation.
- Do not add dependencies without asking first.
- Do not commit or push. The owner reviews and commits each step.

## Reporting results

When asked to run tests or the eval, reply in this format so it can be pasted into a review:

1. The exact command you ran.
2. Passed, failed and skipped counts.
3. For each failure: test name and the first assertion line, nothing more.
4. Any metrics table printed by the run, copied verbatim.
5. One line on what you think is wrong, marked as your opinion.
