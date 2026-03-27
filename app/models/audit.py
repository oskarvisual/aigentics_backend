from __future__ import annotations

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import AuditActorType
from app.db.base_class import Base, JSONMixin, JsonDict, TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class AuditLog(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, JSONMixin):
    __tablename__ = "audit_logs"

    actor_type: Mapped[AuditActorType] = mapped_column(Enum(AuditActorType), index=True)
    actor_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    actor_agent_id: Mapped[str | None] = mapped_column(ForeignKey("tenant_agents.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(150), index=True)
    entity_type: Mapped[str] = mapped_column(String(100), index=True)
    entity_id: Mapped[str] = mapped_column(String(36), index=True)
    status: Mapped[str] = mapped_column(String(50), default="success")
    metadata_json: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    redacted_details: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)

