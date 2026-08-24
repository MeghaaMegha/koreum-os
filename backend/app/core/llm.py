"""LLM provider abstraction (Phase 2 wires implementations; Phase 1 defines the protocol).

Per spec §10: do not hard-code to one LLM provider. This protocol lets any module
depend on `LLMProvider` rather than a concrete vendor. A Gemini implementation is
registered by config (`LLM_PROVIDER=gemini`) and can be swapped for OpenAI,
Anthropic, or local models without touching call sites.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    name: str

    async def chat(self, system: str, user: str, temperature: float = 0.2) -> str:
        ...


@runtime_checkable
class EmbeddingProvider(Protocol):
    name: str

    async def embed(self, texts: list[str]) -> list[list[float]]:
        ...

    @property
    def dimension(self) -> int:
        ...


def get_llm_provider() -> LLMProvider:  # pragma: no cover - Phase 2
    from app.config import settings

    provider = settings.LLM_PROVIDER.lower()
    if provider == "gemini":
        from app.core.gemini import GeminiLLM

        return GeminiLLM()
    raise ValueError(f"Unknown LLM provider: {provider}")


def get_embedding_provider() -> EmbeddingProvider:  # pragma: no cover - Phase 2
    from app.config import settings

    provider = settings.EMBEDDING_PROVIDER.lower()
    if provider == "gemini":
        from app.core.gemini import GeminiEmbeddings

        return GeminiEmbeddings()
    raise ValueError(f"Unknown embedding provider: {provider}")
