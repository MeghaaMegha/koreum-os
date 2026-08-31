"""Text chunking for RAG — splits documents into overlapping chunks."""
import re
from dataclasses import dataclass


@dataclass
class Chunk:
    index: int
    content: str


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[Chunk]:
    """Split text into overlapping chunks of approximately chunk_size characters.

    Tries to break on sentence/paragraph boundaries for cleaner chunks.
    """
    if not text or not text.strip():
        return []

    # Split into paragraphs first
    paragraphs = re.split(r"\n\s*\n", text)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    chunks: list[Chunk] = []
    current = ""
    idx = 0

    for para in paragraphs:
        if len(current) + len(para) > chunk_size and current:
            chunks.append(Chunk(index=idx, content=current.strip()))
            idx += 1
            current = para
        else:
            current = current + "\n\n" + para if current else para

        while len(current) > chunk_size + overlap:
            chunks.append(Chunk(index=idx, content=current[:chunk_size].strip()))
            idx += 1
            current = current[chunk_size - overlap:]

    if current.strip():
        chunks.append(Chunk(index=idx, content=current.strip()))
        idx += 1

    return chunks
