from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ApprovalStatus
from app.db.base_class import Base, JSONMixin, JsonDict, TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class ApprovalRequest(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, JSONMixin):
    __tablename__ = "approval_requests"

    tenant_agent_id: Mapped[str | None] = mapped_column(ForeignKey("tenant_agents.id"), nullable=True)
    requested_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    conversation_id: Mapped[str | None] = mapped_column(ForeignKey("conversations.id"), nullable=True)
    action_type: Mapped[str] = mapped_column(String(150), index=True)
    reason: Mapped[str] = mapped_column(Text)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus), default=ApprovalStatus.PENDING, index=True
    )
    request_payload: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    decision_payload: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

