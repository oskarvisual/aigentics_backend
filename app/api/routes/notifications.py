from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import TenantScope
from app.db.session import get_db
from app.schemas.notification import NotificationResponse
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get("", response_model=list[NotificationResponse])
def list_notifications(
    context: TenantScope, db: Session = Depends(get_db)
) -> list[NotificationResponse]:
    return NotificationService(db).list_for_user(context.tenant_id, context.user.id)


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_read(
    notification_id: str, context: TenantScope, db: Session = Depends(get_db)
) -> NotificationResponse:
    notification = NotificationService(db).mark_read(context.tenant_id, context.user.id, notification_id)
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
    return notification

