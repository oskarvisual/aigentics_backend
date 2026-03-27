from pydantic import BaseModel


class DashboardSummary(BaseModel):
    agents_active: int
    pending_approvals: int
    open_conversations: int
    knowledge_sources_processing: int
    unread_notifications: int

