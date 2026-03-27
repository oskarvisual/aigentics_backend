from fastapi import APIRouter

from app.api.deps import TenantScope
from app.schemas.upload import UploadCreateRequest, UploadTargetResponse
from app.services.upload_service import UploadService

router = APIRouter()


@router.post("", response_model=UploadTargetResponse)
def create_upload_target(
    payload: UploadCreateRequest, context: TenantScope
) -> UploadTargetResponse:
    return UploadService().create_upload_target(context.tenant_id, payload)

