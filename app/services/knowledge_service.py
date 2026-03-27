from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import AuditActorType, ProcessingStatus, WorkspaceRole
from app.models.knowledge import KnowledgeSource
from app.schemas.knowledge import KnowledgeSourceCreate
from app.services.audit_service import AuditService
from app.services.base import TenantContext, ensure_role


class KnowledgeService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditService(db)

    def list_sources(self, tenant_id: str) -> list[KnowledgeSource]:
        return list(
            self.db.scalars(
                select(KnowledgeSource)
                .where(KnowledgeSource.tenant_id == tenant_id)
                .order_by(KnowledgeSource.created_at.desc())
            )
        )

    def create_source(self, context: TenantContext, payload: KnowledgeSourceCreate) -> KnowledgeSource:
        ensure_role(
            context,
            [WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.MANAGER, WorkspaceRole.HUMAN_AGENT],
        )
        source = KnowledgeSource(
            tenant_id=context.tenant_id,
            uploaded_by_user_id=context.user.id,
            name=payload.name,
            source_type=payload.source_type,
            original_object_key=payload.original_object_key,
            status=ProcessingStatus.PENDING,
            language=payload.language,
            source_metadata=payload.source_metadata,
            permissions=payload.permissions,
            ownership=payload.ownership,
        )
        self.db.add(source)
        self.db.flush()
        self.audit.log(
            tenant_id=context.tenant_id,
            actor_type=AuditActorType.USER,
            actor_user_id=context.user.id,
            actor_agent_id=None,
            action="knowledge.create_source",
            entity_type="knowledge_source",
            entity_id=source.id,
        )
        self.db.commit()
        self.db.refresh(source)
        return source

