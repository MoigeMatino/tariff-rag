import pytest

from tariff_rag.chunking import chunk_transcript
from tariff_rag.evaluation import (
    first_relevant_rank,
    hit_at_k,
    mean_reciprocal_rank,
    random_hit_at_k,
)
from tariff_rag.retrieval import Hit
from tariff_rag.transcript import load_transcript

CHUNKS = {c.id: c for c in chunk_transcript(load_transcript())}


def hits(*ids):
    return [Hit(CHUNKS[i], 1.0) for i in ids]


def test_first_relevant_rank_matches_on_section():
    ranked = hits("card-fees-01", "agency-banking-02", "agency-banking-01")
    assert first_relevant_rank(ranked, "agency-banking") == 2
    assert first_relevant_rank(ranked, "yea-account") is None


def test_hit_at_k_and_mrr():
    ranks = [1, 2, None, 4]
    assert hit_at_k(ranks, 1) == 0.25
    assert hit_at_k(ranks, 3) == 0.5
    assert mean_reciprocal_rank(ranks) == pytest.approx((1 + 0.5 + 0 + 0.25) / 4)


def test_random_baseline():
    assert random_hit_at_k(1, 10, 1) == pytest.approx(0.1)
    assert random_hit_at_k(2, 11, 3) == pytest.approx(1 - comb_ratio(9, 11, 3))
    assert random_hit_at_k(3, 3, 5) == 1.0


def comb_ratio(a, b, k):
    from math import comb

    return comb(a, k) / comb(b, k)
