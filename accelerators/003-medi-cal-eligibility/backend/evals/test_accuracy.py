"""Accuracy evaluation tests for Medi-Cal Eligibility Agent."""

import json
import os
import pytest
from pathlib import Path
from app.agents.query_agent import QueryAgent
from app.agents.action_agent import ActionAgent
from app.agents.router_agent import RouterAgent
from app.models.schemas import RoutingDecision


EVAL_CONFIG = Path(__file__).parent / "eval_config.json"


@pytest.fixture
def eval_cases():
    with open(EVAL_CONFIG) as f:
        data = json.load(f)
    return data["test_cases"]


@pytest.fixture
def query_agent():
    return QueryAgent()


@pytest.fixture
def action_agent():
    os.environ["USE_MOCK_SERVICES"] = "true"
    return ActionAgent()


@pytest.fixture
def router_agent():
    return RouterAgent()


class TestIntentAccuracy:
    @pytest.mark.asyncio
    async def test_intent_detection_accuracy(self, eval_cases, query_agent):
        """Verify intent detection matches expected intents across eval cases."""
        correct = 0
        total = len(eval_cases)
        for case in eval_cases:
            result = await query_agent.process(case["input"])
            if result.intent == case["expected_intent"]:
                correct += 1
        accuracy = correct / total
        assert accuracy >= 0.7, f"Intent accuracy {accuracy:.0%} below 70% threshold"


class TestEligibilityAccuracy:
    @pytest.mark.asyncio
    async def test_eligibility_determination(self, eval_cases, query_agent, router_agent, action_agent):
        """Verify eligibility determinations are correct for income-based cases."""
        eligible_cases = [c for c in eval_cases if "expected_eligible" in c]
        correct = 0
        for case in eligible_cases:
            query = await query_agent.process(case["input"])
            routing = await router_agent.route(query)
            result = await action_agent.execute(query, routing)
            if result.eligibility and result.eligibility.likely_eligible == case["expected_eligible"]:
                correct += 1
        accuracy = correct / len(eligible_cases) if eligible_cases else 0
        assert accuracy >= 0.7, f"Eligibility accuracy {accuracy:.0%} below 70% threshold"


class TestResponseQuality:
    @pytest.mark.asyncio
    async def test_responses_are_nonempty(self, eval_cases, query_agent, router_agent, action_agent):
        """All eval cases should produce non-empty responses."""
        for case in eval_cases:
            query = await query_agent.process(case["input"])
            routing = await router_agent.route(query)
            result = await action_agent.execute(query, routing)
            assert result.response, f"Empty response for case {case['id']}"

    @pytest.mark.asyncio
    async def test_confidence_reasonable(self, eval_cases, query_agent, router_agent, action_agent):
        """All responses should have confidence > 0."""
        for case in eval_cases:
            query = await query_agent.process(case["input"])
            routing = await router_agent.route(query)
            result = await action_agent.execute(query, routing)
            assert result.confidence > 0, f"Zero confidence for case {case['id']}"
