"""Answer backends.

`ExtractiveLLM` needs no model — it returns the most relevant retrieved passage
with its citation, so the pipeline gives a useful answer offline. `OllamaLLM`
synthesizes a cited answer from a local model when one is available.
"""
from __future__ import annotations

from typing import List

_PROMPT = """You are a security and compliance assistant. Answer the question using ONLY the numbered sources below. Cite each claim with its source number in square brackets, e.g. [2]. If the sources do not contain the answer, say so plainly.

Sources:
{context}

Question: {question}
Answer:"""


class ExtractiveLLM:
    """No-model fallback: surface the top source verbatim, cited."""

    def generate(self, question: str, contexts: List[str]) -> str:
        if not contexts:
            return "No relevant information was found in the corpus for that question."
        top = contexts[0].strip()
        return (
            f"Based on the most relevant source [1]:\n\n{top}\n\n"
            "(Extractive answer. Start a local Ollama model and use OllamaLLM for a "
            "synthesized, multi-source response.)"
        )


class OllamaLLM:
    """Generative, cited answers from a local Ollama model (default llama3.2)."""

    def __init__(self, model: str = "llama3.2", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host.rstrip("/")

    def generate(self, question: str, contexts: List[str]) -> str:
        import requests  # lazy import keeps the offline path dependency-free

        context = "\n\n".join(f"[{i + 1}] {c}" for i, c in enumerate(contexts))
        prompt = _PROMPT.format(context=context, question=question)
        resp = requests.post(
            f"{self.host}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["response"].strip()
