from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tool import TenantAgentToolPermission, TenantToolBinding, ToolDefinition


class ToolSummary(BaseModel):
    binding_id: str
    tool_slug: str
    display_name: str
    risk_level: str
    permission_mode: str
    enabled: bool


class ToolRegistryService:
    def __init__(self, db: Session):
        self.db = db

    def list_agent_tools(self, *, tenant_id: str, agent_id: str | None) -> list[ToolSummary]:
        if agent_id is None:
            return []
        rows = self.db.execute(
            select(TenantAgentToolPermission, TenantToolBinding, ToolDefinition)
            .join(
                TenantToolBinding,
                TenantToolBinding.id == TenantAgentToolPermission.tenant_tool_binding_id,
            )
            .join(ToolDefinition, ToolDefinition.id == TenantToolBinding.tool_definition_id)
            .where(
                TenantAgentToolPermission.tenant_id == tenant_id,
                TenantAgentToolPermission.tenant_agent_id == agent_id,
            )
        ).all()
        return [
            ToolSummary(
                binding_id=binding.id,
                tool_slug=definition.slug,
                display_name=binding.display_name_override or definition.display_name,
                risk_level=permission.max_risk_level,
                permission_mode=permission.permission_mode,
                enabled=binding.enabled,
            )
            for permission, binding, definition in rows
        ]
