from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import (
    CredentialType,
    IntegrationConnectionStatus,
    IntegrationOwnershipType,
    IntegrationType,
)
from app.db.base_class import Base, JSONMixin, JsonDict, TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class IntegrationTemplate(Base, UUIDPrimaryKeyMixin, TimestampMixin, JSONMixin):
    __tablename__ = "integration_templates"

    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    provider: Mapped[str] = mapped_column(String(100), index=True)
    integration_type: Mapped[IntegrationType] = mapped_column(Enum(IntegrationType), index=True)
    ownership_type: Mapped[IntegrationOwnershipType] = mapped_column(
        Enum(IntegrationOwnershipType), default=IntegrationOwnershipType.NATIVE
    )
    auth_type: Mapped[CredentialType] = mapped_column(Enum(CredentialType))
    description: Mapped[str] = mapped_column(Text)
    tool_generation_strategy: Mapped[str] = mapped_column(String(100), default="native")
    config_schema: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    tenant_integrations: Mapped[list["TenantIntegration"]] = relationship(back_populates="template")


class IntegrationCredentialsReference(
    Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, JSONMixin
):
    __tablename__ = "integration_credentials_reference"

    provider: Mapped[str] = mapped_column(String(100), index=True)
    credential_type: Mapped[CredentialType] = mapped_column(Enum(CredentialType))
    secret_path: Mapped[str] = mapped_column(String(500))
    secret_metadata: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    last_rotated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tenant_integrations: Mapped[list["TenantIntegration"]] = relationship(back_populates="credentials")


class TenantIntegration(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, JSONMixin):
    __tablename__ = "tenant_integrations"
    __table_args__ = (Index("ix_tenant_integrations_tenant_status", "tenant_id", "status"),)

    template_id: Mapped[str] = mapped_column(ForeignKey("integration_templates.id"), index=True)
    credentials_reference_id: Mapped[str | None] = mapped_column(
        ForeignKey("integration_credentials_reference.id"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[IntegrationConnectionStatus] = mapped_column(
        Enum(IntegrationConnectionStatus), default=IntegrationConnectionStatus.DISCONNECTED
    )
    ownership_type: Mapped[IntegrationOwnershipType] = mapped_column(
        Enum(IntegrationOwnershipType), default=IntegrationOwnershipType.TENANT_PRIVATE
    )
    external_account_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    config: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    last_tested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_shared_connection: Mapped[bool] = mapped_column(Boolean, default=False)

    template: Mapped["IntegrationTemplate"] = relationship(back_populates="tenant_integrations")
    credentials: Mapped["IntegrationCredentialsReference | None"] = relationship(
        back_populates="tenant_integrations"
    )
    tool_bindings: Mapped[list["TenantToolBinding"]] = relationship(back_populates="tenant_integration")


from app.models.tool import TenantToolBinding  # noqa: E402  pylint: disable=wrong-import-position

