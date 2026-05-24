from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    service_name: str
    env: str


@router.get("/health", response_model=HealthResponse)
async def health(request: Request):
    ctx = request.app.state.ctx
    return HealthResponse(
        status="ok", service_name=ctx.config.service_name, env=ctx.config.env
    )
