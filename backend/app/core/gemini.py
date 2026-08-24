"""Gemini LLM & embedding provider (default). Full implementation lands in Phase 2.

This module is intentionally a thin placeholder: it validates that an API key is
configured and raises a clear error if a Phase 2 code path is reached before the
implementation is complete. This keeps Phase 1 runnable without a real LLM call.
"""
from app.config import settings


class GeminiLLM:
    name = "gemini"

    def __init__(self) -> None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Configure it in .env to use the Gemini LLM provider."
            )

    async def chat(self, system: str, user: str, temperature: float = 0.2) -> str:  # pragma: no cover
        raise NotImplementedError("Gemini LLM chat is implemented in Phase 2 (Koreum Vault/RAG).")


class GeminiEmbeddings:
    name = "gemini"

    def __init__(self) -> None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Configure it in .env to use Gemini embeddings."
            )

    @property
    def dimension(self) -> int:  # pragma: no cover
        return 768

    async def embed(self, texts: list[str]) -> list[list[float]]:  # pragma: no cover
        raise NotImplementedError("Gemini embeddings are implemented in Phase 2 (Koreum Vault/RAG).")
