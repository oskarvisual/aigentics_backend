from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import TenantStatus, WorkspaceRole
from app.db.base_class import Base, JSONMixin, JsonDict, TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Tenant(Base, UUIDPrimaryKeyMixin, TimestampMixin, JSONMixin):
    __tablename__ = "tenants"

    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    status: Mapped[TenantStatus] = mapped_column(
        Enum(TenantStatus), default=TenantStatus.ACTIVE, index=True
    )
    branding_settings: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    workspace_settings: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)

    memberships: Mapped[list["TenantMembership"]] = relationship(back_populates="tenant")
    agents: Mapped[list["TenantAgent"]] = relationship(back_populates="tenant")


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    memberships: Mapped[list["TenantMembership"]] = relationship(
        back_populates="user", foreign_keys="TenantMembership.user_id"
    )
    refresh_sessions: Mapped[list["RefreshTokenSession"]] = relationship(back_populates="user")


class TenantMembership(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, JSONMixin):
    __tablename__ = "tenant_memberships"
    __table_args__ = (
        UniqueConstraint("tenant_id", "user_id", name="uq_tenant_memberships_tenant_user"),
    )

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[WorkspaceRole] = mapped_column(Enum(WorkspaceRole), index=True)
    permissions: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    is_default_workspace: Mapped[bool] = mapped_column(Boolean, default=False)
    invited_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    invited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tenant: Mapped["Tenant"] = relationship(back_populates="memberships")
    user: Mapped["User"] = relationship(
        back_populates="memberships", foreign_keys=[user_id]
    )


class RefreshTokenSession(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    __tablename__ = "refresh_token_sessions"
    __table_args__ = (Index("ix_refresh_token_sessions_user_tenant", "user_id", "tenant_id"),)

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(255))
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="refresh_sessions")


from app.models.agent import TenantAgent  # noqa: E402  pylint: disable=wrong-import-position
