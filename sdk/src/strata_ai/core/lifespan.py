from __future__ import annotations
from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI
from loguru import logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Bootstrap orchestrator. Strict startup/shutdown order."""
    state = app.state.ctx
    config = state.config
    logger.info("Starting up", service=config.service_name, env=config.env)

    # Phase 0: Mock/Stub initialization. Phase 1 replaces with real DB/Cache/AI/OTel
    state.db = "mock_db_pool"
    state.cache = "mock_redis"
    state.otel = "mock_tracer"

    logger.info("Service startup complete — ready to serve")
    yield

    logger.info("Shutdown initiated — draining connections")
    # Phase 1: await state.db.disconnect(), await state.cache.close(), otel.flush()
    logger.info("Shutdown complete")
