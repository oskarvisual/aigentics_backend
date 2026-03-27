from pydantic import BaseModel, Field

from app.core.enums import (
    CredentialType,
    IntegrationConnectionStatus,
    IntegrationOwnershipType,
    IntegrationType,
    ToolPermissionMode,
    ToolRiskLevel,
)
from app.schemas.common import TimestampedResponse


class IntegrationTemplateResponse(TimestampedResponse):
    slug: str
    name: str
    provider: str
    integration_type: IntegrationType
    ownership_type: IntegrationOwnershipType
    auth_type: CredentialType
    description: str
    tool_generation_strategy: str
    config_schema: dict
    logo_url: str | None
    is_active: bool


class TenantIntegrationCreate(BaseModel):
    template_id: str
    name: str = Field(min_length=2, max_length=255)
    ownership_type: IntegrationOwnershipType = IntegrationOwnershipType.TENANT_PRIVATE
    external_account_id: str | None = None
    config: dict = Field(default_factory=dict)
    credentials_secret_path: str | None = None


class TenantIntegrationResponse(TimestampedResponse):
    tenant_id: str
    template_id: str
    credentials_reference_id: str | None
    name: str
    status: IntegrationConnectionStatus
    ownership_type: IntegrationOwnershipType
    external_account_id: str | None
    config: dict
    last_error: str | None
    is_shared_connection: bool


class ToolDefinitionResponse(TimestampedResponse):
    tenant_id: str | None
    integration_template_id: str | None
    name: str
    slug: str
    display_name: str
    description: str
    input_schema: dict
    output_schema: dict
    tags: list
    risk_level: ToolRiskLevel
    permission_mode: ToolPermissionMode
    implementation_type: str
    source_kind: str
    is_active: bool


class OpenAPIToolDraft(BaseModel):
    operation_id: str
    path: str
    method: str
    name: str
    description: str
    input_schema: dict
    risk_level: ToolRiskLevel = ToolRiskLevel.MEDIUM
    permission_mode: ToolPermissionMode = ToolPermissionMode.SUPERVISED

