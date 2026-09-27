"""Pick embedding + answer backends. Offline by default; Ollama when asked."""
from __future__ import annotations

import os

from .embeddings import HashingEmbeddings, OllamaEmbeddings
from .llm import ExtractiveLLM, OllamaLLM
from .rag import RagEngine
from .store import VectorStore


def build_engine(mode: str | None = None, store: VectorStore | None = None) -> RagEngine:
    """Build a RagEngine.

    mode "offline" (default): HashingEmbeddings + ExtractiveLLM — no model, no network.
    mode "ollama": OllamaEmbeddings + OllamaLLM against a local Ollama server.
    When mode is None it reads SECRAG_MODE, falling back to "offline".
    """
    mode = (mode or os.environ.get("SECRAG_MODE", "offline")).lower()
    if mode == "ollama":
        host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        embed_model = os.environ.get("SECRAG_EMBED_MODEL", "nomic-embed-text")
        gen_model = os.environ.get("SECRAG_LLM_MODEL", "llama3.2")
        return RagEngine(
            OllamaEmbeddings(model=embed_model, host=host),
            OllamaLLM(model=gen_model, host=host),
            store=store,
        )
    if mode != "offline":
        raise ValueError(f"unknown SECRAG_MODE: {mode!r} (use 'offline' or 'ollama')")
    return RagEngine(HashingEmbeddings(), ExtractiveLLM(), store=store)
