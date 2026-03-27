from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import TenantScope
from app.db.session import get_db
from app.schemas.integration import (
    IntegrationTemplateResponse,
    TenantIntegrationCreate,
    TenantIntegrationResponse,
    ToolDefinitionResponse,
)
from app.services.integration_service import IntegrationService

router = APIRouter()


@router.get("/templates", response_model=list[IntegrationTemplateResponse])
def list_templates(db: Session = Depends(get_db)) -> list[IntegrationTemplateResponse]:
    return IntegrationService(db).list_templates()


@router.get("", response_model=list[TenantIntegrationResponse])
def list_integrations(
    context: TenantScope, db: Session = Depends(get_db)
) -> list[TenantIntegrationResponse]:
    return IntegrationService(db).list_tenant_integrations(context.tenant_id)


@router.post("", response_model=TenantIntegrationResponse)
def create_integration(
    payload: TenantIntegrationCreate, context: TenantScope, db: Session = Depends(get_db)
) -> TenantIntegrationResponse:
    return IntegrationService(db).create_tenant_integration(context, payload)


@router.get("/tools", response_model=list[ToolDefinitionResponse])
def list_tools(context: TenantScope, db: Session = Depends(get_db)) -> list[ToolDefinitionResponse]:
    return IntegrationService(db).list_tools(context.tenant_id)

