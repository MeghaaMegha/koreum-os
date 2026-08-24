"""pgvector-backed VectorStore implementation (Phase 2)."""
from app.core.vector_store import VectorStore


class PgVectorStore(VectorStore):  # pragma: no cover - Phase 2
    async def add(self, ids, vectors, metadata):
        raise NotImplementedError("Implemented in Phase 2 (Koreum Vault).")

    async def search(self, query, top_k, filters):
        raise NotImplementedError("Implemented in Phase 2 (Koreum Vault).")

    async def delete(self, ids):
        raise NotImplementedError("Implemented in Phase 2 (Koreum Vault).")
