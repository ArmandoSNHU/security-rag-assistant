"""FastAPI service exposing the RAG index over HTTP.

Run:  uvicorn secrag.server:app --reload
The index path comes from SECRAG_DB (default data/index); build it first with the CLI.
"""
from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .factory import build_engine
from .store import VectorStore

app = FastAPI(title="secrag", description="Local security & compliance RAG assistant")

_DB = os.environ.get("SECRAG_DB", "data/index")
_engine = None


class Query(BaseModel):
    question: str
    k: int = 4


def _get_engine():
    global _engine
    if _engine is None:
        try:
            store = VectorStore.load(_DB)
        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Index not found at {_DB}. Build it: python -m secrag.cli ingest corpus --db {_DB}",
            ) from exc
        _engine = build_engine(store=store)
    return _engine


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "mode": os.environ.get("SECRAG_MODE", "offline"), "db": _DB}


@app.post("/query")
def query(q: Query) -> dict:
    if not q.question.strip():
        raise HTTPException(status_code=422, detail="question must not be empty")
    return _get_engine().answer(q.question, k=q.k)
