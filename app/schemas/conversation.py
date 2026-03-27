from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enums import ConversationStatus, ConversationType, MessageRole
from app.schemas.common import TimestampedResponse


class ConversationCreate(BaseModel):
    tenant_agent_id: str | None = None
    subject: str | None = Field(default=None, max_length=255)
    conversation_type: ConversationType
    external_channel: str | None = None
    channel_metadata: dict = Field(default_factory=dict)


class ConversationResponse(TimestampedResponse):
    tenant_id: str
    tenant_agent_id: str | None
    assigned_user_id: str | None
    conversation_type: ConversationType
    subject: str | None
    status: ConversationStatus
    external_channel: str | None
    channel_metadata: dict
    requires_human_handoff: bool
    last_message_at: datetime | None


class MessageCreate(BaseModel):
    role: MessageRole
    content: str = Field(min_length=1)
    content_structured: dict = Field(default_factory=dict)
    tool_name: str | None = None
    tool_call_id: str | None = None
    parent_message_id: str | None = None
    requires_approval: bool = False


class MessageResponse(TimestampedResponse):
    tenant_id: str
    conversation_id: str
    sender_user_id: str | None
    sender_agent_id: str | None
    role: MessageRole
    content: str
    content_structured: dict
    tool_name: str | None
    tool_call_id: str | None
    parent_message_id: str | None
    external_message_ref: str | None
    requires_approval: bool

