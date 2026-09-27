"""The retrieval-augmented pipeline: ingest documents, then answer with citations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .chunk import chunk_text
from .store import VectorStore


@dataclass
class Document:
    text: str
    source: str


class RagEngine:
    """Ties an embedding backend, a vector store, and an answer backend together."""

    def __init__(self, embeddings, llm, store: VectorStore | None = None,
                 chunk_size: int = 120, overlap: int = 20):
        self.embeddings = embeddings
        self.llm = llm
        self.store = store or VectorStore()
        self.chunk_size = chunk_size
        self.overlap = overlap

    def ingest(self, docs: List[Document]) -> int:
        records: List[Dict] = []
        for doc in docs:
            for idx, chunk in enumerate(chunk_text(doc.text, self.chunk_size, self.overlap)):
                records.append({
                    "id": f"{doc.source}#{idx}",
                    "text": chunk,
                    "source": doc.source,
                    "chunk": idx,
                })
        if not records:
            return 0
        vectors = self.embeddings.embed([r["text"] for r in records])
        self.store.add(vectors, records)
        return len(records)

    def answer(self, question: str, k: int = 4) -> Dict:
        query_vec = self.embeddings.embed([question])[0]
        hits = self.store.search(query_vec, k)
        citations = [
            {
                "n": i + 1,
                "source": rec["source"],
                "chunk": rec["chunk"],
                "score": round(score, 4),
                "snippet": rec["text"][:220],
            }
            for i, (rec, score) in enumerate(hits)
        ]
        contexts = [f"({rec['source']}) {rec['text']}" for rec, _ in hits]
        answer = self.llm.generate(question, contexts)
        return {"question": question, "answer": answer, "citations": citations}
