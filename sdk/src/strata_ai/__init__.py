"""Strata AI SDK — Layered contracts for AI systems."""

__version__ = "0.1.0"

from strata_ai.core.config import StrataBaseConfig
from strata_ai.core.app import StrataAIApp
from strata_ai.core.di import AppState
from strata_ai.core.models import AgentConfig, AgentState, AgentResult, AgentDefinition
from strata_ai.core.agent import BaseAgent
from strata_ai.core.tool import tool, Tool
from strata_ai.core.messages import AgentMessage, ToolCall, ToolResult, AgentEvent
from strata_ai.agent.patterns import ReActAgent
from strata_ai.runtime.base import AgentRuntime
from strata_ai.runtime.mock import MockRuntime
from strata_ai.runtime.langgraph_adapter import LangGraphAdapter

__all__ = [
    "StrataBaseConfig",
    "StrataAIApp",
    "AppState",
    "AgentConfig",
    "AgentState",
    "AgentResult",
    "AgentDefinition",
    "BaseAgent",
    "tool",
    "Tool",
    "AgentMessage",
    "ToolCall",
    "ToolResult",
    "AgentEvent",
    "ReActAgent",
    "AgentRuntime",
    "MockRuntime",
    "LangGraphAdapter",
]
