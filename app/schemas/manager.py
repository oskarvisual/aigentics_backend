from app.core.enums import ManagerInsightSeverity
from app.schemas.common import TimestampedResponse


class ManagerInsightResponse(TimestampedResponse):
    tenant_id: str
    tenant_agent_id: str | None
    severity: ManagerInsightSeverity
    category: str
    title: str
    summary: str
    insight_payload: dict
    dismissed: bool
