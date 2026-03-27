from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import TenantScope
from app.db.session import get_db
from app.schemas.approval import (
    ApprovalDecision,
    ApprovalRequestCreate,
    ApprovalRequestResponse,
)
from app.services.approval_service import ApprovalService

router = APIRouter()


@router.get("", response_model=list[ApprovalRequestResponse])
def list_approvals(context: TenantScope, db: Session = Depends(get_db)) -> list[ApprovalRequestResponse]:
    return ApprovalService(db).list(context.tenant_id)


@router.post("", response_model=ApprovalRequestResponse)
def create_approval(
    payload: ApprovalRequestCreate, context: TenantScope, db: Session = Depends(get_db)
) -> ApprovalRequestResponse:
    return ApprovalService(db).create(context, payload)


@router.post("/{approval_id}/approve", response_model=ApprovalRequestResponse)
def approve(
    approval_id: str,
    payload: ApprovalDecision,
    context: TenantScope,
    db: Session = Depends(get_db),
) -> ApprovalRequestResponse:
    return ApprovalService(db).decide(context, approval_id, True, payload.decision_payload)


@router.post("/{approval_id}/reject", response_model=ApprovalRequestResponse)
def reject(
    approval_id: str,
    payload: ApprovalDecision,
    context: TenantScope,
    db: Session = Depends(get_db),
) -> ApprovalRequestResponse:
    return ApprovalService(db).decide(context, approval_id, False, payload.decision_payload)

