from pydantic import BaseModel, EmailStr, Field

from app.core.enums import WorkspaceRole
from app.schemas.common import TimestampedResponse


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    role: WorkspaceRole


class UserResponse(TimestampedResponse):
    email: EmailStr
    full_name: str
    is_active: bool

