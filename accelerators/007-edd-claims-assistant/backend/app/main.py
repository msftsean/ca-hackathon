"""EDD Claims Assistant — FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import get_settings
from app.models.schemas import ChatRequest, ChatResponse
from app.pipeline import EDDClaimsPipeline
from app.services.mock_service import MockEDDService

settings = get_settings()

app = FastAPI(
    title="EDD Claims Assistant API",
    description="AI-powered claims status and eligibility assistant for EDD",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = EDDClaimsPipeline()
mock_service = MockEDDService()


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "edd-claims-assistant",
        "mock_mode": settings.use_mock_services,
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return await pipeline.process(request)


@app.get("/api/status")
async def status():
    return {
        "service": settings.app_name,
        "version": "0.1.0",
        "mock_mode": settings.use_mock_services,
        "supported_claim_types": settings.supported_claim_types.split(","),
    }


class ClaimStatusRequest(BaseModel):
    claim_type: str = "UI"
    last_four_ssn: str = ""
    date_of_birth: str = ""


@app.post("/api/claim-status")
async def claim_status(request: ClaimStatusRequest):
    if settings.identity_verification_required and request.last_four_ssn:
        mock_service.verify_identity(request.last_four_ssn, request.date_of_birth)
    claim = mock_service.get_claim(request.claim_type)
    if claim is None:
        return {"error": "Claim not found"}
    return claim.model_dump()


class EligibilityRequest(BaseModel):
    claim_type: str = "UI"


@app.post("/api/eligibility")
async def eligibility(request: EligibilityRequest):
    assessment = mock_service.get_eligibility(request.claim_type)
    return assessment.model_dump()


class DocumentChecklistRequest(BaseModel):
    claim_type: str = "UI"


@app.post("/api/document-checklist")
async def document_checklist(request: DocumentChecklistRequest):
    checklist = mock_service.get_document_checklist(request.claim_type)
    return [item.model_dump() for item in checklist]
