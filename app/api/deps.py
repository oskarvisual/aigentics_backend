from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.identity import TenantMembership, User
from app.services.base import TenantContext

bearer_scheme = HTTPBearer(auto_error=False)


DbSession = Annotated[Session, Depends(get_db)]


def get_access_payload(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials.")
    try:
        return decode_access_token(credentials.credentials)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token.") from exc


AccessPayload = Annotated[dict, Depends(get_access_payload)]


def get_current_user(
    db: DbSession, credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]
) -> User:
    payload = get_access_payload(credentials)
    user = db.scalar(select(User).where(User.id == payload["sub"], User.is_active.is_(True)))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_tenant_context(
    db: DbSession,
    current_user: CurrentUser,
    access_payload: AccessPayload,
    x_workspace_id: Annotated[str | None, Header(alias="X-Workspace-ID")] = None,
) -> TenantContext:
    if not x_workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Workspace-ID header is required for workspace-scoped endpoints.",
        )
    if access_payload.get("tenant_id") and access_payload["tenant_id"] != x_workspace_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access token is scoped to a different workspace.",
        )
    membership = db.scalar(
        select(TenantMembership).where(
            TenantMembership.user_id == current_user.id, TenantMembership.tenant_id == x_workspace_id
        )
    )
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace.",
        )
    return TenantContext(tenant_id=x_workspace_id, user=current_user, membership=membership)


TenantScope = Annotated[TenantContext, Depends(get_tenant_context)]
