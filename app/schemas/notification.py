from app.core.enums import NotificationType
from app.schemas.common import TimestampedResponse


class NotificationResponse(TimestampedResponse):
    tenant_id: str
    user_id: str | None
    notification_type: NotificationType
    title: str
    body: str
    payload: dict
    is_read: bool

