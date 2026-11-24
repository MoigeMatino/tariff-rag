"""Retrieval metrics. Pure functions, so the numbers in reports can be unit-tested.

A retrieved chunk counts as relevant when it comes from the question's expected section. Scoring
by section rather than chunk id keeps the answer key valid when chunk boundaries change.
"""

from collections.abc import Sequence
from math import comb

from tariff_rag.retrieval import Hit


def first_relevant_rank(hits: Sequence[Hit], section_id: str) -> int | None:
    """1-based rank of the first hit from the expected section, or None if none is returned."""
    for rank, hit in enumerate(hits, 1):
        if hit.chunk.section_id == section_id:
            return rank
    return None


def hit_at_k(ranks: Sequence[int | None], k: int) -> float:
    """Share of questions with a relevant chunk in the top k."""
    return sum(r is not None and r <= k for r in ranks) / len(ranks)


def mean_reciprocal_rank(ranks: Sequence[int | None]) -> float:
    """Average of 1/rank, counting a miss as 0. Rewards ranking the right chunk first."""
    return sum(1 / r if r else 0.0 for r in ranks) / len(ranks)


def random_hit_at_k(n_relevant: int, n_total: int, k: int) -> float:
    """Chance a random ranking puts at least one of n_relevant chunks in the top k.

    With only a handful of chunks this is high, and every reported score should be read
    against it.
    """
    k = min(k, n_total)
    return 1 - comb(n_total - n_relevant, k) / comb(n_total, k)
