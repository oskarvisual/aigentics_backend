from pydantic import BaseModel, Field

from app.core.enums import ToolPermissionMode


class RiskEvaluation(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    rationale: str
    sensitive_write: bool = False
    missing_information: bool = False
    repeated_failures: bool = False
    customer_escalation_signal: bool = False


class ActionProposal(BaseModel):
    title: str
    summary: str
    tool_name: str | None = None
    tool_input: dict = Field(default_factory=dict)
    execution_mode: ToolPermissionMode
    requires_approval: bool
    human_handoff_recommended: bool = False


class ConversationTriage(BaseModel):
    category: str
    urgency: str
    needs_human: bool
    missing_context: list[str] = Field(default_factory=list)
    next_step: str


class KnowledgeGapSummary(BaseModel):
    has_gap: bool
    missing_topics: list[str] = Field(default_factory=list)
    suggested_sources: list[str] = Field(default_factory=list)


class ManagerInsightSummary(BaseModel):
    title: str
    severity: str
    summary: str
    recommended_actions: list[str] = Field(default_factory=list)
    counts: dict = Field(default_factory=dict)

