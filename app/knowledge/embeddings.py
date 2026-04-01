from __future__ import annotations

from typing import Protocol

from google import genai


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
        self.model_name = model_name.removeprefix("models/")

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is required for Gemini embeddings.")

        client = genai.Client(api_key=self.api_key)
        response = client.models.embed_content(model=self.model_name, contents=texts)
        return [list(embedding.values) for embedding in response.embeddings]

