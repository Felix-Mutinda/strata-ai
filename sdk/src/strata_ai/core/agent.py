from __future__ import annotations
import uuid
from typing import Any, Dict, List, Optional

from strata_ai.core.models import AgentConfig, AgentResult, AgentDefinition
from strata_ai.runtime.base import AgentRuntime


class BaseAgent:
    """
    Base contract for all agent patterns.
    Patterns inherit from this and implement _build_definition().
    The runtime is injected; swapping it requires zero pattern refactors.
    """

    def __init__(
        self,
        config: AgentConfig,
        runtime: AgentRuntime,
        tools: List[Any] = None,
        memory: Any = None,
        guardrails: List[Any] = None,
    ):
        self.config = config
        self.runtime = runtime
        self.tools = tools or []
        self.memory = memory
        self.guardrails = guardrails or []
        self._compiled: Optional[Any] = None

    async def compile(self) -> None:
        """Idempotent compilation. Cares the runtime adapter once."""
        if self._compiled is None:
            definition = self._build_definition()
            self._compiled = await self.runtime.compile(definition)

    async def run(self, input: Dict[str, Any], **kwargs) -> AgentResult:
        await self.compile()
        thread_id = kwargs.get("thread_id", str(uuid.uuid4()))
        return await self.runtime.run(
            self._compiled, input, config={"thread_id": thread_id, **kwargs}
        )

    async def stream(self, input: Dict[str, Any], **kwargs):
        await self.compile()
        async for event in self.runtime.stream(
            self._compiled, input, config={**kwargs}
        ):
            yield event

    def _build_definition(self) -> AgentDefinition:
        raise NotImplementedError(
            "Pattern subclasses must implement _build_definition()"
        )
