from app.approvals.policy_engine import PolicyEngine, PolicyEvaluationInput
from app.core.enums import ToolPermissionMode, ToolRiskLevel


def test_high_risk_tool_requires_approval() -> None:
    result = PolicyEngine().evaluate(
        PolicyEvaluationInput(
            tool_permission_mode=ToolPermissionMode.AUTONOMOUS,
            tool_risk_level=ToolRiskLevel.HIGH,
        )
    )
    assert result.decision == ToolPermissionMode.APPROVAL_REQUIRED


def test_customer_frustration_triggers_handoff() -> None:
    result = PolicyEngine().evaluate(
        PolicyEvaluationInput(
            tool_permission_mode=ToolPermissionMode.SUPERVISED,
            tool_risk_level=ToolRiskLevel.LOW,
            customer_frustration_signal=True,
        )
    )
    assert result.human_handoff is True
    assert result.decision == ToolPermissionMode.HUMAN_ONLY

