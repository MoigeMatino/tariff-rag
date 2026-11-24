"""Checks the shape of the eval sets. These tests read the answer keys; they never edit them."""

import json
import re
from pathlib import Path

import pytest

from tariff_rag.chunking import chunk_section
from tariff_rag.transcript import load_transcript

ROOT = Path(__file__).resolve().parents[1]
EVAL_FILES = ["questions.json", "customer_questions.json"]


def load(name):
    return json.loads((ROOT / "eval" / name).read_text())


def test_main_set_has_ten_answerable_and_five_fallback_questions():
    types = [q["type"] for q in load("questions.json")["questions"]]
    assert types.count("answerable") == 10
    assert types.count("fallback") == 5


def test_customer_set_has_fifteen_answerable_questions():
    types = [q["type"] for q in load("customer_questions.json")["questions"]]
    assert types == ["answerable"] * 15


def test_question_ids_are_unique_across_all_sets():
    ids = [q["id"] for name in EVAL_FILES for q in load(name)["questions"]]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("name", EVAL_FILES)
def test_eval_targets_the_pinned_edition(name):
    source = json.loads((ROOT / "data" / "source.json").read_text())
    assert load(name)["edition_sha256"] == source["sha256"]


@pytest.mark.parametrize("name", EVAL_FILES)
def test_answerable_questions_point_at_a_section_holding_the_expected_values(name):
    transcript = load_transcript()
    for q in (q for q in load(name)["questions"] if q["type"] == "answerable"):
        assert q["expected_page"] == 1, q["id"]
        assert q["expected_values"], q["id"]
        text = "\n".join(c.text for c in chunk_section(transcript.section(q["expected_section"])))
        for value in q["expected_values"]:
            assert value in text, f"{q['id']}: {value!r} not in {q['expected_section']}"


def test_fallback_questions_have_no_expected_source():
    for q in (q for q in load("questions.json")["questions"] if q["type"] == "fallback"):
        assert q["expected_section"] is None and q["expected_page"] is None, q["id"]
        assert q["expected_values"] == [], q["id"]


def test_customer_questions_do_not_use_the_terms_they_avoid():
    for q in load("customer_questions.json")["questions"]:
        assert q["avoids"], q["id"]
        for term in q["avoids"]:
            # Whole words only: "euro" does not count as using "EUR".
            pattern = rf"\b{re.escape(term)}\b"
            assert not re.search(pattern, q["question"], re.IGNORECASE), f"{q['id']} uses {term!r}"
