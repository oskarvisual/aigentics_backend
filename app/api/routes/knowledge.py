from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import TenantScope
from app.db.session import get_db
from app.schemas.knowledge import KnowledgeSourceCreate, KnowledgeSourceResponse
from app.services.knowledge_service import KnowledgeService

router = APIRouter()


@router.get("/sources", response_model=list[KnowledgeSourceResponse])
def list_sources(context: TenantScope, db: Session = Depends(get_db)) -> list[KnowledgeSourceResponse]:
    return KnowledgeService(db).list_sources(context.tenant_id)


@router.post("/sources", response_model=KnowledgeSourceResponse)
def create_source(
    payload: KnowledgeSourceCreate, context: TenantScope, db: Session = Depends(get_db)
) -> KnowledgeSourceResponse:
    return KnowledgeService(db).create_source(context, payload)

