from sqlalchemy import select

from app.core.enums import (
    CredentialType,
    IntegrationOwnershipType,
    IntegrationType,
    ToolPermissionMode,
    ToolRiskLevel,
)
from app.db.session import SessionLocal
from app.models.agent import AgentTemplate
from app.models.integration import IntegrationTemplate
from app.models.tool import ToolDefinition


DEFAULT_AGENT_TEMPLATES = [
    {
        "slug": "secretary-agent",
        "name": "Secretary Agent",
        "role_title": "Executive Secretary",
        "description": "Handles scheduling, inbox coordination, note taking, and follow-up drafting.",
        "default_system_prompt": "Operate as an executive secretary for business stakeholders.",
        "capability_tags": ["calendar", "email", "task-triage"],
    },
    {
        "slug": "support-agent",
        "name": "Support Agent",
        "role_title": "Support Specialist",
        "description": "Handles support triage, retrieval, and supervised response drafting.",
        "default_system_prompt": "Operate as a customer support specialist with strong escalation discipline.",
        "capability_tags": ["support", "faq", "handoff"],
    },
    {
        "slug": "sales-agent",
        "name": "Sales Agent",
        "role_title": "Sales Development Representative",
        "description": "Qualifies leads, drafts outreach, and updates CRM tools under policy.",
        "default_system_prompt": "Operate as a consultative sales development representative.",
        "capability_tags": ["crm", "lead-qualification", "outreach"],
    },
    {
        "slug": "customer-success-agent",
        "name": "Customer Success Agent",
        "role_title": "Customer Success Manager",
        "description": "Monitors renewals, adoption signals, and onboarding gaps.",
        "default_system_prompt": "Operate as a proactive customer success manager.",
        "capability_tags": ["renewals", "health", "onboarding"],
    },
    {
        "slug": "recruiter-agent",
        "name": "Recruiter Agent",
        "role_title": "Recruiter",
        "description": "Coordinates candidate screening, ATS updates, and scheduling.",
        "default_system_prompt": "Operate as a recruiter coordinating candidate workflows.",
        "capability_tags": ["ats", "sourcing", "screening"],
    },
    {
        "slug": "agent-manager",
        "name": "Agent Manager",
        "role_title": "Digital Workforce Manager",
        "description": "Monitors the digital workforce and advises workspace leaders.",
        "default_system_prompt": "Operate as the internal manager of an AI workforce.",
        "capability_tags": ["ops", "insights", "approvals"],
        "is_manager_template": True,
    },
]

DEFAULT_INTEGRATIONS = [
    {
        "slug": "gmail",
        "name": "Gmail",
        "provider": "google",
        "integration_type": IntegrationType.NATIVE,
        "ownership_type": IntegrationOwnershipType.THIRD_PARTY_SHARED,
        "auth_type": CredentialType.OAUTH_TOKEN,
        "description": "Email inbox access and thread operations.",
        "tool_generation_strategy": "native",
    },
    {
        "slug": "slack",
        "name": "Slack",
        "provider": "slack",
        "integration_type": IntegrationType.NATIVE,
        "ownership_type": IntegrationOwnershipType.THIRD_PARTY_SHARED,
        "auth_type": CredentialType.OAUTH_TOKEN,
        "description": "Workspace messaging and notifications.",
        "tool_generation_strategy": "native",
    },
    {
        "slug": "openapi-import",
        "name": "OpenAPI Import",
        "provider": "custom",
        "integration_type": IntegrationType.OPENAPI_IMPORTED,
        "ownership_type": IntegrationOwnershipType.TENANT_PRIVATE,
        "auth_type": CredentialType.CUSTOM,
        "description": "Transforms imported API specs into normalized tenant tools.",
        "tool_generation_strategy": "openapi",
    },
]

DEFAULT_TOOLS = [
    {
        "slug": "gmail.read_thread",
        "name": "gmail.read_thread",
        "display_name": "Read Gmail Thread",
        "description": "Read a Gmail thread through a normalized tenant binding.",
        "risk_level": ToolRiskLevel.LOW,
        "permission_mode": ToolPermissionMode.SUPERVISED,
    },
    {
        "slug": "gmail.send_reply",
        "name": "gmail.send_reply",
        "display_name": "Send Gmail Reply",
        "description": "Send an email reply through a normalized tenant binding.",
        "risk_level": ToolRiskLevel.HIGH,
        "permission_mode": ToolPermissionMode.APPROVAL_REQUIRED,
    },
]


def seed() -> None:
    db = SessionLocal()
    try:
        for template_data in DEFAULT_AGENT_TEMPLATES:
            existing = db.scalar(
                select(AgentTemplate).where(AgentTemplate.slug == template_data["slug"])
            )
            if existing is None:
                db.add(
                    AgentTemplate(
                        slug=template_data["slug"],
                        name=template_data["name"],
                        role_title=template_data["role_title"],
                        description=template_data["description"],
                        default_system_prompt=template_data["default_system_prompt"],
                        capability_tags=template_data["capability_tags"],
                        is_manager_template=template_data.get("is_manager_template", False),
                    )
                )

        for integration_data in DEFAULT_INTEGRATIONS:
            existing = db.scalar(
                select(IntegrationTemplate).where(IntegrationTemplate.slug == integration_data["slug"])
            )
            if existing is None:
                db.add(IntegrationTemplate(**integration_data))

        for tool_data in DEFAULT_TOOLS:
            existing = db.scalar(select(ToolDefinition).where(ToolDefinition.slug == tool_data["slug"]))
            if existing is None:
                db.add(
                    ToolDefinition(
                        name=tool_data["name"],
                        slug=tool_data["slug"],
                        display_name=tool_data["display_name"],
                        description=tool_data["description"],
                        risk_level=tool_data["risk_level"],
                        permission_mode=tool_data["permission_mode"],
                    )
                )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()

