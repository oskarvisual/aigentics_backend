from __future__ import annotations

from typing import Protocol


class EmbeddingProvider(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per text input."""


class GeminiEmbeddingProvider:
    """
    Gemini embedding adapter scaffold.

    This intentionally keeps SDK-specific calls encapsulated so the rest of the codebase
    does not depend on a particular Google client implementation detail.
    """

    def __init__(self, api_key: str | None, model_name: str) -> None:
        self.api_key = api_key
        self.model_name = model_name

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError(
            "Wire the active Google GenAI SDK for Gemini Embedding here. "
            "The service boundary is ready; only the provider adapter remains SDK-specific."
        )

