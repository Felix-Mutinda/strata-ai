import pytest
from strata_ai.core.models import AgentConfig
from strata_ai.core.tool import tool
from strata_ai.agent.patterns import ReActAgent
from strata_ai.runtime.mock import MockRuntime
from strata_ai.runtime.langgraph_adapter import LangGraphAdapter

   
@tool
def mock_weather(city: str) -> str:
    return f"Sunny in {city}"

class TestRuntimeSwapParity:
    """Proves that swapping runtimes requires ZERO pattern refactors."""
 

    @pytest.mark.asyncio
    async def test_mock_runtime_parity(self):
        config = AgentConfig(name="parity-test", model="mock:llm", instructions="Check weather")
        agent = ReActAgent(config=config, runtime=MockRuntime(), tools=[mock_weather])
        result = await agent.run({"query": "Nairobi"})
        assert result.status == "done"
        assert result.thread_id is not None

    @pytest.mark.asyncio
    async def test_langgraph_runtime_parity(self):
        config = AgentConfig(name="parity-test", model="mock:llm", instructions="Check weather")
        # LangGraphAdapter uses in-memory checkpointer for tests
        agent = ReActAgent(config=config, runtime=LangGraphAdapter(), tools=[mock_weather])
        result = await agent.run({"query": "Nairobi"})
        assert result.status == "done"
        assert result.thread_id is not None