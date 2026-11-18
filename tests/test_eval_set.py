"""Checks the shape of eval/questions.json. These tests read the answer key; they never edit it."""

import json
from pathlib import Path

from tariff_rag.chunking import chunk_section
from tariff_rag.transcript import load_transcript

ROOT = Path(__file__).resolve().parents[1]
EVAL = json.loads((ROOT / "eval" / "questions.json").read_text())
QUESTIONS = EVAL["questions"]


def test_eval_has_ten_answerable_and_five_fallback_questions():
    types = [q["type"] for q in QUESTIONS]
    assert types.count("answerable") == 10
    assert types.count("fallback") == 5


def test_question_ids_are_unique():
    ids = [q["id"] for q in QUESTIONS]
    assert len(ids) == len(set(ids))


def test_eval_targets_the_pinned_edition():
    source = json.loads((ROOT / "data" / "source.json").read_text())
    assert EVAL["edition_sha256"] == source["sha256"]


def test_answerable_questions_point_at_a_section_holding_the_expected_values():
    transcript = load_transcript()
    for q in (q for q in QUESTIONS if q["type"] == "answerable"):
        assert q["expected_page"] == 1, q["id"]
        assert q["expected_values"], q["id"]
        text = "\n".join(c.text for c in chunk_section(transcript.section(q["expected_section"])))
        for value in q["expected_values"]:
            assert value in text, f"{q['id']}: {value!r} not in {q['expected_section']}"


def test_fallback_questions_have_no_expected_source():
    for q in (q for q in QUESTIONS if q["type"] == "fallback"):
        assert q["expected_section"] is None and q["expected_page"] is None, q["id"]
        assert q["expected_values"] == [], q["id"]
