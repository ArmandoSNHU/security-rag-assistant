"""secrag — a local-first retrieval-augmented assistant for security & compliance docs.

Runs with zero external models by default (hashing embeddings + extractive answers)
and upgrades to Ollama (nomic-embed-text + a local LLM) for semantic, generative answers.
"""

__version__ = "0.1.0"
