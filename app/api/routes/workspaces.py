from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, TenantScope
from app.db.session import get_db
from app.schemas.workspace import MembershipResponse, WorkspaceCreate, WorkspaceResponse
from app.services.workspace_service import WorkspaceService

router = APIRouter()


@router.get("/memberships", response_model=list[MembershipResponse])
def list_memberships(current_user: CurrentUser, db: Session = Depends(get_db)) -> list[MembershipResponse]:
    return WorkspaceService(db).list_for_user(current_user.id)


@router.post("", response_model=WorkspaceResponse)
def create_workspace(
    payload: WorkspaceCreate, context: TenantScope, db: Session = Depends(get_db)
) -> WorkspaceResponse:
    return WorkspaceService(db).create(context, payload)

