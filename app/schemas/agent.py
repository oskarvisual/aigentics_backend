from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enums import AgentStatus, ToolPermissionMode, ToolRiskLevel
from app.schemas.common import TimestampedResponse


class AgentTemplateResponse(TimestampedResponse):
    slug: str
    name: str
    role_title: str
    description: str
    default_language: str
    default_tone: str
    capability_tags: list
    default_policies: dict
    is_manager_template: bool


class TenantAgentCreate(BaseModel):
    template_id: str
    name: str = Field(min_length=2, max_length=255)
    role_title: str
    description: str
    language: str = "en"
    tone: str = "professional"
    instructions_override: str | None = None
    knowledge_scope: dict = Field(default_factory=dict)
    approval_rules: dict = Field(default_factory=dict)


class TenantAgentResponse(TimestampedResponse):
    tenant_id: str
    template_id: str
    name: str
    role_title: str
    description: str
    status: AgentStatus
    language: str
    tone: str
    knowledge_scope: dict
    approval_rules: dict
    pending_work_count: int
    completed_actions_count: int
    failed_actions_count: int
    requires_attention: bool
    last_active_at: datetime | None


class ToolPermissionResponse(TimestampedResponse):
    tenant_id: str
    tenant_agent_id: str
    tenant_tool_binding_id: str
    permission_mode: ToolPermissionMode
    max_risk_level: ToolRiskLevel
    requires_approval: bool
    constraints: dict

