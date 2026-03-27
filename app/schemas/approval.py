from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enums import ApprovalStatus
from app.schemas.common import TimestampedResponse


class ApprovalRequestCreate(BaseModel):
    tenant_agent_id: str | None = None
    conversation_id: str | None = None
    action_type: str = Field(min_length=2, max_length=150)
    reason: str = Field(min_length=3)
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    request_payload: dict = Field(default_factory=dict)
    expires_at: datetime | None = None


class ApprovalDecision(BaseModel):
    decision_payload: dict = Field(default_factory=dict)


class ApprovalRequestResponse(TimestampedResponse):
    tenant_id: str
    tenant_agent_id: str | None
    requested_by_user_id: str | None
    conversation_id: str | None
    action_type: str
    reason: str
    risk_score: float
    status: ApprovalStatus
    request_payload: dict
    decision_payload: dict
    expires_at: datetime | None
    resolved_by_user_id: str | None
    resolved_at: datetime | None

