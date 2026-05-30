# tests/sdk/core/test_task_queue.py
import pytest
from strata_ai.core.task_queue import TaskPayload, InMemoryTaskQueue


class TestTaskQueue:
    @pytest.mark.asyncio
    async def test_submit_and_poll(self):
        q = InMemoryTaskQueue()
        payload = TaskPayload(
            thread_id="t1", task_type="human_approval", payload={"approve": False}
        )
        tid = await q.submit(payload)
        result = await q.poll(tid)

        # Type narrowing: satisfies Pyright's Optional check
        assert result is not None
        assert result.thread_id == "t1"
        assert result.status == "pending"

    @pytest.mark.asyncio
    async def test_update_status(self):
        q = InMemoryTaskQueue()
        await q.submit(TaskPayload(thread_id="t2", task_type="agent_run", payload={}))
        await q.update_status("t2", "completed", metadata={"score": 0.9})
        result = await q.poll("t2")

        assert result is not None
        assert result.status == "completed"
        assert result.payload["score"] == 0.9

    def test_instance_isolation(self):
        q1, q2 = InMemoryTaskQueue(), InMemoryTaskQueue()
        assert q1._store is not q2._store
