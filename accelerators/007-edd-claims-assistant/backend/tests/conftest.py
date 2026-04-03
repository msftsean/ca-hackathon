"""Shared fixtures for EDD Claims Assistant tests."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_status_message():
    return "Check my unemployment claim status"


@pytest.fixture
def sample_eligibility_message():
    return "Am I eligible for disability insurance?"


@pytest.fixture
def sample_filing_message():
    return "How do I file for paid family leave?"
