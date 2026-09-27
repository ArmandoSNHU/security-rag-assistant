"""Embedding backends.

`HashingEmbeddings` needs no model or network — a hashed, L2-normalized
bag-of-words that makes lexical retrieval work anywhere. `OllamaEmbeddings`
calls a local Ollama server for semantic vectors when you want quality.
"""
from __future__ import annotations

import hashlib
import re
from typing import List

import numpy as np

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> List[str]:
    return _TOKEN.findall(text.lower())


class HashingEmbeddings:
    """Deterministic, offline embeddings via the hashing trick.

    Each token increments one dimension chosen by its hash; the vector is
    L2-normalized so a dot product is cosine similarity. No model, no network.
    """

    def __init__(self, dim: int = 512):
        self.dim = dim

    def embed(self, texts: List[str]) -> np.ndarray:
        vecs = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, text in enumerate(texts):
            for tok in _tokenize(text):
                h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
                vecs[i, h % self.dim] += 1.0
            norm = float(np.linalg.norm(vecs[i]))
            if norm:
                vecs[i] /= norm
        return vecs


class OllamaEmbeddings:
    """Semantic embeddings from a local Ollama server (default nomic-embed-text)."""

    def __init__(self, model: str = "nomic-embed-text", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host.rstrip("/")

    def embed(self, texts: List[str]) -> np.ndarray:
        import requests  # imported lazily so the offline path needs no dependency

        out = []
        for text in texts:
            resp = requests.post(
                f"{self.host}/api/embeddings",
                json={"model": self.model, "prompt": text},
                timeout=60,
            )
            resp.raise_for_status()
            out.append(resp.json()["embedding"])
        arr = np.asarray(out, dtype=np.float32)
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return arr / norms
