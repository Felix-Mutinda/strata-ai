from __future__ import annotations
from typing import Any, Dict, AsyncIterator

from strata_ai.runtime.base import AgentRuntime
from strata_ai.core.models import AgentState, AgentResult, AgentDefinition


class MockRuntime(AgentRuntime):
    """In-memory, deterministic runtime for unit tests and local dev."""

    def __init__(self) -> None:
        self._store: Dict[str, AgentState] = {}

    async def compile(self, definition: AgentDefinition) -> Any:
        return {"definition": definition, "compiled_at": "mock"}

    async def run(
        self,
        compiled_agent: Any,
        input: Dict[str, Any],
        config: Dict[str, Any] | None = None,
    ) -> AgentResult:
        thread_id = config.get("thread_id", "mock-thread") if config else "mock-thread"
        return AgentResult(
            thread_id=thread_id,
            status="done",
            output=f"[mock] processed by {compiled_agent['definition'].config.name}",
            metadata={"runtime": "mock", "iterations": 1, "mock_input": input},
        )

    async def stream(
        self,
        compiled_agent: Any,
        input: Dict[str, Any],
        config: Dict[str, Any] | None = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        tid = config.get("thread_id", "mock-stream") if config else "mock-stream"
        yield {"event": "start", "thread_id": tid}
        yield {"event": "step", "node": "mock_reasoning"}
        yield {"event": "end", "status": "done"}

    async def checkpoint(self, thread_id: str, state: AgentState) -> None:
        state.thread_id = thread_id
        self._store[thread_id] = state

    async def resume(self, thread_id: str, human_input: Dict[str, Any]) -> AgentResult:
        state = self._store.get(thread_id)
        if not state:
            return AgentResult(
                thread_id=thread_id, status="error", error="Checkpoint not found"
            )

        state.status = "done"
        state.context["human_input"] = human_input
        return AgentResult(
            thread_id=thread_id,
            status="done",
            output=f"[mock] resumed with {human_input}",
            metadata={"runtime": "mock", "resumed": True},
        )
