from enum import StrEnum


class WorkspaceRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    HUMAN_AGENT = "human_agent"
    VIEWER = "viewer"


class TenantStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class AgentStatus(StrEnum):
    DRAFT = "draft"
    ONBOARDING = "onboarding"
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class KnowledgeSourceType(StrEnum):
    PDF = "pdf"
    URL = "url"
    FAQ_PAGE = "faq_page"
    VIDEO = "video"
    CHAT = "chat"
    EMAIL_THREAD = "email_thread"
    TEXT = "text"
    DOC = "doc"


class ProcessingStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class IntegrationType(StrEnum):
    NATIVE = "native"
    MCP = "mcp"
    OPENAPI_IMPORTED = "openapi_imported"
    DOCUMENTATION_ASSISTED = "documentation_assisted"
    CUSTOM_API = "custom_api"
    BROWSER_FALLBACK = "browser_fallback"


class IntegrationOwnershipType(StrEnum):
    NATIVE = "native"
    THIRD_PARTY_SHARED = "third_party_shared"
    TENANT_PRIVATE = "tenant_private"


class IntegrationConnectionStatus(StrEnum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class CredentialType(StrEnum):
    OAUTH_TOKEN = "oauth_token"
    API_KEY = "api_key"
    SERVICE_ACCOUNT = "service_account"
    BASIC_AUTH = "basic_auth"
    CUSTOM = "custom"


class ToolRiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ToolPermissionMode(StrEnum):
    AUTONOMOUS = "autonomous"
    SUPERVISED = "supervised"
    APPROVAL_REQUIRED = "approval_required"
    HUMAN_ONLY = "human_only"


class ConversationType(StrEnum):
    AGENT_CHAT = "agent_chat"
    MANAGER_CHAT = "manager_chat"
    INBOX = "inbox"
    INTERNAL = "internal"


class ConversationStatus(StrEnum):
    OPEN = "open"
    PENDING = "pending"
    HANDOFF = "handoff"
    RESOLVED = "resolved"
    CLOSED = "closed"


class MessageRole(StrEnum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    TOOL = "tool"
    INTERNAL_NOTE = "internal_note"


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class AuditActorType(StrEnum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class NotificationType(StrEnum):
    INFO = "info"
    APPROVAL = "approval"
    INSIGHT = "insight"
    SYSTEM = "system"


class ManagerInsightSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ScheduledJobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

