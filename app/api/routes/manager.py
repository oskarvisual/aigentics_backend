from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import TenantScope
from app.db.session import get_db
from app.schemas.manager import ManagerInsightResponse
from app.services.manager_service import ManagerInsightService

router = APIRouter()


@router.get("", response_model=list[ManagerInsightResponse])
def list_manager_insights(
    context: TenantScope, db: Session = Depends(get_db)
) -> list[ManagerInsightResponse]:
    return ManagerInsightService(db).list(context.tenant_id)
