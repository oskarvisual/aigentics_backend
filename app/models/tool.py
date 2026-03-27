from __future__ import annotations

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ToolPermissionMode, ToolRiskLevel
from app.db.base_class import Base, JSONMixin, JsonDict, TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class ToolDefinition(Base, UUIDPrimaryKeyMixin, TimestampMixin, JSONMixin):
    __tablename__ = "tool_definitions"

    tenant_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    integration_template_id: Mapped[str | None] = mapped_column(
        ForeignKey("integration_templates.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(150))
    slug: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    input_schema: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    output_schema: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    tags: Mapped[list] = mapped_column(JsonDict, default=JSONMixin.json_list_default)
    risk_level: Mapped[ToolRiskLevel] = mapped_column(
        Enum(ToolRiskLevel), default=ToolRiskLevel.MEDIUM, index=True
    )
    permission_mode: Mapped[ToolPermissionMode] = mapped_column(
        Enum(ToolPermissionMode), default=ToolPermissionMode.SUPERVISED
    )
    implementation_type: Mapped[str] = mapped_column(String(100), default="adapter")
    source_kind: Mapped[str] = mapped_column(String(100), default="native")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    bindings: Mapped[list["TenantToolBinding"]] = relationship(back_populates="tool_definition")


class TenantToolBinding(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, JSONMixin):
    __tablename__ = "tenant_tool_bindings"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "tool_definition_id",
            "tenant_integration_id",
            name="uq_tenant_tool_bindings_binding",
        ),
    )

    tool_definition_id: Mapped[str] = mapped_column(ForeignKey("tool_definitions.id"), index=True)
    tenant_integration_id: Mapped[str | None] = mapped_column(
        ForeignKey("tenant_integrations.id"), nullable=True, index=True
    )
    display_name_override: Mapped[str | None] = mapped_column(String(255), nullable=True)
    config: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    tool_definition: Mapped["ToolDefinition"] = relationship(back_populates="bindings")
    tenant_integration: Mapped["TenantIntegration | None"] = relationship(
        back_populates="tool_bindings"
    )
    agent_permissions: Mapped[list["TenantAgentToolPermission"]] = relationship(
        back_populates="tenant_tool_binding"
    )


class TenantAgentToolPermission(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, JSONMixin):
    __tablename__ = "tenant_agent_tool_permissions"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "tenant_agent_id",
            "tenant_tool_binding_id",
            name="uq_tenant_agent_tool_permissions_agent_binding",
        ),
    )

    tenant_agent_id: Mapped[str] = mapped_column(ForeignKey("tenant_agents.id"), index=True)
    tenant_tool_binding_id: Mapped[str] = mapped_column(
        ForeignKey("tenant_tool_bindings.id"), index=True
    )
    permission_mode: Mapped[ToolPermissionMode] = mapped_column(Enum(ToolPermissionMode))
    max_risk_level: Mapped[ToolRiskLevel] = mapped_column(
        Enum(ToolRiskLevel), default=ToolRiskLevel.MEDIUM
    )
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    constraints: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)

    tenant_agent: Mapped["TenantAgent"] = relationship(back_populates="tool_permissions")
    tenant_tool_binding: Mapped["TenantToolBinding"] = relationship(back_populates="agent_permissions")


from app.models.agent import TenantAgent  # noqa: E402  pylint: disable=wrong-import-position
from app.models.integration import TenantIntegration  # noqa: E402  pylint: disable=wrong-import-position

