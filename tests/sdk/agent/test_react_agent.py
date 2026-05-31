import pytest
from strata_ai.core.models import AgentConfig, AgentDefinition
from strata_ai.core.tool import tool
from strata_ai.runtime.mock import MockRuntime
from strata_ai.agent.patterns import ReActAgent


class TestReActAgent:
    @pytest.mark.asyncio
    async def test_build_definition_returns_valid_structure(self):
        config = AgentConfig(name="test-react", model="mock:llm", instructions="test")
        runtime = MockRuntime()
        agent = ReActAgent(config=config, runtime=runtime, tools=[])
        definition = agent._build_definition()

        assert isinstance(definition, AgentDefinition)
        assert definition.entry_point == "reason"
        assert len(definition.nodes) >= 2  # reason + act

    @pytest.mark.asyncio
    async def test_executes_deterministic_loop_with_mock_runtime(self):
        @tool
        def get_weather(city: str) -> str:
            return "Sunny"

        config = AgentConfig(
            name="weather-react", model="mock:llm", instructions="Check weather"
        )
        runtime = MockRuntime()
        agent = ReActAgent(config=config, runtime=runtime, tools=[get_weather])

        result = await agent.run({"query": "Weather in Nairobi"})
        assert result.status == "done"
        assert result.thread_id is not None
