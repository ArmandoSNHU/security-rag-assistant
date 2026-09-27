# secrag — local security & compliance RAG assistant

[![tests](https://github.com/ArmandoSNHU/security-rag-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/ArmandoSNHU/security-rag-assistant/actions/workflows/ci.yml)
[![python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

Ask questions about security and compliance material — MITRE ATT&CK, the NIST CSF, GDPR, PCI DSS — and get an answer grounded in a cited source instead of a model's memory. Retrieval-augmented generation, built to run locally.

The point of the project is the retrieval contract: **every answer names the sources it came from, with a similarity score**, so a claim can be checked against the text it was drawn from.

## Runs with no model at all

The default backend needs no downloads and no network:

- **Embeddings** — a hashed, L2-normalized bag-of-words (`HashingEmbeddings`). Lexical, deterministic, instant.
- **Answers** — `ExtractiveLLM` returns the top retrieved passage with its citation.

That means you can clone it and get cited retrieval working in one command. Point it at a real model when you want semantic search and synthesized answers.

## Quickstart (offline, zero models)

```bash
pip install numpy
python -m secrag.cli ingest corpus --db data/index
python -m secrag.cli query "How long do I have to report a personal data breach under GDPR?"
```

Example (trimmed):

```
Q: How long do I have to report a personal data breach under GDPR?

Based on the most relevant source [1]:
GDPR ... the controller must notify its supervisory authority without undue delay
and, where feasible, within 72 hours of becoming aware of it ...

Sources:
  [1] gdpr.md (score 0.41) — GDPR is the European Union's data-protection law ...
```

## Semantic mode (local Ollama)

For real semantic retrieval and a synthesized, multi-source answer, run a local
[Ollama](https://ollama.com) server and switch modes:

```bash
ollama pull nomic-embed-text
ollama pull llama3.2

set SECRAG_MODE=ollama              # PowerShell: $env:SECRAG_MODE="ollama"
python -m secrag.cli ingest corpus --db data/index
python -m secrag.cli query "How does MITRE ATT&CK help a detection engineer?"
```

Nothing leaves the machine — embeddings and generation both run against the local server.

## HTTP API

```bash
pip install -r requirements.txt
python -m secrag.cli ingest corpus --db data/index
uvicorn secrag.server:app --port 8000
```

```bash
curl -s localhost:8000/query -H "content-type: application/json" \
     -d '{"question": "What must PCI DSS scans cover, and how often?"}'
```

Returns `{ "question", "answer", "citations": [ { "n", "source", "score", "snippet" } ] }`.

## How it works

```
corpus/*.md ──chunk──▶ embed ──▶ VectorStore (normalized vectors)
                                        │
question ──embed──▶ cosine top-k ──────┘──▶ contexts + citations ──▶ answer backend
```

1. **Chunk** each document into overlapping word windows so a straddling sentence stays retrievable.
2. **Embed** every chunk and the query with the same backend.
3. **Retrieve** the top-k chunks by cosine similarity.
4. **Answer** from those chunks, carrying each source through as a numbered citation.

Swapping backends is a one-line change (`secrag/factory.py`); the pipeline and the citation contract stay the same.

## Project structure

```text
secrag/
  chunk.py        overlapping word-window chunking
  embeddings.py   HashingEmbeddings (offline) + OllamaEmbeddings
  store.py        cosine VectorStore with save/load
  llm.py          ExtractiveLLM (offline) + OllamaLLM
  rag.py          RagEngine: ingest() and answer()
  ingest.py       load a corpus directory into Documents
  factory.py      choose the backend (offline | ollama)
  cli.py          ingest / query commands
  server.py       FastAPI service
corpus/           sample security & compliance notes (original summaries)
tests/            pytest suite (runs with no model)
```

## Tests

```bash
pip install numpy pytest
pytest -q
```

The suite covers chunking, cosine ranking, persistence round-trips, and the
retrieval contract (a security question resolves to the right source) — all
without a model, so CI stays fast and hermetic.

## Limitations

- The bundled corpus is a small set of hand-written summaries for demonstration; add your own `.md`/`.txt` files to `corpus/` and re-ingest.
- Offline embeddings are lexical, so they match on shared vocabulary rather than meaning. Use the Ollama mode for semantic questions.
- Generated answers are only as good as the retrieved sources; the citations are there so you can verify.
