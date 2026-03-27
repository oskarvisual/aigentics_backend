from __future__ import annotations

from sqlalchemy import Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import KnowledgeSourceType, ProcessingStatus
from app.db.base_class import Base, JSONMixin, JsonDict, TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class KnowledgeSource(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, JSONMixin):
    __tablename__ = "knowledge_sources"
    __table_args__ = (Index("ix_knowledge_sources_tenant_status", "tenant_id", "status"),)

    uploaded_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    source_type: Mapped[KnowledgeSourceType] = mapped_column(Enum(KnowledgeSourceType), index=True)
    original_object_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus), default=ProcessingStatus.PENDING
    )
    language: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source_metadata: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    permissions: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    ownership: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    documents: Mapped[list["KnowledgeDocument"]] = relationship(back_populates="source")
    chunks: Mapped[list["KnowledgeChunk"]] = relationship(back_populates="source")


class KnowledgeDocument(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, JSONMixin):
    __tablename__ = "knowledge_documents"

    source_id: Mapped[str] = mapped_column(ForeignKey("knowledge_sources.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    document_metadata: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus), default=ProcessingStatus.PENDING
    )
    extracted_text_object_key: Mapped[str | None] = mapped_column(String(500), nullable=True)

    source: Mapped["KnowledgeSource"] = relationship(back_populates="documents")
    chunks: Mapped[list["KnowledgeChunk"]] = relationship(back_populates="document")


class KnowledgeChunk(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, JSONMixin):
    __tablename__ = "knowledge_chunks"

    source_id: Mapped[str] = mapped_column(ForeignKey("knowledge_sources.id"), index=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("knowledge_documents.id"), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    content_preview: Mapped[str] = mapped_column(Text)
    vector_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    language: Mapped[str | None] = mapped_column(String(32), nullable=True)
    permissions: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    chunk_metadata: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    source: Mapped["KnowledgeSource"] = relationship(back_populates="chunks")
    document: Mapped["KnowledgeDocument"] = relationship(back_populates="chunks")

