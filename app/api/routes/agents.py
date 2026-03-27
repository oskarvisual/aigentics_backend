from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import TenantScope
from app.db.session import get_db
from app.schemas.agent import AgentTemplateResponse, TenantAgentCreate, TenantAgentResponse
from app.services.agent_service import AgentCatalogService, TenantAgentService

router = APIRouter()


@router.get("/catalog", response_model=list[AgentTemplateResponse])
def list_catalog(db: Session = Depends(get_db)) -> list[AgentTemplateResponse]:
    return AgentCatalogService(db).list_templates()


@router.get("", response_model=list[TenantAgentResponse])
def list_agents(context: TenantScope, db: Session = Depends(get_db)) -> list[TenantAgentResponse]:
    return TenantAgentService(db).list(context.tenant_id)


@router.post("", response_model=TenantAgentResponse)
def create_agent(
    payload: TenantAgentCreate, context: TenantScope, db: Session = Depends(get_db)
) -> TenantAgentResponse:
    return TenantAgentService(db).create(context, payload)

