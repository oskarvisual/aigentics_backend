from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import TenantScope
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get("", response_model=list[UserResponse])
def list_users(context: TenantScope, db: Session = Depends(get_db)) -> list[UserResponse]:
    return UserService(db).list_workspace_users(context.tenant_id)


@router.post("", response_model=UserResponse)
def create_user(
    payload: UserCreate, context: TenantScope, db: Session = Depends(get_db)
) -> UserResponse:
    return UserService(db).create_workspace_user(context, payload)

