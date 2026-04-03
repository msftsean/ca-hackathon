"""BenefitsCal Navigator — FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models.schemas import ChatRequest, ChatResponse, ProgramInfo
from app.pipeline import BenefitsCalPipeline
from app.services.mock_service import MockBenefitsService

settings = get_settings()

app = FastAPI(
    title="BenefitsCal Navigator API",
    description="AI-powered benefits eligibility assistant for CDSS programs",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = BenefitsCalPipeline()
mock_service = MockBenefitsService()


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "benefitscal-navigator",
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
        "supported_languages": settings.supported_languages.split(","),
    }


@app.get("/api/programs", response_model=list[ProgramInfo])
async def list_programs() -> list[ProgramInfo]:
    programs = mock_service.list_programs()
    return [
        ProgramInfo(
            program_id=p["program_id"],
            name=p["name"],
            description=p["description"],
            agency=p["agency"],
            requirements=p["requirements"],
            documents_needed=p["documents_needed"],
        )
        for p in programs
    ]
