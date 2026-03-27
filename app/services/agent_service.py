from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import AgentStatus, AuditActorType, WorkspaceRole
from app.models.agent import AgentTemplate, TenantAgent
from app.schemas.agent import TenantAgentCreate
from app.services.audit_service import AuditService
from app.services.base import TenantContext, ensure_role


class AgentCatalogService:
    def __init__(self, db: Session):
        self.db = db

    def list_templates(self) -> list[AgentTemplate]:
        return list(self.db.scalars(select(AgentTemplate).where(AgentTemplate.is_active.is_(True))))


class TenantAgentService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditService(db)

    def list(self, tenant_id: str) -> list[TenantAgent]:
        return list(
            self.db.scalars(
                select(TenantAgent).where(TenantAgent.tenant_id == tenant_id).order_by(TenantAgent.created_at)
            )
        )

    def create(self, context: TenantContext, payload: TenantAgentCreate) -> TenantAgent:
        ensure_role(context, [WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.MANAGER])
        agent = TenantAgent(
            tenant_id=context.tenant_id,
            template_id=payload.template_id,
            name=payload.name,
            role_title=payload.role_title,
            description=payload.description,
            status=AgentStatus.ONBOARDING,
            language=payload.language,
            tone=payload.tone,
            instructions_override=payload.instructions_override,
            knowledge_scope=payload.knowledge_scope,
            approval_rules=payload.approval_rules,
        )
        self.db.add(agent)
        self.db.flush()
        self.audit.log(
            tenant_id=context.tenant_id,
            actor_type=AuditActorType.USER,
            actor_user_id=context.user.id,
            actor_agent_id=None,
            action="agent.hire",
            entity_type="tenant_agent",
            entity_id=agent.id,
        )
        self.db.commit()
        self.db.refresh(agent)
        return agent

