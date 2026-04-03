"""Mock service returning sample Medi-Cal eligibility data."""

from datetime import datetime
from app.models.schemas import (
    EligibilityScreening,
    ApplicationInfo,
    ApplicationStatus,
)


class MockMediCalService:
    """Returns mock eligibility determinations for development."""

    FPL_2024_BASE = 15060
    FPL_2024_PER_ADDITIONAL = 5380

    # MAGI income limits as percentage of FPL
    PROGRAM_FPL_LIMITS: dict[str, float] = {
        "MAGI_Adult": 1.38,       # 138% FPL
        "MAGI_Child": 2.66,       # 266% FPL
        "Pregnancy": 2.13,        # 213% FPL
        "ABD": 1.00,              # 100% FPL
        "QMB": 1.00,              # 100% FPL
        "SLMB": 1.20,             # 120% FPL
    }

    SAMPLE_APPLICATIONS: dict[str, ApplicationInfo] = {
        "MC-2025-00001": ApplicationInfo(
            app_id="MC-2025-00001", applicant_name="Maria Garcia",
            household_size=3, monthly_income=2200.0, county="Los Angeles",
            status="pending_verification", program_type="MAGI_Adult",
            created_at=datetime(2025, 3, 15, 10, 0),
        ),
        "MC-2025-00002": ApplicationInfo(
            app_id="MC-2025-00002", applicant_name="James Chen",
            household_size=1, monthly_income=1500.0, county="San Francisco",
            status="approved", program_type="MAGI_Adult",
            created_at=datetime(2025, 2, 20, 14, 30),
        ),
        "MC-2025-00003": ApplicationInfo(
            app_id="MC-2025-00003", applicant_name="Sarah Williams",
            household_size=4, monthly_income=4500.0, county="Sacramento",
            status="denied", program_type="MAGI_Adult",
            created_at=datetime(2025, 1, 10, 9, 0),
        ),
        "MC-2025-00004": ApplicationInfo(
            app_id="MC-2025-00004", applicant_name="Robert Johnson",
            household_size=2, monthly_income=1800.0, county="San Diego",
            status="pending_documents", program_type="Pregnancy",
            created_at=datetime(2025, 3, 28, 11, 15),
        ),
        "MC-2025-00005": ApplicationInfo(
            app_id="MC-2025-00005", applicant_name="Lisa Nguyen",
            household_size=5, monthly_income=3200.0, county="Fresno",
            status="submitted", program_type="MAGI_Child",
            created_at=datetime(2025, 4, 1, 8, 45),
        ),
    }

    COUNTY_OFFICES: dict[str, dict] = {
        "Los Angeles": {
            "name": "LA County DPSS",
            "address": "12860 Crossroads Pkwy S, City of Industry, CA 91746",
            "phone": "(866) 613-3777",
            "hours": "Mon-Fri 8:00 AM - 5:00 PM",
        },
        "San Diego": {
            "name": "San Diego County HHSA",
            "address": "1255 Imperial Ave, Suite 100, San Diego, CA 92101",
            "phone": "(866) 262-9881",
            "hours": "Mon-Fri 7:30 AM - 5:00 PM",
        },
        "San Francisco": {
            "name": "SF Human Services Agency",
            "address": "1235 Mission St, San Francisco, CA 94103",
            "phone": "(415) 557-5000",
            "hours": "Mon-Fri 8:00 AM - 5:00 PM",
        },
        "Sacramento": {
            "name": "Sacramento County DHA",
            "address": "2700 Fulton Ave, Sacramento, CA 95821",
            "phone": "(916) 874-3100",
            "hours": "Mon-Fri 8:00 AM - 5:00 PM",
        },
        "Fresno": {
            "name": "Fresno County DSS",
            "address": "1900 Mariposa Mall, Suite 100, Fresno, CA 93721",
            "phone": "(559) 600-1377",
            "hours": "Mon-Fri 8:00 AM - 5:00 PM",
        },
    }

    def calculate_fpl(self, household_size: int) -> float:
        """Calculate Federal Poverty Level for household size (2024)."""
        if household_size <= 0:
            household_size = 1
        return self.FPL_2024_BASE + self.FPL_2024_PER_ADDITIONAL * max(0, household_size - 1)

    def screen_eligibility(
        self,
        monthly_income: float,
        household_size: int = 1,
        program_type: str | None = None,
    ) -> EligibilityScreening:
        """Screen for Medi-Cal eligibility based on income and household size."""
        if program_type is None:
            program_type = "MAGI_Adult"

        fpl = self.calculate_fpl(household_size)
        annual_income = monthly_income * 12
        fpl_percentage = (annual_income / fpl) * 100
        fpl_limit = self.PROGRAM_FPL_LIMITS.get(program_type, 1.38)
        income_limit = fpl * fpl_limit
        likely_eligible = annual_income <= income_limit

        factors = [f"Household size: {household_size}", f"Monthly income: ${monthly_income:,.2f}"]
        if likely_eligible:
            factors.append(f"Income is below {fpl_limit * 100:.0f}% FPL threshold")
        else:
            factors.append(f"Income exceeds {fpl_limit * 100:.0f}% FPL threshold")

        required_documents = ["Proof of identity (CA ID or driver's license)", "Proof of income (pay stubs, W-2, or tax return)"]
        if program_type == "Pregnancy":
            required_documents.append("Proof of pregnancy (doctor's statement)")
        if program_type in ("ABD", "QMB", "SLMB"):
            required_documents.append("Proof of disability or Medicare enrollment")
        required_documents.append("Proof of California residency")

        next_steps = []
        if likely_eligible:
            next_steps = [
                "Complete application at BenefitsCal.com or your county office",
                "Gather required verification documents",
                "Submit application — you should receive a determination within 45 days",
            ]
        else:
            next_steps = [
                "You may qualify for Covered California subsidized health insurance",
                "Check if other household members qualify for Medi-Cal",
                "Visit CoveredCA.com for marketplace options",
            ]

        return EligibilityScreening(
            program_type=program_type,
            likely_eligible=likely_eligible,
            confidence=0.92,
            income_limit=income_limit,
            fpl_percentage=round(fpl_percentage, 1),
            factors=factors,
            required_documents=required_documents,
            next_steps=next_steps,
        )

    def get_application_status(self, app_id: str | None) -> ApplicationStatus | None:
        """Look up application status by ID."""
        if app_id and app_id in self.SAMPLE_APPLICATIONS:
            app = self.SAMPLE_APPLICATIONS[app_id]
            next_action_map = {
                "draft": "Complete and submit your application",
                "submitted": "Your application is being reviewed — no action needed",
                "pending_verification": "Submit outstanding verification documents",
                "pending_documents": "Upload required documents to continue processing",
                "approved": "Your Medi-Cal coverage is active — check your BIC card",
                "denied": "You may appeal within 90 days or reapply with updated information",
            }
            return ApplicationStatus(
                app_id=app.app_id,
                status=app.status,
                last_updated=app.created_at,
                next_action=next_action_map.get(app.status),
            )
        return None

    def get_program_info(self, program_type: str) -> str:
        """Return informational text about a Medi-Cal program type."""
        info_map = {
            "MAGI_Adult": "MAGI Medi-Cal covers adults aged 19-64 with income up to 138% of the Federal Poverty Level. No asset test is required under MAGI rules.",
            "MAGI_Child": "Medi-Cal for children covers individuals under 19 with family income up to 266% FPL. Children may also qualify for the Healthy Families/CHIP program.",
            "Pregnancy": "Medi-Cal for pregnant individuals covers those with income up to 213% FPL. Coverage includes prenatal care, delivery, and 12 months postpartum.",
            "ABD": "Aged, Blind, and Disabled Medi-Cal covers individuals who are 65+, blind, or have a disability. Income limit is 100% FPL with an asset test.",
            "QMB": "Qualified Medicare Beneficiary program helps pay Medicare premiums, deductibles, and copayments for those with income up to 100% FPL.",
            "SLMB": "Specified Low-Income Medicare Beneficiary program pays Medicare Part B premiums for those with income between 100-120% FPL.",
        }
        return info_map.get(program_type, "Medi-Cal offers several programs based on age, income, disability status, and other factors. Please provide more details so I can help determine which program may be right for you.")

    def get_required_documents(self) -> list[str]:
        """Return list of commonly required documents."""
        return [
            "Photo ID (California driver's license or ID card)",
            "Social Security card or number",
            "Proof of income (pay stubs, W-2, tax return)",
            "Proof of California residency (utility bill, lease)",
            "Proof of citizenship or immigration status",
            "Bank statements (for ABD/non-MAGI programs)",
        ]

    def get_county_office(self, county: str | None) -> dict | None:
        """Look up county office information."""
        if county:
            return self.COUNTY_OFFICES.get(county)
        return None

    def create_application(self, app_data: dict) -> ApplicationInfo:
        """Create a new mock application."""
        import uuid
        app_id = f"MC-2025-{str(uuid.uuid4())[:5].upper()}"
        app = ApplicationInfo(
            app_id=app_id,
            applicant_name=app_data.get("applicant_name", "Unknown"),
            household_size=app_data.get("household_size", 1),
            monthly_income=app_data.get("monthly_income", 0.0),
            county=app_data.get("county", "Unknown"),
            status="draft",
            program_type=app_data.get("program_type", "MAGI_Adult"),
        )
        self.SAMPLE_APPLICATIONS[app_id] = app
        return app

    def get_all_applications(self) -> list[ApplicationInfo]:
        """Return all sample applications."""
        return list(self.SAMPLE_APPLICATIONS.values())
