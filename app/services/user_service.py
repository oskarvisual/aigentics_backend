from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import AuditActorType, WorkspaceRole
from app.core.security import hash_password
from app.models.identity import TenantMembership, User
from app.schemas.user import UserCreate
from app.services.audit_service import AuditService
from app.services.base import TenantContext, ensure_role


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditService(db)

    def list_workspace_users(self, tenant_id: str) -> list[User]:
        return list(
            self.db.scalars(
                select(User)
                .join(TenantMembership, TenantMembership.user_id == User.id)
                .where(TenantMembership.tenant_id == tenant_id)
                .order_by(User.created_at)
            )
        )

    def create_workspace_user(self, context: TenantContext, payload: UserCreate) -> User:
        ensure_role(context, [WorkspaceRole.OWNER, WorkspaceRole.ADMIN])
        user = self.db.scalar(select(User).where(User.email == payload.email))
        if user is None:
            user = User(
                email=payload.email,
                full_name=payload.full_name,
                password_hash=hash_password(payload.password),
            )
            self.db.add(user)
            self.db.flush()

        membership = TenantMembership(
            tenant_id=context.tenant_id,
            user_id=user.id,
            role=payload.role,
            permissions={},
            invited_by_user_id=context.user.id,
        )
        self.db.add(membership)
        self.audit.log(
            tenant_id=context.tenant_id,
            actor_type=AuditActorType.USER,
            actor_user_id=context.user.id,
            actor_agent_id=None,
            action="user.invite",
            entity_type="user",
            entity_id=user.id,
        )
        self.db.commit()
        self.db.refresh(user)
        return user

