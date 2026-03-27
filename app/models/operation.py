from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ManagerInsightSeverity, NotificationType, ScheduledJobStatus
from app.db.base_class import Base, JSONMixin, JsonDict, TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Notification(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, JSONMixin):
    __tablename__ = "notifications"

    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    notification_type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), index=True)
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class ManagerInsight(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, JSONMixin):
    __tablename__ = "manager_insights"

    tenant_agent_id: Mapped[str | None] = mapped_column(ForeignKey("tenant_agents.id"), nullable=True)
    severity: Mapped[ManagerInsightSeverity] = mapped_column(
        Enum(ManagerInsightSeverity), default=ManagerInsightSeverity.INFO
    )
    category: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text)
    insight_payload: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    dismissed: Mapped[bool] = mapped_column(Boolean, default=False)


class ScheduledJob(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, JSONMixin):
    __tablename__ = "scheduled_jobs"

    job_name: Mapped[str] = mapped_column(String(255), index=True)
    job_type: Mapped[str] = mapped_column(String(100), index=True)
    interval_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cron_expression: Mapped[str | None] = mapped_column(String(100), nullable=True)
    payload: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    status: Mapped[ScheduledJobStatus] = mapped_column(
        Enum(ScheduledJobStatus), default=ScheduledJobStatus.QUEUED
    )
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
