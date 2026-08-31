"""Embedding provider abstraction — Gemini default."""
import logging
from typing import Protocol

from google import genai
from google.genai import types

from app.config import settings

logger = logging.getLogger("koreum")


class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> list[float]: ...
    def embed_batch(self, texts: list[str]) -> list[list[float]]: ...


class GeminiEmbeddingProvider:
    """Google Gemini gemini-embedding-001 (768 dims) via google-genai SDK."""

    def __init__(self, api_key: str):
        self._client = genai.Client(api_key=api_key)
        self._model = "gemini-embedding-001"

    def embed(self, text: str) -> list[float]:
        result = self._client.models.embed_content(
            model=self._model,
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=768,
            ),
        )
        return result.embeddings[0].values

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        result = self._client.models.embed_content(
            model=self._model,
            contents=texts,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=768,
            ),
        )
        return [e.values for e in result.embeddings]


def get_embedding_provider() -> EmbeddingProvider:
    if settings.EMBEDDING_PROVIDER == "gemini":
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set")
        return GeminiEmbeddingProvider(settings.GEMINI_API_KEY)
    raise ValueError(f"Unknown embedding provider: {settings.EMBEDDING_PROVIDER}")
