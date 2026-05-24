# tests/sdk/core/test_core_contract.py
import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError as PydanticValidationError
from fastapi import FastAPI, Body
from pydantic import BaseModel

from strata_ai.core.config import StrataBaseConfig
from strata_ai.core.app import StrataAIApp
from strata_ai.core.di import AppState


class TestStrataBaseConfig:
    def test_loads_from_env(self, monkeypatch):
        monkeypatch.setenv("STRATA_AI_SERVICE_NAME", "test-api")
        monkeypatch.setenv("STRATA_AI_ENV", "dev")
        config = StrataBaseConfig.from_env()
        assert config.service_name == "test-api"
        assert config.env == "dev"

    def test_raises_on_missing_required(self, monkeypatch):
        monkeypatch.delenv("STRATA_AI_SERVICE_NAME", raising=False)
        with pytest.raises(PydanticValidationError):
            StrataBaseConfig.from_env()

    def test_defaults_optional_fields(self, monkeypatch):
        monkeypatch.setenv("STRATA_AI_SERVICE_NAME", "test-defaults")
        config = StrataBaseConfig.from_env()
        assert config.temperature == 0.0
        assert config.max_iterations == 10


class TestStrataAIApp:
    @pytest.mark.asyncio
    async def test_build_returns_fastapi_with_typed_ctx(self):
        config = StrataBaseConfig(service_name="unit-test", env="test")
        app = StrataAIApp.build(config=config)
        assert isinstance(app, FastAPI)
        assert hasattr(app.state, "ctx")
        assert isinstance(app.state.ctx, AppState)
        assert app.state.ctx.config.service_name == "unit-test"

    @pytest.mark.asyncio
    async def test_health_endpoint_returns_contract_payload(self):
        config = StrataBaseConfig(service_name="health-test", env="test")
        app = StrataAIApp.build(config=config)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            resp = await ac.get("/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "ok"
            assert data["service_name"] == "health-test"

    @pytest.mark.asyncio
    async def test_validation_errors_return_rfc9457_format(self):
        config = StrataBaseConfig(service_name="error-test", env="test")
        app = StrataAIApp.build(config=config)

        class TestPayload(BaseModel):
            value: int

        @app.post("/test-validate")
        async def test_endpoint(payload: TestPayload = Body(...)):
            return {"received": payload.value}

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            # Send invalid type to trigger Pydantic ValidationError
            resp = await ac.post("/test-validate", json={"value": "not_an_int"})
            assert resp.status_code == 422
            data = resp.json()
            # RFC 9457 ProblemDetail contract
            assert "type" in data
            assert data["status"] == 422
            assert "instance" in data
            assert isinstance(data.get("errors"), list)
