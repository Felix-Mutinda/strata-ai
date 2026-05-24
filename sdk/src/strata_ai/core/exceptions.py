from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """RFC 9457 ProblemDetail format for validation errors."""
    # Runtime check to satisfy static type checker
    if not isinstance(exc, RequestValidationError):
        raise exc  # Re-raise if not the expected error type

    return JSONResponse(
        status_code=422,
        content={
            "type": "about:blank",
            "title": "Validation Error",
            "status": 422,
            "detail": "Invalid request payload",
            "instance": str(request.url),
            "errors": exc.errors(),  # List of validation error dicts
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """RFC 9457 ProblemDetail for unexpected failures."""
    return JSONResponse(
        status_code=500,
        content={
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred.",
            "instance": str(request.url),
        },
    )
