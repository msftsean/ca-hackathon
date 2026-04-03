"""Mock service returning sample benefits data."""

from app.models.schemas import BenefitQuery, EligibilityResult


class MockBenefitsService:
    """Returns mock eligibility information for CDSS programs."""

    MOCK_RESPONSES = {
        "calfresh": EligibilityResult(
            program="CalFresh",
            eligible=None,
            summary="CalFresh provides monthly food benefits to low-income individuals and families. A household of 1 may qualify with gross monthly income at or below $2,510.",
            citations=["CDSS MPP 63-503", "7 CFR 273.9"],
            next_steps=["Apply online at BenefitsCal.com", "Visit your county office", "Call 1-877-847-3663"],
            confidence=0.92,
        ),
        "calworks": EligibilityResult(
            program="CalWORKs",
            eligible=None,
            summary="CalWORKs provides temporary cash aid and services to families with children. Eligibility depends on income, assets, and family composition.",
            citations=["CDSS MPP 44-211", "WIC §11250"],
            next_steps=["Apply at BenefitsCal.com", "Gather proof of income and identity"],
            confidence=0.89,
        ),
        "general": EligibilityResult(
            program="General",
            eligible=None,
            summary="California offers several public assistance programs including CalFresh, CalWORKs, Medi-Cal, and General Assistance. Visit BenefitsCal.com to explore options.",
            citations=["BenefitsCal.com"],
            next_steps=["Visit BenefitsCal.com for a full list of programs"],
            confidence=0.85,
        ),
    }

    def get_eligibility_info(self, query: BenefitQuery, program: str) -> EligibilityResult:
        result = self.MOCK_RESPONSES.get(program, self.MOCK_RESPONSES["general"])
        result.language = query.language
        return result
