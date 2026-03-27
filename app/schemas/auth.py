from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    workspace_name: str = Field(min_length=2, max_length=255)
    workspace_slug: str = Field(min_length=2, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    tenant_id: str


class RefreshRequest(BaseModel):
    refresh_token: str
    tenant_id: str


class TokenPair(ORMModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthenticatedUser(ORMModel):
    id: str
    email: EmailStr
    full_name: str
    tenant_id: str
    role: str

