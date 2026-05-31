# sdk/src/strata_ai/agent/patterns.py
from __future__ import annotations
from typing import Any, Dict

from strata_ai.core.agent import BaseAgent
from strata_ai.core.models import AgentState, AgentDefinition, AgentConfig
from strata_ai.runtime.base import AgentRuntime
from strata_ai.core.tool import Tool


class ReActAgent(BaseAgent):
    """
    ReAct: Synergizing Reasoning and Acting in Language Models.
    Loop: Thought → Action → Observation → Thought → ...
    """

    def __init__(
        self,
        config: AgentConfig,
        runtime: AgentRuntime,
        tools: list[Tool] | None = None,
        memory: Any = None,
        guardrails: list[Any] | None = None,
    ):
        super().__init__(
            config=config,
            runtime=runtime,
            tools=tools,
            memory=memory,
            guardrails=guardrails,
        )

    def _build_definition(self) -> AgentDefinition:
        return AgentDefinition(
            config=self.config,
            state_schema=AgentState,
            nodes=[
                {"name": "reason", "fn": self._reason_node},
                {"name": "act", "fn": self._tool_node},
            ],
            edges=[("act", "reason")],
            conditional_edges=[
                ("reason", self._should_continue, {"continue": "act", "end": "__end__"})
            ],
            entry_point="reason",
        )

    async def _reason_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder: LLM generates next thought/action
        return {"messages": [{"role": "assistant", "content": "Reasoning..."}]}

    async def _tool_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder: Executes selected tool
        return {"messages": [{"role": "tool", "content": "Tool executed"}]}

    def _should_continue(self, state: Dict[str, Any]) -> str:
        # Mock termination condition for deterministic testing
        return "end" if len(state.get("messages", [])) > 5 else "continue"
