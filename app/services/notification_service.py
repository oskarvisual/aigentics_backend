from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.operation import Notification


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, tenant_id: str, user_id: str) -> list[Notification]:
        return list(
            self.db.scalars(
                select(Notification)
                .where(Notification.tenant_id == tenant_id, Notification.user_id == user_id)
                .order_by(Notification.created_at.desc())
            )
        )

    def mark_read(self, tenant_id: str, user_id: str, notification_id: str) -> Notification | None:
        notification = self.db.scalar(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.tenant_id == tenant_id,
                Notification.user_id == user_id,
            )
        )
        if notification:
            notification.is_read = True
            self.db.commit()
            self.db.refresh(notification)
        return notification

