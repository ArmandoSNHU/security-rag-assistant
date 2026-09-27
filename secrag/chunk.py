"""Split documents into overlapping word-window chunks for retrieval."""
from __future__ import annotations

from typing import List


def chunk_text(text: str, size: int = 120, overlap: int = 20) -> List[str]:
    """Break text into chunks of ~`size` words with `overlap` words of carry-over.

    Overlap keeps a sentence that straddles a boundary retrievable from either
    chunk. Returns a single chunk when the text is shorter than `size`.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    if not 0 <= overlap < size:
        raise ValueError("overlap must be >= 0 and < size")

    words = text.split()
    if not words:
        return []
    if len(words) <= size:
        return [" ".join(words)]

    chunks: List[str] = []
    step = size - overlap
    i = 0
    while i < len(words):
        chunks.append(" ".join(words[i : i + size]))
        if i + size >= len(words):
            break
        i += step
    return chunks
