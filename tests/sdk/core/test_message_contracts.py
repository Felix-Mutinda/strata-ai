import pytest
from strata_ai.core.messages import AgentMessage, ToolCall, ToolResult, AgentEvent
from strata_ai.core.models import _append_messages

class TestAgentMessageContract:
    def test_user_message(self):
        msg = AgentMessage(role="user", content="What's the weather?")
        assert msg.role == "user"
        assert msg.tool_calls == []

    def test_tool_call_with_result(self):
        call = ToolCall(id="t1", name="get_weather", arguments={"city": "Nairobi"})
        result = ToolResult(tool_call_id="t1", output="Sunny", status="success")
        msg = AgentMessage(role="tool", tool_result=result, metadata={"tool_id": "t1"})
        
        # Fix: Assert optional field is present before accessing
        assert msg.tool_result is not None
        assert msg.tool_result.tool_call_id == "t1"
        assert msg.metadata["tool_id"] == "t1"

    def test_reducer_accumulates(self):
        m1 = AgentMessage(role="user", content="start")
        m2 = AgentMessage(role="assistant", content="done")
        accumulated = _append_messages([m1], [m2])
        assert len(accumulated) == 2
        assert accumulated[0].role == "user"

class TestAgentEventContract:
    def test_stream_event(self):
        event = AgentEvent(event_type="tool_call", thread_id="t1", node_name="act", data={"tool": "weather"})
        assert event.event_type == "tool_call"
        assert event.thread_id == "t1"