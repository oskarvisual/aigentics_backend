from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.enums import AgentStatus, ApprovalStatus, ConversationStatus, ProcessingStatus
from app.models.agent import TenantAgent
from app.models.approval import ApprovalRequest
from app.models.conversation import Conversation
from app.models.knowledge import KnowledgeSource
from app.models.operation import Notification
from app.schemas.analytics import DashboardSummary


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def dashboard_summary(self, tenant_id: str, user_id: str) -> DashboardSummary:
        agents_active = self.db.scalar(
            select(func.count()).select_from(TenantAgent).where(
                TenantAgent.tenant_id == tenant_id, TenantAgent.status == AgentStatus.ACTIVE
            )
        ) or 0
        pending_approvals = self.db.scalar(
            select(func.count()).select_from(ApprovalRequest).where(
                ApprovalRequest.tenant_id == tenant_id,
                ApprovalRequest.status == ApprovalStatus.PENDING,
            )
        ) or 0
        open_conversations = self.db.scalar(
            select(func.count()).select_from(Conversation).where(
                Conversation.tenant_id == tenant_id,
                Conversation.status.in_([ConversationStatus.OPEN, ConversationStatus.PENDING]),
            )
        ) or 0
        knowledge_sources_processing = self.db.scalar(
            select(func.count()).select_from(KnowledgeSource).where(
                KnowledgeSource.tenant_id == tenant_id,
                KnowledgeSource.status == ProcessingStatus.PROCESSING,
            )
        ) or 0
        unread_notifications = self.db.scalar(
            select(func.count()).select_from(Notification).where(
                Notification.tenant_id == tenant_id,
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
        ) or 0
        return DashboardSummary(
            agents_active=agents_active,
            pending_approvals=pending_approvals,
            open_conversations=open_conversations,
            knowledge_sources_processing=knowledge_sources_processing,
            unread_notifications=unread_notifications,
        )

