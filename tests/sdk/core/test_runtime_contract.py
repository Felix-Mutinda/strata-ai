import pytest
from typing import Any, Dict

from strata_ai.core.models import AgentConfig, AgentState, AgentResult, AgentDefinition
from strata_ai.core.messages import AgentMessage  # Added import
from strata_ai.core.agent import BaseAgent
from strata_ai.runtime.base import AgentRuntime
from strata_ai.runtime.mock import MockRuntime


class _TestAgent(BaseAgent):
    """Thin concrete implementation to satisfy BaseAgent's abstract contract."""
    def _build_definition(self) -> AgentDefinition:
        return AgentDefinition(
            config=self.config,
            state_schema=AgentState,
            nodes=[],
            edges=[],
            entry_point=None,
        )


class TestAgentRuntimeABC:
    def test_cannot_instantiate_abstract_runtime(self):
        with pytest.raises(TypeError):
            AgentRuntime()  # type: ignore[abstract]

    def test_subclass_must_implement_abstract_methods(self):
        class IncompleteRuntime(AgentRuntime):
            pass
        with pytest.raises(TypeError):
            IncompleteRuntime()  # type: ignore[abstract]


class TestBaseAgentWithMockRuntime:
    @pytest.mark.asyncio
    async def test_run_returns_deterministic_result(self):
        config = AgentConfig(name="unit-agent", model="mock:llm", instructions="You are a test agent.")
        runtime = MockRuntime()
        agent = _TestAgent(config=config, runtime=runtime)

        result = await agent.run({"input": "hello"})
        assert isinstance(result, AgentResult)
        assert result.status == "done"
        assert result.thread_id is not None
        assert "unit-agent" in str(result.output)

    @pytest.mark.asyncio
    async def test_compile_is_idempotent(self):
        config = AgentConfig(name="compile-cache-test", model="mock:llm", instructions="test")
        runtime = MockRuntime()
        agent = _TestAgent(config=config, runtime=runtime)

        await agent.compile()
        first_ref = agent._compiled
        await agent.compile()
        assert agent._compiled is first_ref

    @pytest.mark.asyncio
    async def test_checkpoint_and_resume_flow(self):
        config = AgentConfig(name="hitl-mock", model="mock:llm", instructions="test")
        runtime = MockRuntime()
        thread_id = "thread-humans-1"

        # Fix: Use AgentMessage objects instead of raw dicts
        state = AgentState(
            messages=[AgentMessage(role="user", content="pause")], 
            status="awaiting_human"
        )
        await runtime.checkpoint(thread_id, state)

        # Resume with human approval
        result = await runtime.resume(thread_id, human_input={"approved": True, "notes": "proceed"})
        assert result.status == "done"
        assert "resumed" in str(result.output).lower()