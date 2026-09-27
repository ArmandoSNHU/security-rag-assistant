"""Command-line interface: build an index from a corpus, then query it.

    python -m secrag.cli ingest corpus --db data/index
    python -m secrag.cli query "How is a technique mapped in MITRE ATT&CK?" --db data/index
"""
from __future__ import annotations

import argparse
import json
import sys

from .factory import build_engine
from .ingest import load_corpus
from .store import VectorStore


def _ingest(args: argparse.Namespace) -> int:
    engine = build_engine(args.mode)
    docs = load_corpus(args.corpus)
    if not docs:
        print(f"No documents found in {args.corpus}", file=sys.stderr)
        return 1
    n = engine.ingest(docs)
    engine.store.save(args.db)
    print(f"Ingested {len(docs)} document(s) -> {n} chunk(s). Index saved to {args.db}.(json|npz)")
    return 0


def _query(args: argparse.Namespace) -> int:
    store = VectorStore.load(args.db)
    engine = build_engine(args.mode, store=store)
    result = engine.answer(args.question, k=args.k)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    print(f"\nQ: {result['question']}\n")
    print(result["answer"])
    print("\nSources:")
    for c in result["citations"]:
        print(f"  [{c['n']}] {c['source']} (score {c['score']}) — {c['snippet'][:100]}...")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="secrag", description="Local security/compliance RAG assistant")
    parser.add_argument("--mode", choices=["offline", "ollama"], default=None,
                        help="backend (default: SECRAG_MODE env or 'offline')")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ing = sub.add_parser("ingest", help="build an index from a corpus directory")
    p_ing.add_argument("corpus")
    p_ing.add_argument("--db", default="data/index")
    p_ing.set_defaults(func=_ingest)

    p_q = sub.add_parser("query", help="answer a question against an index")
    p_q.add_argument("question")
    p_q.add_argument("--db", default="data/index")
    p_q.add_argument("--k", type=int, default=4)
    p_q.add_argument("--json", action="store_true")
    p_q.set_defaults(func=_query)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
