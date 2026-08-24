"""Vector store abstraction (Phase 2 implements pgvector + swappable backends).

Per spec §7: do not tightly couple RAG to one vector DB. The protocol below lets
Vault/RAG code depend on `VectorStore` and swap pgvector for Pinecone, Qdrant, etc.
"""
from typing import Protocol, runtime_checkable


@runtime_checkable
class VectorStore(Protocol):
    async def add(self, ids: list[str], vectors: list[list[float]], metadata: list[dict]) -> None:
        ...

    async def search(self, query: list[float], top_k: int, filters: dict) -> list[dict]:
        ...

    async def delete(self, ids: list[str]) -> None:
        ...


def get_vector_store() -> VectorStore:  # pragma: no cover - Phase 2
    from app.core.pgvector_store import PgVectorStore

    return PgVectorStore()
