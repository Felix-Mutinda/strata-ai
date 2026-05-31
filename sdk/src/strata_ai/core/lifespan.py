from __future__ import annotations
from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI
from loguru import logger
import sys


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    config = app.state.ctx.config

    # ── 0. Enterprise Loguru Bootstrap ──────────────────────────────────────
    logger.remove()  # Strip default handler to prevent duplicate logs
    logger.add(
        sys.stderr,
        level=config.log_level,
        format=config.log_format,
        serialize=config.log_serialize,
        enqueue=True,  # Thread-safe, async-compatible
        backtrace=config.env != "prod",  # Full tracebacks only in dev/staging
        diagnose=config.env != "prod",  # Variable inspection only in dev/staging
    )
    if config.log_file:
        logger.add(
            config.log_file,
            rotation="500 MB",
            retention="10 days",
            level="DEBUG",
            compression="zip",
        )

    # Bind baseline context to every log line
    logger.configure(
        extra={"service": config.service_name, "env": config.env, "correlation_id": "-"}
    )
    logger.info(
        "Enterprise logger initialized",
        format="default" if not config.log_serialize else "json",
    )

    # ── 1. Observability — must be first; everything else emits spans ───────
    # Phase 1: OTelBootstrap placeholder
    app.state.ctx.otel = "mock_tracer"
    logger.info("OTel initialised", service=config.service_name, env=config.env)

    # ── 2. Database / Cache / Task Queue / AI SDK ───────────────────────────
    app.state.ctx.db = "mock_db_pool"
    app.state.ctx.cache = "mock_redis"
    app.state.ctx.task_queue = "mock_queue"
    logger.info("Infrastructure pools ready")

    # ── 3. Publish state & yield ────────────────────────────────────────────
    logger.info("Service startup complete — ready to serve")
    yield

    # ── 4. Graceful shutdown (reverse order) ────────────────────────────────
    logger.info("Shutdown initiated — draining connections")
    # Phase 1: await db.disconnect(), cache.close(), task_queue.stop(), otel.flush()
    logger.info("Shutdown complete")
