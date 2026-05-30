import asyncio
from typing import Optional, Dict, Any
from pydantic import BaseModel


class TaskPayload(BaseModel):
    thread_id: str
    task_type: str
    payload: Dict[str, Any]
    status: str = "pending"


class TaskQueueAdapter:
    async def submit(self, payload: TaskPayload) -> str: ...
    async def poll(
        self, task_id: str, timeout_ms: int = 5000
    ) -> Optional[TaskPayload]: ...
    async def update_status(
        self, task_id: str, status: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None: ...
    async def claim_pending(self, agent_name: str) -> Optional[TaskPayload]: ...


class InMemoryTaskQueue(TaskQueueAdapter):
    def __init__(self) -> None:
        self._store: Dict[str, TaskPayload] = {}
        self._lock = asyncio.Lock()

    async def submit(self, payload: TaskPayload) -> str:
        async with self._lock:
            self._store[payload.thread_id] = payload
        return payload.thread_id

    async def poll(self, task_id: str, timeout_ms: int = 5000) -> Optional[TaskPayload]:
        async with self._lock:
            return self._store.get(task_id)

    async def update_status(
        self, task_id: str, status: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        async with self._lock:
            p = self._store.get(task_id)
            if p:
                p.status = status
                if metadata:
                    p.payload.update(metadata)

    async def claim_pending(self, agent_name: str) -> Optional[TaskPayload]:
        async with self._lock:
            for t in self._store.values():
                if t.status == "pending":
                    t.status = "claimed"
                    return t
            return None
