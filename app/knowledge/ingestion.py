from __future__ import annotations

from qdrant_client.http import models
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.enums import ProcessingStatus
from app.knowledge.embeddings import EmbeddingProvider, GeminiEmbeddingProvider
from app.knowledge.qdrant import QdrantKnowledgeStore
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument, KnowledgeSource


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    if len(text) <= chunk_size:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return chunks


class KnowledgeIngestionService:
    def __init__(
        self,
        db: Session,
        embeddings: EmbeddingProvider | None = None,
        vector_store: QdrantKnowledgeStore | None = None,
    ) -> None:
        settings = get_settings()
        self.db = db
        self.embeddings = embeddings or GeminiEmbeddingProvider(
            api_key=settings.google_api_key,
            model_name=settings.default_embedding_model,
        )
        self.vector_store = vector_store or QdrantKnowledgeStore()

    def ingest_text_document(self, source: KnowledgeSource, title: str, text: str) -> KnowledgeDocument:
        source.status = ProcessingStatus.PROCESSING
        document = KnowledgeDocument(
            tenant_id=source.tenant_id,
            source_id=source.id,
            title=title,
            mime_type="text/plain",
            processing_status=ProcessingStatus.PROCESSING,
        )
        self.db.add(document)
        self.db.flush()

        chunks = chunk_text(text)
        vectors = self.embeddings.embed_texts(chunks)
        if vectors:
            self.vector_store.ensure_collection(vector_size=len(vectors[0]))
        points: list[models.PointStruct] = []
        for index, (content, vector) in enumerate(zip(chunks, vectors, strict=True)):
            chunk = KnowledgeChunk(
                tenant_id=source.tenant_id,
                source_id=source.id,
                document_id=document.id,
                chunk_index=index,
                content_preview=content[:500],
                vector_id=f"{document.id}:{index}",
                language=source.language,
                permissions=source.permissions,
                chunk_metadata=source.source_metadata,
            )
            self.db.add(chunk)
            self.db.flush()
            points.append(
                models.PointStruct(
                    id=chunk.vector_id,
                    vector=vector,
                    payload={
                        "tenant_id": source.tenant_id,
                        "agent_scope": source.permissions.get("agent_ids", []),
                        "source_id": source.id,
                        "source_type": source.source_type,
                        "modality": "text",
                        "permissions": source.permissions,
                        "language": source.language,
                        "chunk_index": index,
                        "created_at": chunk.created_at.isoformat(),
                        "tags": source.source_metadata.get("tags", []),
                        "chunk_id": chunk.id,
                        "preview": chunk.content_preview,
                    },
                )
            )
        if points:
            self.vector_store.upsert(vector_size=len(vectors[0]), points=points)

        document.processing_status = ProcessingStatus.READY
        source.status = ProcessingStatus.READY
        self.db.commit()
        self.db.refresh(document)
        return document

