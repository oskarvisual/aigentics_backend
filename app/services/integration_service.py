from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import AuditActorType, CredentialType, WorkspaceRole
from app.models.integration import (
    IntegrationCredentialsReference,
    IntegrationTemplate,
    TenantIntegration,
)
from app.models.tool import ToolDefinition
from app.schemas.integration import TenantIntegrationCreate
from app.services.audit_service import AuditService
from app.services.base import TenantContext, ensure_role


class IntegrationService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditService(db)

    def list_templates(self) -> list[IntegrationTemplate]:
        return list(
            self.db.scalars(
                select(IntegrationTemplate).where(IntegrationTemplate.is_active.is_(True))
            )
        )

    def list_tenant_integrations(self, tenant_id: str) -> list[TenantIntegration]:
        return list(
            self.db.scalars(
                select(TenantIntegration)
                .where(TenantIntegration.tenant_id == tenant_id)
                .order_by(TenantIntegration.created_at.desc())
            )
        )

    def create_tenant_integration(
        self, context: TenantContext, payload: TenantIntegrationCreate
    ) -> TenantIntegration:
        ensure_role(context, [WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.MANAGER])

        credentials_reference_id: str | None = None
        if payload.credentials_secret_path:
            credentials = IntegrationCredentialsReference(
                tenant_id=context.tenant_id,
                provider="custom",
                credential_type=CredentialType.CUSTOM,
                secret_path=payload.credentials_secret_path,
            )
            self.db.add(credentials)
            self.db.flush()
            credentials_reference_id = credentials.id

        integration = TenantIntegration(
            tenant_id=context.tenant_id,
            template_id=payload.template_id,
            credentials_reference_id=credentials_reference_id,
            name=payload.name,
            ownership_type=payload.ownership_type,
            external_account_id=payload.external_account_id,
            config=payload.config,
        )
        self.db.add(integration)
        self.db.flush()
        self.audit.log(
            tenant_id=context.tenant_id,
            actor_type=AuditActorType.USER,
            actor_user_id=context.user.id,
            actor_agent_id=None,
            action="integration.create",
            entity_type="tenant_integration",
            entity_id=integration.id,
        )
        self.db.commit()
        self.db.refresh(integration)
        return integration

    def list_tools(self, tenant_id: str) -> list[ToolDefinition]:
        return list(
            self.db.scalars(
                select(ToolDefinition).where(
                    (ToolDefinition.tenant_id.is_(None)) | (ToolDefinition.tenant_id == tenant_id)
                )
            )
        )

