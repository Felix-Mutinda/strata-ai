from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, AsyncIterator

from strata_ai.core.models import AgentState, AgentResult, AgentDefinition


class AgentRuntime(ABC):
    """Contract every runtime adapter must fulfil. Agent patterns are framework-agnostic."""

    @abstractmethod
    async def compile(self, definition: AgentDefinition) -> Any:
        """Compile an agent definition into a runnable graph/state machine."""

    @abstractmethod
    async def run(
        self,
        compiled_agent: Any,
        input: Dict[str, Any],
        config: Dict[str, Any] | None = None,
    ) -> AgentResult:
        """Execute the agent until completion or pause."""

    @abstractmethod
    def stream(
        self,
        compiled_agent: Any,
        input: Dict[str, Any],
        config: Dict[str, Any] | None = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Yield intermediate events. Implementations should be async generators."""

    @abstractmethod
    async def checkpoint(self, thread_id: str, state: AgentState) -> None:
        """Persist state for HITL or long-running agents."""

    @abstractmethod
    async def resume(self, thread_id: str, human_input: Dict[str, Any]) -> AgentResult:
        """Resume a paused agent run with human input."""
