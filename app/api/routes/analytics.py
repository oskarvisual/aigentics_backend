from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import TenantScope
from app.db.session import get_db
from app.schemas.analytics import DashboardSummary
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/dashboard", response_model=DashboardSummary)
def dashboard_summary(context: TenantScope, db: Session = Depends(get_db)) -> DashboardSummary:
    return AnalyticsService(db).dashboard_summary(context.tenant_id, context.user.id)

