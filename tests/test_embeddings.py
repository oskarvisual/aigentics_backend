from types import SimpleNamespace

from app.knowledge.embeddings import GeminiEmbeddingProvider


def test_gemini_embedding_provider_normalizes_model_and_returns_values(monkeypatch) -> None:
    captured: dict = {}

    class FakeModels:
        def embed_content(self, *, model: str, contents: list[str]):
            captured["model"] = model
            captured["contents"] = contents
            return SimpleNamespace(
                embeddings=[
                    SimpleNamespace(values=[0.1, 0.2]),
                    SimpleNamespace(values=[0.3, 0.4]),
                ]
            )

    class FakeClient:
        def __init__(self, *, api_key: str):
            captured["api_key"] = api_key
            self.models = FakeModels()

    monkeypatch.setattr("app.knowledge.embeddings.genai.Client", FakeClient)

    provider = GeminiEmbeddingProvider(
        api_key="test-google-key",
        model_name="models/gemini-embedding-001",
    )
    vectors = provider.embed_texts(["hello", "world"])

    assert captured["api_key"] == "test-google-key"
    assert captured["model"] == "gemini-embedding-001"
    assert captured["contents"] == ["hello", "world"]
    assert vectors == [[0.1, 0.2], [0.3, 0.4]]


def test_gemini_embedding_provider_requires_api_key() -> None:
    provider = GeminiEmbeddingProvider(api_key=None, model_name="gemini-embedding-001")

    try:
        provider.embed_texts(["hello"])
    except ValueError as exc:
        assert "GOOGLE_API_KEY" in str(exc)
    else:
        raise AssertionError("Expected ValueError when GOOGLE_API_KEY is missing.")
