"""A small in-memory vector store with cosine search and JSON/npz persistence."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np


class VectorStore:
    """Holds normalized vectors and their records; searches by cosine similarity.

    Vectors are expected to arrive L2-normalized (both embedding backends do
    this), so a dot product is the cosine similarity.
    """

    def __init__(self) -> None:
        self.vectors: np.ndarray | None = None
        self.records: List[Dict] = []

    def add(self, vectors, records: List[Dict]) -> None:
        vectors = np.asarray(vectors, dtype=np.float32)
        if vectors.shape[0] != len(records):
            raise ValueError("vectors and records length mismatch")
        self.vectors = vectors if self.vectors is None else np.vstack([self.vectors, vectors])
        self.records.extend(records)

    def search(self, query_vec, k: int = 4) -> List[Tuple[Dict, float]]:
        if self.vectors is None or not self.records:
            return []
        q = np.asarray(query_vec, dtype=np.float32).ravel()
        norm = float(np.linalg.norm(q))
        if norm:
            q = q / norm
        sims = self.vectors @ q
        k = min(k, len(self.records))
        top = np.argsort(-sims)[:k]
        return [(self.records[i], float(sims[i])) for i in top]

    def __len__(self) -> int:
        return len(self.records)

    def save(self, path: str) -> None:
        base = Path(path)
        base.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(base.with_suffix(".npz"), vectors=self.vectors)
        base.with_suffix(".json").write_text(
            json.dumps(self.records, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    @classmethod
    def load(cls, path: str) -> "VectorStore":
        base = Path(path)
        store = cls()
        store.records = json.loads(base.with_suffix(".json").read_text(encoding="utf-8"))
        with np.load(base.with_suffix(".npz")) as data:
            store.vectors = data["vectors"]
        return store
