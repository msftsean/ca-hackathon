"""Tests for QueryAgent — intent detection and entity extraction."""

import pytest
from app.agents.query_agent import QueryAgent


@pytest.fixture
def agent():
    return QueryAgent()


class TestIntentDetection:
    @pytest.mark.asyncio
    async def test_eligibility_check(self, agent):
        result = await agent.process("Am I eligible for Medi-Cal?")
        assert result.intent == "eligibility_check"

    @pytest.mark.asyncio
    async def test_application_status(self, agent):
        result = await agent.process("Where is my application?")
        assert result.intent == "application_status"

    @pytest.mark.asyncio
    async def test_income_verification(self, agent):
        result = await agent.process("I earn $3,000 per month as salary")
        assert result.intent == "income_verification"

    @pytest.mark.asyncio
    async def test_document_help(self, agent):
        result = await agent.process("What documents do I need to upload?")
        assert result.intent == "document_help"

    @pytest.mark.asyncio
    async def test_program_info(self, agent):
        result = await agent.process("What is the difference between MAGI and ABD?")
        assert result.intent == "program_info"

    @pytest.mark.asyncio
    async def test_county_info(self, agent):
        result = await agent.process("Where is the county office near me?")
        assert result.intent == "county_info"

    @pytest.mark.asyncio
    async def test_general_info(self, agent):
        result = await agent.process("Tell me about healthcare")
        assert result.intent == "general_info"


class TestEntityExtraction:
    @pytest.mark.asyncio
    async def test_extract_income(self, agent):
        result = await agent.process("I make $2,500 per month, am I eligible?")
        assert "income_amounts" in result.entities
        assert 2500.0 in result.entities["income_amounts"]

    @pytest.mark.asyncio
    async def test_extract_household_size(self, agent):
        result = await agent.process("I have a family of 4, do we qualify?")
        assert result.entities.get("household_size") == 4

    @pytest.mark.asyncio
    async def test_extract_single_person(self, agent):
        result = await agent.process("I live alone, can I get medi-cal?")
        assert result.entities.get("household_size") == 1

    @pytest.mark.asyncio
    async def test_extract_county(self, agent):
        result = await agent.process("I live in Sacramento, where do I go?")
        assert result.entities.get("county") == "Sacramento"


class TestProgramDetection:
    @pytest.mark.asyncio
    async def test_detect_magi(self, agent):
        result = await agent.process("Am I eligible for MAGI Medi-Cal?")
        assert result.program_type == "MAGI_Adult"

    @pytest.mark.asyncio
    async def test_detect_pregnancy(self, agent):
        result = await agent.process("I'm pregnant, do I qualify?")
        assert result.program_type == "Pregnancy"

    @pytest.mark.asyncio
    async def test_detect_abd(self, agent):
        result = await agent.process("I have a disability, can I get coverage?")
        assert result.program_type == "ABD"

    @pytest.mark.asyncio
    async def test_detect_child(self, agent):
        result = await agent.process("Can my children get Medi-Cal?")
        assert result.program_type == "MAGI_Child"

    @pytest.mark.asyncio
    async def test_no_program(self, agent):
        result = await agent.process("How do I apply?")
        assert result.program_type is None
