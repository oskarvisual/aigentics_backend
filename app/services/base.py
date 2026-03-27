from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.core.enums import WorkspaceRole
from app.models.identity import TenantMembership, User


class TenantContext:
    def __init__(self, tenant_id: str, user: User, membership: TenantMembership):
        self.tenant_id = tenant_id
        self.user = user
        self.membership = membership

    @property
    def role(self) -> WorkspaceRole:
        return self.membership.role


def ensure_role(context: TenantContext, allowed: Sequence[WorkspaceRole]) -> None:
    if context.role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission for this workspace action.",
        )


def tenant_query(statement: Select[tuple], tenant_id: str, model: type) -> Select[tuple]:
    return statement.where(model.tenant_id == tenant_id)

