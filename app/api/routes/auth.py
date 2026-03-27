from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.db.session import get_db
from app.models.identity import TenantMembership
from app.schemas.auth import AuthenticatedUser, LoginRequest, RefreshRequest, RegisterRequest, TokenPair
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=AuthenticatedUser)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthenticatedUser:
    return AuthService(db).register(payload)


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenPair:
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    return AuthService(db).login(payload, user_agent=user_agent, ip_address=ip_address)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenPair:
    return AuthService(db).refresh(payload.refresh_token, payload.tenant_id)


@router.get("/me", response_model=AuthenticatedUser)
def me(current_user: CurrentUser, db: Session = Depends(get_db)) -> AuthenticatedUser:
    membership = db.query(TenantMembership).filter(TenantMembership.user_id == current_user.id).first()
    if membership is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User has no workspace membership.")
    return AuthenticatedUser(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        tenant_id=membership.tenant_id,
        role=membership.role,
    )
