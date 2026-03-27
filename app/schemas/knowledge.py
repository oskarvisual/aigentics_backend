from pydantic import BaseModel, Field

from app.core.enums import KnowledgeSourceType, ProcessingStatus
from app.schemas.common import TimestampedResponse


class KnowledgeSourceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    source_type: KnowledgeSourceType
    original_object_key: str | None = None
    language: str | None = None
    source_metadata: dict = Field(default_factory=dict)
    permissions: dict = Field(default_factory=dict)
    ownership: dict = Field(default_factory=dict)


class KnowledgeSourceResponse(TimestampedResponse):
    tenant_id: str
    uploaded_by_user_id: str | None
    name: str
    source_type: KnowledgeSourceType
    original_object_key: str | None
    status: ProcessingStatus
    language: str | None
    source_metadata: dict
    permissions: dict
    ownership: dict
    checksum: str | None
    last_error: str | None


class RetrievalRequest(BaseModel):
    query: str = Field(min_length=3)
    agent_id: str | None = None
    limit: int = Field(default=5, ge=1, le=20)
    filters: dict = Field(default_factory=dict)


class RetrievalHit(BaseModel):
    chunk_id: str
    source_id: str
    score: float
    preview: str
    metadata: dict

