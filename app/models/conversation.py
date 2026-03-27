from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ConversationStatus, ConversationType, MessageRole
from app.db.base_class import Base, JSONMixin, JsonDict, TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Conversation(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, JSONMixin):
    __tablename__ = "conversations"
    __table_args__ = (Index("ix_conversations_tenant_status", "tenant_id", "status"),)

    tenant_agent_id: Mapped[str | None] = mapped_column(ForeignKey("tenant_agents.id"), nullable=True)
    assigned_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    conversation_type: Mapped[ConversationType] = mapped_column(Enum(ConversationType), index=True)
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[ConversationStatus] = mapped_column(
        Enum(ConversationStatus), default=ConversationStatus.OPEN
    )
    external_channel: Mapped[str | None] = mapped_column(String(100), nullable=True)
    channel_metadata: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    requires_human_handoff: Mapped[bool] = mapped_column(Boolean, default=False)
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    participants: Mapped[list["ConversationParticipant"]] = relationship(back_populates="conversation")
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation")


class ConversationParticipant(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    __tablename__ = "conversation_participants"

    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"), index=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    tenant_agent_id: Mapped[str | None] = mapped_column(ForeignKey("tenant_agents.id"), nullable=True)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False)
    last_read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    conversation: Mapped["Conversation"] = relationship(back_populates="participants")


class Message(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, JSONMixin):
    __tablename__ = "messages"

    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"), index=True)
    sender_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    sender_agent_id: Mapped[str | None] = mapped_column(ForeignKey("tenant_agents.id"), nullable=True)
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole), index=True)
    content: Mapped[str] = mapped_column(Text)
    content_structured: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    tool_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    tool_call_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    parent_message_id: Mapped[str | None] = mapped_column(ForeignKey("messages.id"), nullable=True)
    external_message_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")

