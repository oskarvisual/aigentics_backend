from __future__ import annotations

from dataclasses import dataclass

from pydantic_ai import Agent, RunContext

from app.agents.schemas import ActionProposal, ManagerInsightSummary
from app.core.config import get_settings
from app.knowledge.retrieval import RetrievalService
from app.tools.registry import ToolRegistryService


@dataclass
class AgentRuntimeDeps:
    tenant_id: str
    agent_id: str | None
    retrieval_service: RetrievalService
    tool_registry: ToolRegistryService


class WorkforceAgentRuntime:
    """Factory for role-specific PydanticAI agents with structured outputs."""

    def __init__(self) -> None:
        settings = get_settings()
        self.default_model = settings.default_agent_model_openai
        self.manager_model = settings.default_agent_model_gemini

    def build_worker_agent(self) -> Agent[AgentRuntimeDeps, ActionProposal]:
        agent = Agent(
            self.default_model,
            deps_type=AgentRuntimeDeps,
            output_type=ActionProposal,
            system_prompt=(
                "You are a workforce agent operating in a supervised enterprise SaaS platform. "
                "Prefer structured action proposals, obey tool constraints, and do not invent tools."
            ),
        )

        @agent.tool
        def search_knowledge(ctx: RunContext[AgentRuntimeDeps], query: str) -> list[dict]:
            results = ctx.deps.retrieval_service.search(
                tenant_id=ctx.deps.tenant_id,
                agent_id=ctx.deps.agent_id,
                query=query,
                limit=5,
            )
            return [result.model_dump() for result in results]

        @agent.tool
        def list_allowed_tools(ctx: RunContext[AgentRuntimeDeps]) -> list[dict]:
            return [
                tool.model_dump()
                for tool in ctx.deps.tool_registry.list_agent_tools(
                    tenant_id=ctx.deps.tenant_id, agent_id=ctx.deps.agent_id
                )
            ]

        return agent

    def build_manager_agent(self) -> Agent[AgentRuntimeDeps, ManagerInsightSummary]:
        return Agent(
            self.manager_model,
            deps_type=AgentRuntimeDeps,
            output_type=ManagerInsightSummary,
            system_prompt=(
                "You are the Agent Manager. Focus on operational health, pending work, knowledge gaps, "
                "approval bottlenecks, integration failures, and actionable recommendations for admins."
            ),
        )
