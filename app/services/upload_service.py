from pathlib import Path
from uuid import uuid4

from app.knowledge.storage import ObjectStorageService
from app.schemas.upload import UploadCreateRequest, UploadTargetResponse


class UploadService:
    def __init__(self) -> None:
        self.storage = ObjectStorageService()

    def create_upload_target(self, tenant_id: str, payload: UploadCreateRequest) -> UploadTargetResponse:
        suffix = Path(payload.filename).suffix
        object_key = f"{tenant_id}/uploads/{uuid4()}{suffix}"
        return UploadTargetResponse(
            object_key=object_key,
            upload_url=self.storage.presign_upload(object_key),
        )
