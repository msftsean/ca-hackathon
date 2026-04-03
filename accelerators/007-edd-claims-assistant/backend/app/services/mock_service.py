"""Mock service returning sample EDD claims data."""

from datetime import date, timedelta
from app.models.schemas import ClaimQuery, ClaimStatus


class MockEDDService:
    """Returns mock EDD claim status for development."""

    def get_claim_status(self, query: ClaimQuery, program: str) -> ClaimStatus:
        today = date.today()
        mock_claims = {
            "ui": ClaimStatus(
                claim_id="UI-2025-1234567",
                program="ui",
                status="approved",
                claimant_name="Mock Claimant",
                filed_date=today - timedelta(days=21),
                weekly_benefit_amount=450.00,
                last_payment_date=today - timedelta(days=3),
                next_certification_date=today + timedelta(days=11),
                notes=["Certify every two weeks to continue receiving benefits"],
            ),
            "di": ClaimStatus(
                claim_id="DI-2025-7654321",
                program="di",
                status="in_review",
                claimant_name="Mock Claimant",
                filed_date=today - timedelta(days=10),
                weekly_benefit_amount=None,
                notes=["Awaiting physician certification", "Processing time: 14 days"],
            ),
            "pfl": ClaimStatus(
                claim_id="PFL-2025-9876543",
                program="pfl",
                status="pending",
                claimant_name="Mock Claimant",
                filed_date=today - timedelta(days=5),
                weekly_benefit_amount=None,
                notes=["Bonding claim — awaiting documentation"],
            ),
        }
        return mock_claims.get(program, mock_claims["ui"])
