"""Shared test fixtures for 005 GenAI Procurement Compliance."""

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("USE_MOCK_SERVICES", "true")

from app.main import app  # noqa: E402


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_chat_request():
    return {"message": "Check the compliance of this vendor attestation"}


@pytest.fixture
def sample_gap_request():
    return {"message": "What are the compliance gaps?"}


@pytest.fixture
def sample_risk_request():
    return {"message": "What is the risk tier?"}
