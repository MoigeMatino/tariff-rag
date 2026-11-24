"""Vector retrieval tests with a small fake embedder, so they run without downloading a model.

The fake turns text into a hashed bag of words. It is crude, but it lets the tests check the
retriever's own logic: ranking by cosine similarity, the token-limit guard and empty queries.
"""

import hashlib

import numpy as np
import pytest

from tariff_rag.chunking import chunk_transcript
from tariff_rag.embeddings import normalise
from tariff_rag.retrieval import VectorRetriever, tokenize
from tariff_rag.transcript import load_transcript

CHUNKS = chunk_transcript(load_transcript())


class FakeEmbedder:
    name = "fake"

    def __init__(self, dim: int = 256, max_tokens: int | None = None):
        self.dim = dim
        self.max_tokens = max_tokens

    def _vector(self, text: str) -> np.ndarray:
        v = np.zeros(self.dim)
        for token in tokenize(text):
            v[int(hashlib.md5(token.encode()).hexdigest(), 16) % self.dim] += 1
        return v

    def embed_documents(self, texts):
        return normalise(np.array([self._vector(t) for t in texts]))

    def embed_query(self, text):
        return normalise(self._vector(text))

    def count_tokens(self, text):
        return len(text.split())


def test_normalise_gives_unit_vectors_and_leaves_zero_vectors_alone():
    out = normalise(np.array([[3.0, 4.0], [0.0, 0.0]]))
    assert np.allclose(out, [[0.6, 0.8], [0.0, 0.0]])


def test_vector_search_ranks_by_cosine_similarity():
    hits = VectorRetriever(CHUNKS, FakeEmbedder()).search("Pesalink Transactions", k=3)
    assert hits[0].chunk.section_id == "agency-banking"
    assert [h.score for h in hits] == sorted((h.score for h in hits), reverse=True)
    assert all(-1.0 <= h.score <= 1.0 + 1e-9 for h in hits)


def test_identical_text_scores_one():
    retriever = VectorRetriever(CHUNKS, FakeEmbedder())
    hits = retriever.search(CHUNKS[4].text, k=1)
    assert hits[0].chunk.id == CHUNKS[4].id
    assert hits[0].score == pytest.approx(1.0)


def test_chunks_longer_than_the_model_window_are_refused():
    with pytest.raises(ValueError, match="longer than 20 tokens"):
        VectorRetriever(CHUNKS, FakeEmbedder(max_tokens=20))


def test_blank_query_returns_nothing():
    assert VectorRetriever(CHUNKS, FakeEmbedder()).search("   ") == []
