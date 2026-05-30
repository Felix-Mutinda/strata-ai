from __future__ import annotations
from typing import Annotated, Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field

from .messages import AgentMessage


def _append_messages(
    left: List[AgentMessage], right: List[AgentMessage]
) -> List[AgentMessage]:
    """Framework-agnostic message accumulator."""
    return left + right


class AgentConfig(BaseModel):
    name: str
    model: str
    instructions: str
    max_iterations: int = Field(default=10, ge=1, le=50)
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    tags: List[str] = Field(default_factory=list)


class AgentState(BaseModel):
    messages: Annotated[List[AgentMessage], _append_messages] = Field(
        default_factory=list
    )
    context: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="running")
    thread_id: Optional[str] = Field(default=None)


class AgentResult(BaseModel):
    thread_id: str
    status: str
    output: Any = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class AgentDefinition(BaseModel):
    config: AgentConfig
    state_schema: Type[BaseModel] = AgentState
    nodes: List[Any] = Field(default_factory=list)
    edges: List[Any] = Field(default_factory=list)
    conditional_edges: List[Any] = Field(default_factory=list)
    entry_point: Optional[str] = None
