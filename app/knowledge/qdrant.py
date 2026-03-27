from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.core.config import get_settings

COLLECTION_NAME = "knowledge_chunks"


class QdrantKnowledgeStore:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)

    def ensure_collection(self, vector_size: int) -> None:
        collections = [item.name for item in self.client.get_collections().collections]
        if COLLECTION_NAME in collections:
            return
        self.client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
        )

    def upsert(
        self,
        *,
        vector_size: int,
        points: list[models.PointStruct],
    ) -> None:
        self.ensure_collection(vector_size=vector_size)
        self.client.upsert(collection_name=COLLECTION_NAME, points=points)

    def search(self, query_vector: list[float], limit: int, query_filter: models.Filter) -> list:
        return self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit,
            query_filter=query_filter,
        )

