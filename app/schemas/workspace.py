from pydantic import BaseModel, Field

from app.core.enums import TenantStatus, WorkspaceRole
from app.schemas.common import TimestampedResponse


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    slug: str = Field(min_length=2, max_length=100)


class WorkspaceResponse(TimestampedResponse):
    slug: str
    name: str
    status: TenantStatus
    branding_settings: dict
    workspace_settings: dict


class MembershipResponse(TimestampedResponse):
    tenant_id: str
    user_id: str
    role: WorkspaceRole
    permissions: dict
    is_default_workspace: bool

