"""Shared test fixtures for 008 Multilingual Emergency Chatbot."""

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
    return {"message": "Are there any wildfire alerts?", "language": "en"}


@pytest.fixture
def sample_shelter_request():
    return {"message": "Where is the nearest shelter?", "language": "en"}


@pytest.fixture
def sample_aqi_request():
    return {"message": "What is the air quality?", "language": "en"}
