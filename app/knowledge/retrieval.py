from __future__ import annotations

from qdrant_client.http import models
from pydantic import BaseModel

from app.core.config import get_settings
from app.knowledge.embeddings import EmbeddingProvider, GeminiEmbeddingProvider
from app.knowledge.qdrant import QdrantKnowledgeStore


class RetrievalResult(BaseModel):
    chunk_id: str
    source_id: str
    score: float
    preview: str
    metadata: dict


class RetrievalService:
    def __init__(
        self,
        embeddings: EmbeddingProvider | None = None,
        vector_store: QdrantKnowledgeStore | None = None,
    ) -> None:
        settings = get_settings()
        self.embeddings = embeddings or GeminiEmbeddingProvider(
            api_key=settings.google_api_key,
            model_name=settings.default_embedding_model,
        )
        self.vector_store = vector_store or QdrantKnowledgeStore()

    def search(
        self,
        *,
        tenant_id: str,
        agent_id: str | None,
        query: str,
        limit: int = 5,
    ) -> list[RetrievalResult]:
        vectors = self.embeddings.embed_texts([query])
        should_conditions = None
        if agent_id:
            should_conditions = [
                models.FieldCondition(key="agent_scope", match=models.MatchValue(value=agent_id))
            ]
        query_filter = models.Filter(
            must=[models.FieldCondition(key="tenant_id", match=models.MatchValue(value=tenant_id))],
            should=should_conditions,
        )
        hits = self.vector_store.search(query_vector=vectors[0], limit=limit, query_filter=query_filter)
        return [
            RetrievalResult(
                chunk_id=hit.payload.get("chunk_id", ""),
                source_id=hit.payload.get("source_id", ""),
                score=hit.score,
                preview=hit.payload.get("preview", ""),
                metadata=hit.payload,
            )
            for hit in hits
        ]
