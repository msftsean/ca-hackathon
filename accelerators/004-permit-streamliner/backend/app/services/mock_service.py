"""Mock service returning sample permit data."""

from datetime import date, timedelta
from app.models.schemas import PermitQuery, PermitApplication, ChecklistItem


class MockPermitService:
    """Returns mock permit application data for development."""

    def get_permit_status(self, query: PermitQuery, jurisdiction: str) -> PermitApplication:
        today = date.today()
        return PermitApplication(
            permit_id="PRM-2025-00042",
            permit_type=query.permit_type or "residential",
            applicant_name="Mock Applicant",
            jurisdiction=jurisdiction,
            status="review",
            submitted_date=today - timedelta(days=12),
            sla_deadline=today + timedelta(days=18),
            sla_days_remaining=18,
            checklist=[
                ChecklistItem(item_id="CK-01", description="Site plan (to scale)", required=True, completed=True),
                ChecklistItem(item_id="CK-02", description="Floor plan with dimensions", required=True, completed=True),
                ChecklistItem(item_id="CK-03", description="Title 24 energy compliance", required=True, completed=False),
                ChecklistItem(item_id="CK-04", description="Structural calculations", required=True, completed=False),
                ChecklistItem(item_id="CK-05", description="CEQA exemption or clearance", required=False, completed=False, document_type="ceqa"),
            ],
            notes=["Awaiting Title 24 energy compliance report"],
        )
