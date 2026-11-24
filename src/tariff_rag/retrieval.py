"""Finds the chunks most likely to answer a question.

Every retriever takes the same chunks, answers `search(query, k)` with scored hits, best first,
and has a `name` for reports. That shared shape lets the eval compare them on equal terms and lets
the answering step stay unaware of which one it is using.
"""

import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from rank_bm25 import BM25Okapi

from tariff_rag.chunking import Chunk


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float


class Retriever(Protocol):
    name: str

    def search(self, query: str, k: int = 3) -> list[Hit]: ...


def top_k(chunks: Sequence[Chunk], scores: Sequence[float], k: int) -> list[Hit]:
    """Best k hits by score. Ties keep chunk order, so results are the same on every run."""
    order = sorted(range(len(chunks)), key=lambda i: (-scores[i], i))
    return [Hit(chunks[i], float(scores[i])) for i in order[:k]]


# Words that appear in almost every question and carry no fee information.
STOPWORDS = frozenset(
    "a an and are at be by can do does for from how i if in is it me much my of on or per "
    "the this to what when which with you your".split()
)
TOKEN = re.compile(r"\d[\d,]*(?:\.\d+)?|[a-z]+")


def tokenize(text: str) -> list[str]:
    """Lowercase words and numbers, with thousands separators removed.

    "Ksh.1,500" becomes ["ksh", "1500"], so a question that says "1500" or "1,500" matches.
    """
    tokens = TOKEN.findall(text.lower())
    return [t.replace(",", "") for t in tokens if t not in STOPWORDS]


class BM25Retriever:
    """Keyword ranking with BM25 (Okapi). Strong on exact terms like "Pesalink" or "RTGS",
    blind to synonyms the poster does not use."""

    name = "bm25"

    def __init__(self, chunks: Sequence[Chunk]):
        self.chunks = list(chunks)
        self._index = BM25Okapi([tokenize(c.text) for c in self.chunks])

    def search(self, query: str, k: int = 3) -> list[Hit]:
        tokens = tokenize(query)
        if not tokens:
            return []
        return top_k(self.chunks, self._index.get_scores(tokens), k)
