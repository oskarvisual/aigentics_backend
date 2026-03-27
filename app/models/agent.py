from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import AgentStatus
from app.db.base_class import Base, JSONMixin, JsonDict, TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class AgentTemplate(Base, UUIDPrimaryKeyMixin, TimestampMixin, JSONMixin):
    __tablename__ = "agent_templates"

    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    role_title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    default_system_prompt: Mapped[str] = mapped_column(Text)
    default_language: Mapped[str] = mapped_column(String(32), default="en")
    default_tone: Mapped[str] = mapped_column(String(100), default="professional")
    capability_tags: Mapped[list] = mapped_column(JsonDict, default=JSONMixin.json_list_default)
    default_policies: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    default_metrics_schema: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    is_manager_template: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    tenant_agents: Mapped[list["TenantAgent"]] = relationship(back_populates="template")


class TenantAgent(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, JSONMixin):
    __tablename__ = "tenant_agents"
    __table_args__ = (
        Index("ix_tenant_agents_tenant_status", "tenant_id", "status"),
        UniqueConstraint("tenant_id", "name", name="uq_tenant_agents_tenant_name"),
    )

    template_id: Mapped[str] = mapped_column(ForeignKey("agent_templates.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    role_title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[AgentStatus] = mapped_column(Enum(AgentStatus), default=AgentStatus.DRAFT)
    language: Mapped[str] = mapped_column(String(32), default="en")
    tone: Mapped[str] = mapped_column(String(100), default="professional")
    instructions_override: Mapped[str | None] = mapped_column(Text, nullable=True)
    knowledge_scope: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    approval_rules: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    pending_work_count: Mapped[int] = mapped_column(Integer, default=0)
    completed_actions_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_actions_count: Mapped[int] = mapped_column(Integer, default=0)
    requires_attention: Mapped[bool] = mapped_column(Boolean, default=False)
    last_active_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tenant: Mapped["Tenant"] = relationship(back_populates="agents")
    template: Mapped["AgentTemplate"] = relationship(back_populates="tenant_agents")
    personality_profile: Mapped["AgentPersonalityProfile"] = relationship(
        back_populates="tenant_agent", uselist=False
    )
    skill_assignments: Mapped[list["TenantAgentSkillAssignment"]] = relationship(
        back_populates="tenant_agent"
    )
    tool_permissions: Mapped[list["TenantAgentToolPermission"]] = relationship(
        back_populates="tenant_agent"
    )


class AgentPersonalityProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, JSONMixin):
    __tablename__ = "agent_personality_profiles"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "tenant_agent_id", name="uq_agent_personality_profiles_tenant_agent"
        ),
    )

    tenant_agent_id: Mapped[str] = mapped_column(ForeignKey("tenant_agents.id"), index=True)
    persona_summary: Mapped[str] = mapped_column(Text)
    communication_style: Mapped[str] = mapped_column(Text)
    tone_modifiers: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    guardrails: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    escalation_preferences: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)

    tenant_agent: Mapped["TenantAgent"] = relationship(back_populates="personality_profile")


class AgentSkill(Base, UUIDPrimaryKeyMixin, TimestampMixin, JSONMixin):
    __tablename__ = "agent_skills"

    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100), index=True)
    config_schema: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)

    tenant_assignments: Mapped[list["TenantAgentSkillAssignment"]] = relationship(
        back_populates="skill"
    )


class TenantAgentSkillAssignment(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, JSONMixin):
    __tablename__ = "tenant_agent_skill_assignments"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "tenant_agent_id",
            "skill_id",
            name="uq_tenant_agent_skill_assignments_tenant_agent_skill",
        ),
    )

    tenant_agent_id: Mapped[str] = mapped_column(ForeignKey("tenant_agents.id"), index=True)
    skill_id: Mapped[str] = mapped_column(ForeignKey("agent_skills.id"), index=True)
    config: Mapped[dict] = mapped_column(JsonDict, default=JSONMixin.json_default)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    tenant_agent: Mapped["TenantAgent"] = relationship(back_populates="skill_assignments")
    skill: Mapped["AgentSkill"] = relationship(back_populates="tenant_assignments")


from app.models.tool import TenantAgentToolPermission  # noqa: E402  pylint: disable=wrong-import-position
from app.models.identity import Tenant  # noqa: E402  pylint: disable=wrong-import-position
