import pytest
from typing import cast

from strata_ai.core.models import AgentState
from strata_ai.core.messages import AgentMessage
from strata_ai.runtime.langgraph_adapter import LangGraphAdapter, GraphState

class TestLangGraphAdapter:
    @pytest.mark.asyncio
    async def test_compiles_definition_to_graph(self):
        adapter = LangGraphAdapter()
        # Note: GraphState is used internally, but AgentDefinition uses AgentState
        # The adapter handles the translation.
        
        # We test that compile returns a valid object
        from strata_ai.core.models import AgentDefinition, AgentConfig
        config = AgentConfig(name="test-graph", model="mock:llm", instructions="test")
        
        # Define a simple node
        async def reason_node(state): return {"messages": [AgentMessage(role="assistant", content="thinking")]}

        definition = AgentDefinition(
            config=config,
            state_schema=AgentState, # Adapter ignores this and uses GraphState internally
            nodes=[{"name": "reason", "fn": reason_node}],
            edges=[],
            conditional_edges=[],
            entry_point="reason",
        )

        compiled = await adapter.compile(definition)
        assert compiled is not None
        assert hasattr(compiled, "ainvoke")  # LangGraph compiled graph exposes ainvoke

    @pytest.mark.asyncio
    async def test_checkpoint_and_resume_flow(self):
        adapter = LangGraphAdapter()
        thread_id = "hitl-thread-1"
        
        # Create valid AgentState with AgentMessage
        state = AgentState(
            messages=[AgentMessage(role="user", content="pause")], 
            status="awaiting_human"
        )
        
        await adapter.checkpoint(thread_id, state)
        
        # Resume flow
        result = await adapter.resume(thread_id, human_input={"approved": True})
        assert result.status == "done"
        assert result.metadata.get("resumed") is True