"""Load a corpus directory of text/markdown files into Documents."""
from __future__ import annotations

from pathlib import Path
from typing import List

from .rag import Document

_EXTS = {".md", ".txt", ".markdown"}


def load_corpus(directory: str) -> List[Document]:
    """Read every .md/.txt file under `directory` into a Document.

    `source` is the path relative to the corpus root, so citations stay readable.
    """
    root = Path(directory)
    if not root.is_dir():
        raise NotADirectoryError(f"corpus directory not found: {directory}")
    docs: List[Document] = []
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() in _EXTS and path.is_file():
            text = path.read_text(encoding="utf-8").strip()
            if text:
                docs.append(Document(text=text, source=str(path.relative_to(root)).replace("\\", "/")))
    return docs
