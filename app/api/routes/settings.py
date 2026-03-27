from fastapi import APIRouter

from app.api.deps import TenantScope

router = APIRouter()


@router.get("/workspace")
def workspace_settings(context: TenantScope) -> dict:
    return {
        "tenant_id": context.tenant_id,
        "role": context.role,
        "branding": context.membership.tenant.branding_settings if context.membership.tenant else {},
        "workspace_settings": context.membership.tenant.workspace_settings
        if context.membership.tenant
        else {},
    }

