from sqlalchemy.orm import Session

from app.core.enums import AuditActorType
from app.models.audit import AuditLog


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        *,
        tenant_id: str,
        actor_type: AuditActorType,
        actor_user_id: str | None,
        actor_agent_id: str | None,
        action: str,
        entity_type: str,
        entity_id: str,
        status: str = "success",
        metadata_json: dict | None = None,
        redacted_details: dict | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            tenant_id=tenant_id,
            actor_type=actor_type,
            actor_user_id=actor_user_id,
            actor_agent_id=actor_agent_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            status=status,
            metadata_json=metadata_json or {},
            redacted_details=redacted_details or {},
        )
        self.db.add(entry)
        self.db.flush()
        return entry

