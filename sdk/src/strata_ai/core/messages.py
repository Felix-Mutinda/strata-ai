from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field

class ToolCall(BaseModel):
    id: str
    name: str
    arguments: Dict[str, Any]

class ToolResult(BaseModel):
    tool_call_id: str
    output: Any
    status: str = Field(default="success")
    error: Optional[str] = None

class AgentMessage(BaseModel):
    """Normalized message schema. Adapters translate to provider-specific formats."""
    role: Literal["system", "user", "assistant", "tool"]
    content: Optional[Union[str, List[Dict[str, Any]]]] = None
    tool_calls: List[ToolCall] = Field(default_factory=list)
    tool_result: Optional[ToolResult] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentEvent(BaseModel):
    """Normalized streaming/telemetry event for OTel, UI, and audit sinks."""
    event_type: Literal["start", "step", "tool_call", "tool_result", "llm_output", "checkpoint", "end", "error"]
    thread_id: str
    node_name: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: Optional[str] = None  # ISO8601