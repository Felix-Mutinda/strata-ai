# sdk/src/strata_ai/runtime/langgraph_adapter.py
from __future__ import annotations
from typing import Any, Dict, AsyncIterator, TypedDict, Annotated, Optional

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from strata_ai.runtime.base import AgentRuntime
from strata_ai.core.models import AgentState, AgentResult, AgentDefinition
from strata_ai.core.messages import AgentMessage


def _langgraph_append_messages(left: list, right: list) -> list:
    """LangGraph-compatible list reducer. Bypasses strict OpenAI parser."""
    return left + right


class GraphState(TypedDict, total=False):
    messages: Annotated[list, _langgraph_append_messages]
    context: dict
    metadata: dict
    status: str
    thread_id: Optional[str]


class LangGraphAdapter(AgentRuntime):
    """Translates Strata AI agent definitions to LangGraph StateGraphs."""

    def __init__(self, checkpointer: Any = None) -> None:
        self._checkpointer = checkpointer or MemorySaver()
        self._store: Dict[str, Any] = {}

    def _to_graph_state(self, core_state: AgentState) -> GraphState:
        """Pydantic → TypedDict boundary mapping."""
        return {
            "messages": [m.model_dump() for m in core_state.messages],
            "context": core_state.context,
            "metadata": core_state.metadata,
            "status": core_state.status,
            "thread_id": core_state.thread_id,
        }

    def _to_core_state(self, graph_state: GraphState) -> AgentState:
        """TypedDict → Pydantic boundary validation."""
        messages = [
            AgentMessage.model_validate(m) for m in graph_state.get("messages", [])
        ]
        return AgentState(
            messages=messages,
            context=graph_state.get("context", {}),
            metadata=graph_state.get("metadata", {}),
            status=graph_state.get("status", "running"),
            thread_id=graph_state.get("thread_id"),
        )

    async def compile(self, definition: AgentDefinition) -> Any:
        graph = StateGraph(GraphState)

        for node in definition.nodes:
            graph.add_node(node["name"], node["fn"])

        for src, dst in definition.edges:
            graph.add_edge(src, dst)

        for src, condition_fn, mapping in definition.conditional_edges:
            target_map = {
                k: (END if v in ("END", "__end__") else v) for k, v in mapping.items()
            }
            graph.add_conditional_edges(src, condition_fn, target_map)

        if definition.entry_point is None:
            raise ValueError("AgentDefinition.entry_point must be set.")

        graph.set_entry_point(definition.entry_point)
        return graph.compile(checkpointer=self._checkpointer)

    async def run(
        self,
        compiled_agent: Any,
        input: Dict[str, Any],
        config: Dict[str, Any] | None = None,
    ) -> AgentResult:
        thread_id = (
            config.get("thread_id", "default-thread") if config else "default-thread"
        )
        try:
            initial = {
                "messages": [],
                "context": {},
                "metadata": {},
                "status": "running",
                "thread_id": thread_id,
            }
            output = await compiled_agent.ainvoke(
                initial | input, config={"configurable": {"thread_id": thread_id}}
            )
            return AgentResult(
                thread_id=thread_id,
                status="done",
                output=output,
                metadata={
                    "runtime": "langgraph",
                    "checkpointer": type(self._checkpointer).__name__,
                },
            )
        except Exception as e:
            return AgentResult(thread_id=thread_id, status="error", error=str(e))

    async def stream(
        self,
        compiled_agent: Any,
        input: Dict[str, Any],
        config: Dict[str, Any] | None = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        thread_id = (
            config.get("thread_id", "stream-thread") if config else "stream-thread"
        )
        async for event in compiled_agent.astream(
            input, config={"configurable": {"thread_id": thread_id}}
        ):
            yield event

    async def checkpoint(self, thread_id: str, state: AgentState) -> None:
        state.thread_id = thread_id
        self._store[thread_id] = self._to_graph_state(state)

    async def resume(self, thread_id: str, human_input: Dict[str, Any]) -> AgentResult:
        graph_state = self._store.get(thread_id)
        if not graph_state:
            return AgentResult(
                thread_id=thread_id, status="error", error="Checkpoint not found"
            )

        graph_state["status"] = "done"
        graph_state["context"]["human_input"] = human_input
        return AgentResult(
            thread_id=thread_id,
            status="done",
            output={"resumed_with": human_input},
            metadata={"runtime": "langgraph", "resumed": True},
        )
