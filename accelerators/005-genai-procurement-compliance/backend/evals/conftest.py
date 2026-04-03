"""Fixtures for evaluation tests."""

import os

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("USE_MOCK_SERVICES", "true")

from app.main import app  # noqa: E402


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
