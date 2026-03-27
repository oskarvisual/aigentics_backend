from pydantic import BaseModel, Field


class UploadCreateRequest(BaseModel):
    filename: str = Field(min_length=1)
    content_type: str = Field(min_length=1)


class UploadTargetResponse(BaseModel):
    object_key: str
    upload_url: str

