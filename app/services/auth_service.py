from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import AuditActorType, WorkspaceRole
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models.identity import RefreshTokenSession, Tenant, TenantMembership, User
from app.schemas.auth import AuthenticatedUser, LoginRequest, RegisterRequest, TokenPair
from app.services.audit_service import AuditService


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditService(db)

    def register(self, payload: RegisterRequest) -> AuthenticatedUser:
        existing_user = self.db.scalar(select(User).where(User.email == payload.email))
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists.")

        tenant = Tenant(slug=payload.workspace_slug, name=payload.workspace_name)
        user = User(
            email=payload.email,
            full_name=payload.full_name,
            password_hash=hash_password(payload.password),
        )
        self.db.add_all([tenant, user])
        self.db.flush()

        membership = TenantMembership(
            tenant_id=tenant.id,
            user_id=user.id,
            role=WorkspaceRole.OWNER,
            permissions={"workspace": ["*"]},
            is_default_workspace=True,
            accepted_at=datetime.now(UTC),
        )
        self.db.add(membership)
        self.audit.log(
            tenant_id=tenant.id,
            actor_type=AuditActorType.USER,
            actor_user_id=user.id,
            actor_agent_id=None,
            action="auth.register",
            entity_type="tenant",
            entity_id=tenant.id,
        )
        self.db.commit()
        self.db.refresh(user)
        return AuthenticatedUser(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            tenant_id=tenant.id,
            role=membership.role,
        )

    def login(self, payload: LoginRequest, user_agent: str | None, ip_address: str | None) -> TokenPair:
        user = self.db.scalar(select(User).where(User.email == payload.email))
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

        membership = self.db.scalar(
            select(TenantMembership).where(
                TenantMembership.user_id == user.id, TenantMembership.tenant_id == payload.tenant_id
            )
        )
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of this workspace.",
            )

        access_token = create_access_token(user.id, tenant_id=payload.tenant_id)
        refresh_token, expires_at = create_refresh_token(user.id, session_id="")

        session = RefreshTokenSession(
            tenant_id=payload.tenant_id,
            user_id=user.id,
            token_hash=hash_password(refresh_token),
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at,
        )
        self.db.add(session)
        self.db.flush()

        refresh_token, expires_at = create_refresh_token(user.id, session_id=session.id)
        session.token_hash = hash_password(refresh_token)
        user.last_login_at = datetime.now(UTC)
        self.audit.log(
            tenant_id=payload.tenant_id,
            actor_type=AuditActorType.USER,
            actor_user_id=user.id,
            actor_agent_id=None,
            action="auth.login",
            entity_type="user",
            entity_id=user.id,
        )
        self.db.commit()
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    def refresh(self, refresh_token: str, tenant_id: str) -> TokenPair:
        payload = decode_refresh_token(refresh_token)
        session = self.db.scalar(select(RefreshTokenSession).where(RefreshTokenSession.id == payload["sid"]))
        if not session or session.tenant_id != tenant_id or session.revoked_at is not None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")
        if not verify_password(refresh_token, session.token_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")

        access_token = create_access_token(payload["sub"], tenant_id=tenant_id)
        new_refresh_token, expires_at = create_refresh_token(payload["sub"], session_id=session.id)
        session.token_hash = hash_password(new_refresh_token)
        session.expires_at = expires_at
        self.db.commit()
        return TokenPair(access_token=access_token, refresh_token=new_refresh_token)
