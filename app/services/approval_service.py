from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import ApprovalStatus, AuditActorType, WorkspaceRole
from app.models.approval import ApprovalRequest
from app.schemas.approval import ApprovalRequestCreate
from app.services.audit_service import AuditService
from app.services.base import TenantContext, ensure_role


class ApprovalService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditService(db)

    def list(self, tenant_id: str) -> list[ApprovalRequest]:
        return list(
            self.db.scalars(
                select(ApprovalRequest)
                .where(ApprovalRequest.tenant_id == tenant_id)
                .order_by(ApprovalRequest.created_at.desc())
            )
        )

    def create(self, context: TenantContext, payload: ApprovalRequestCreate) -> ApprovalRequest:
        approval = ApprovalRequest(
            tenant_id=context.tenant_id,
            tenant_agent_id=payload.tenant_agent_id,
            requested_by_user_id=context.user.id,
            conversation_id=payload.conversation_id,
            action_type=payload.action_type,
            reason=payload.reason,
            risk_score=payload.risk_score,
            request_payload=payload.request_payload,
            expires_at=payload.expires_at,
        )
        self.db.add(approval)
        self.db.flush()
        self.audit.log(
            tenant_id=context.tenant_id,
            actor_type=AuditActorType.USER,
            actor_user_id=context.user.id,
            actor_agent_id=None,
            action="approval.create",
            entity_type="approval_request",
            entity_id=approval.id,
        )
        self.db.commit()
        self.db.refresh(approval)
        return approval

    def decide(
        self, context: TenantContext, approval_id: str, approved: bool, decision_payload: dict
    ) -> ApprovalRequest:
        ensure_role(context, [WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.MANAGER])
        approval = self.db.scalar(
            select(ApprovalRequest).where(
                ApprovalRequest.id == approval_id, ApprovalRequest.tenant_id == context.tenant_id
            )
        )
        if approval is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found.")
        approval.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        approval.resolved_by_user_id = context.user.id
        approval.resolved_at = datetime.now(UTC)
        approval.decision_payload = decision_payload
        self.audit.log(
            tenant_id=context.tenant_id,
            actor_type=AuditActorType.USER,
            actor_user_id=context.user.id,
            actor_agent_id=None,
            action="approval.resolve",
            entity_type="approval_request",
            entity_id=approval.id,
            metadata_json={"approved": approved},
        )
        self.db.commit()
        self.db.refresh(approval)
        return approval

