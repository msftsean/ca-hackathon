"""Mock service returning sample Medi-Cal eligibility data."""

from app.models.schemas import EligibilityQuery, EligibilityDetermination


class MockMediCalService:
    """Returns mock eligibility determinations for development."""

    FPL_2024 = {1: 15060, 2: 20440, 3: 25820, 4: 31200, 5: 36580}

    def determine_eligibility(self, query: EligibilityQuery) -> EligibilityDetermination:
        household_size = query.applicant_info.get("household_size", 1)
        monthly_income = query.applicant_info.get("monthly_income", 1500.0)
        annual_income = monthly_income * 12
        fpl = self.FPL_2024.get(household_size, 15060)
        fpl_pct = (annual_income / fpl) * 100
        income_limit = fpl * 1.38
        eligible = annual_income <= income_limit

        return EligibilityDetermination(
            application_id="MC-2025-MOCK-001",
            eligible=eligible,
            program="medi-cal" if eligible else "covered-california",
            magi_income=annual_income,
            fpl_percentage=round(fpl_pct, 1),
            income_limit=income_limit,
            household_size=household_size,
            determination_reason=f"{'Below' if eligible else 'Above'} 138% FPL threshold ({fpl_pct:.0f}% FPL)",
            next_steps=["Submit verification documents", "Complete interview"] if eligible else ["Apply through Covered California"],
            confidence=0.94,
        )
