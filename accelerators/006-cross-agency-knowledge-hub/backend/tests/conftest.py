"""Shared fixtures for Cross-Agency Knowledge Hub tests."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_message():
    return "Find CDSS policy on CalFresh eligibility"


@pytest.fixture
def expert_message():
    return "Who is the expert on procurement?"


@pytest.fixture
def cross_ref_message():
    return "What documents are related to data governance?"
