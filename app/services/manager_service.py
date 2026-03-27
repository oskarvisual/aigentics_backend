from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.operation import ManagerInsight


class ManagerInsightService:
    def __init__(self, db: Session):
        self.db = db

    def list(self, tenant_id: str) -> list[ManagerInsight]:
        return list(
            self.db.scalars(
                select(ManagerInsight)
                .where(ManagerInsight.tenant_id == tenant_id)
                .order_by(ManagerInsight.created_at.desc())
            )
        )
