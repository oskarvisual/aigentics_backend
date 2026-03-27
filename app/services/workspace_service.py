from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import AuditActorType, WorkspaceRole
from app.models.identity import Tenant, TenantMembership
from app.schemas.workspace import WorkspaceCreate
from app.services.audit_service import AuditService
from app.services.base import TenantContext, ensure_role


class WorkspaceService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditService(db)

    def list_for_user(self, user_id: str) -> list[TenantMembership]:
        return list(
            self.db.scalars(
                select(TenantMembership).where(TenantMembership.user_id == user_id).order_by(TenantMembership.created_at)
            )
        )

    def create(self, context: TenantContext, payload: WorkspaceCreate) -> Tenant:
        ensure_role(context, [WorkspaceRole.OWNER])
        tenant = Tenant(slug=payload.slug, name=payload.name)
        self.db.add(tenant)
        self.db.flush()
        self.audit.log(
            tenant_id=context.tenant_id,
            actor_type=AuditActorType.USER,
            actor_user_id=context.user.id,
            actor_agent_id=None,
            action="workspace.create",
            entity_type="tenant",
            entity_id=tenant.id,
        )
        self.db.commit()
        self.db.refresh(tenant)
        return tenant

