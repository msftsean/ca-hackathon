"""Shared test fixtures for BenefitsCal Navigator."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_messages():
    return {
        "eligibility": "Am I eligible for CalFresh?",
        "program_info": "What is CalWORKs? Tell me about it",
        "application": "How do I apply for CalFresh?",
        "documents": "What documents do I need for CalWORKs?",
        "office": "Where is the nearest office in Los Angeles?",
        "status": "Check my application status",
        "general": "I need help with benefits",
        "pii": "My SSN is 123-45-6789",
    }
