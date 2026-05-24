from typing import Any
from pydantic import BaseModel


class AppState(BaseModel):
    """Typed FastAPI DI container. Published to app.state.ctx"""

    config: Any = None
    db: Any = None
    cache: Any = None
    task_queue: Any = None
    ai: Any = None
    otel: Any = None
    model_config = {"arbitrary_types_allowed": True}
