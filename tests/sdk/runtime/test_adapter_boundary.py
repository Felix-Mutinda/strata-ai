import pytest
from typing import cast

from strata_ai.core.models import AgentState
from strata_ai.core.messages import AgentMessage
from strata_ai.runtime.langgraph_adapter import LangGraphAdapter, GraphState

class TestAdapterBoundaryMapping:
    def setup_method(self):
        self.adapter = LangGraphAdapter()

    def test_core_to_graph_roundtrip(self):
        core_state = AgentState(
            messages=[AgentMessage(role="user", content="test")],
            context={"key": "val"},
            status="running",
            thread_id="t1"
        )
        
        # Returns GraphState (TypedDict)
        graph = self.adapter._to_graph_state(core_state)
        
        # Safe access for TypedDict keys
        assert len(graph.get("messages", [])) == 1
        assert graph.get("context", {}).get("key") == "val"
        assert graph.get("status") == "running"

    def test_graph_to_core_validation(self):
        # Create a dict that matches GraphState shape
        graph_state_dict = {
            "messages": [
                {"role": "user", "content": "test", "tool_calls": [], "tool_result": None, "metadata": {}}
            ],
            "context": {"key": "val"},
            "metadata": {},
            "status": "done",
            "thread_id": "t1"
        }
        
        # Cast to GraphState to satisfy type checker
        graph_state = cast(GraphState, graph_state_dict)
        
        core = self.adapter._to_core_state(graph_state)
        
        assert isinstance(core.messages[0], AgentMessage)
        assert core.status == "done"

    def test_invalid_graph_state_raises(self):
        # Structurally valid dict, but semantically invalid for AgentMessage (invalid role)
        bad_state_dict = {
            "messages": [
                {"role": "invalid_role", "content": "x", "tool_calls": [], "tool_result": None, "metadata": {}}
            ],
            "context": {}, 
            "metadata": {}, 
            "status": "x", 
            "thread_id": "t1"
        }
        
        # Pydantic will raise ValidationError during _to_core_state -> AgentMessage.model_validate
        with pytest.raises(Exception): 
            self.adapter._to_core_state(cast(GraphState, bad_state_dict))

    def test_checkpoint_stores_mapped_state(self):
        core = AgentState(
            messages=[], 
            context={}, 
            metadata={}, 
            status="paused", 
            thread_id="ck-1"
        )
        
        self.adapter._store["ck-1"] = self.adapter._to_graph_state(core)
        graph = self.adapter._store["ck-1"]
        
        assert graph.get("thread_id") == "ck-1"
        assert graph.get("status") == "paused"