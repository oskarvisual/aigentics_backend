from pydantic import BaseModel

from app.core.enums import ToolPermissionMode, ToolRiskLevel

RISK_ORDER = {
    ToolRiskLevel.LOW: 1,
    ToolRiskLevel.MEDIUM: 2,
    ToolRiskLevel.HIGH: 3,
    ToolRiskLevel.CRITICAL: 4,
}


class PolicyEvaluationInput(BaseModel):
    tool_permission_mode: ToolPermissionMode
    tool_risk_level: ToolRiskLevel
    requires_approval: bool = False
    confidence: float = 1.0
    repeated_failures: int = 0
    missing_information: bool = False
    sensitive_write: bool = False
    customer_frustration_signal: bool = False


class PolicyEvaluationResult(BaseModel):
    decision: ToolPermissionMode
    reason: str
    human_handoff: bool = False


class PolicyEngine:
    def evaluate(self, data: PolicyEvaluationInput) -> PolicyEvaluationResult:
        if data.customer_frustration_signal:
            return PolicyEvaluationResult(
                decision=ToolPermissionMode.HUMAN_ONLY,
                reason="Customer escalation or frustration requires human intervention.",
                human_handoff=True,
            )
        if data.missing_information or data.repeated_failures >= 3:
            return PolicyEvaluationResult(
                decision=ToolPermissionMode.SUPERVISED,
                reason="Insufficient context or repeated failures require supervised execution.",
                human_handoff=data.repeated_failures >= 5,
            )
        if data.sensitive_write or data.requires_approval:
            return PolicyEvaluationResult(
                decision=ToolPermissionMode.APPROVAL_REQUIRED,
                reason="Sensitive write requires explicit approval.",
            )
        if data.confidence < 0.55:
            return PolicyEvaluationResult(
                decision=ToolPermissionMode.SUPERVISED,
                reason="Low confidence requires human supervision.",
            )
        if RISK_ORDER[data.tool_risk_level] >= RISK_ORDER[ToolRiskLevel.HIGH]:
            return PolicyEvaluationResult(
                decision=ToolPermissionMode.APPROVAL_REQUIRED,
                reason="High-risk tool invocation requires approval.",
            )
        return PolicyEvaluationResult(
            decision=data.tool_permission_mode,
            reason="Action is allowed under the configured agent policy.",
        )

