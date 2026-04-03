"""Medi-Cal Eligibility Agent — FastAPI application."""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.pipeline import MediCalPipeline
from app.models.schemas import ChatRequest, ChatResponse, ApplicationInfo
from app.services.mock_service import MockMediCalService

app = FastAPI(
    title="Medi-Cal Eligibility Agent API",
    description="AI-powered eligibility determination for DHCS Medi-Cal programs",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = MediCalPipeline()
mock_service = MockMediCalService()


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "medi-cal-eligibility",
        "mock_mode": os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message through the 3-agent pipeline."""
    return await pipeline.process(request)


@app.get("/api/status")
async def status():
    """Return service status and configuration."""
    return {
        "service": "medi-cal-eligibility",
        "version": "0.1.0",
        "mock_mode": os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
        "agents": ["query_agent", "router_agent", "action_agent"],
        "supported_programs": ["MAGI_Adult", "MAGI_Child", "Pregnancy", "ABD", "QMB", "SLMB"],
    }


class EligibilityScreenRequest(BaseModel):
    monthly_income: float
    household_size: int = 1
    program_type: str | None = None


@app.post("/api/eligibility/screen")
async def screen_eligibility(request: EligibilityScreenRequest):
    """Quick eligibility screening by income and household size."""
    screening = mock_service.screen_eligibility(
        monthly_income=request.monthly_income,
        household_size=request.household_size,
        program_type=request.program_type,
    )
    return screening


class CreateApplicationRequest(BaseModel):
    applicant_name: str
    household_size: int = 1
    monthly_income: float = 0.0
    county: str = "Unknown"
    program_type: str = "MAGI_Adult"


@app.post("/api/applications")
async def create_application(request: CreateApplicationRequest):
    """Create a new Medi-Cal application."""
    app_data = request.model_dump()
    application = mock_service.create_application(app_data)
    return application


@app.get("/api/applications/{app_id}")
async def get_application(app_id: str):
    """Get application details by ID."""
    status = mock_service.get_application_status(app_id)
    if status is None:
        raise HTTPException(status_code=404, detail=f"Application {app_id} not found")
    return status
