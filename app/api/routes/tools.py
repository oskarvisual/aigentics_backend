from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import TenantScope
from app.db.session import get_db
from app.schemas.integration import ToolDefinitionResponse
from app.services.integration_service import IntegrationService

router = APIRouter()


@router.get("", response_model=list[ToolDefinitionResponse])
def list_tools(context: TenantScope, db: Session = Depends(get_db)) -> list[ToolDefinitionResponse]:
    return IntegrationService(db).list_tools(context.tenant_id)
