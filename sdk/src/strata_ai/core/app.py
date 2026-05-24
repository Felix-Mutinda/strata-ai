from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from strata_ai.core.config import StrataBaseConfig
from strata_ai.core.di import AppState
from strata_ai.core.lifespan import lifespan
from strata_ai.core.exceptions import (
    validation_exception_handler,
    generic_exception_handler,
)
from strata_ai.core.routers import router as health_router


class StrataAIApp:
    """Factory that produces a fully-wired FastAPI instance with Strata AI contracts."""

    @staticmethod
    def build(config: StrataBaseConfig) -> FastAPI:
        state = AppState(config=config)
        app = FastAPI(
            title=config.service_name,
            lifespan=lifespan,
            openapi_url="/docs" if config.env != "prod" else None,
        )
        app.state.ctx = state

        # Register RFC 9457 error handlers
        # FastAPI uses RequestValidationError for route payload validation
        app.add_exception_handler(RequestValidationError, validation_exception_handler)
        app.add_exception_handler(Exception, generic_exception_handler)

        # Include base platform routers
        app.include_router(health_router)

        return app
