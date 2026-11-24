"""Turns text into vectors for similarity search.

An Embedder returns L2-normalised vectors, so the dot product of two vectors is their cosine
similarity. The retriever relies on that and does not normalise again.
"""

import os
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

import numpy as np

DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"
# The bge model card asks for this instruction in front of short queries (not documents).
BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
CACHE_DIR = Path(os.environ.get("FASTEMBED_CACHE_PATH", Path.home() / ".cache" / "fastembed"))


class Embedder(Protocol):
    name: str
    max_tokens: int | None  # longest input the model reads in full; None if unlimited

    def embed_documents(self, texts: Sequence[str]) -> np.ndarray: ...  # shape (n, dim)

    def embed_query(self, text: str) -> np.ndarray: ...  # shape (dim,)

    def count_tokens(self, text: str) -> int: ...


def normalise(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=-1, keepdims=True)
    return vectors / np.where(norms == 0, 1, norms)


class FastEmbedder:
    """A local ONNX model through fastembed. No API key, no torch, runs on CPU.

    The model (about 130 MB) downloads on first use into CACHE_DIR.
    """

    max_tokens = 512

    def __init__(self, model: str = DEFAULT_MODEL, query_prefix: str = BGE_QUERY_PREFIX):
        from fastembed import TextEmbedding  # imported here so tests do not load the model

        self._model = TextEmbedding(model, cache_dir=str(CACHE_DIR))
        self._tokenizer = self._model.model.tokenizer
        self._tokenizer.no_truncation()
        self.query_prefix = query_prefix
        self.name = model if query_prefix else f"{model} (no query prefix)"

    def embed_documents(self, texts: Sequence[str]) -> np.ndarray:
        return normalise(np.array(list(self._model.embed(list(texts)))))

    def embed_query(self, text: str) -> np.ndarray:
        return normalise(np.array(list(self._model.embed([self.query_prefix + text])))[0])

    def count_tokens(self, text: str) -> int:
        return len(self._tokenizer.encode(text).ids)
