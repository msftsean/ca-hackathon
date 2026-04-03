"""BenefitsCal Navigator — FastAPI application."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="BenefitsCal Navigator API",
    description="AI-powered benefits eligibility assistant for CDSS programs",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "benefitscal-navigator",
        "mock_mode": os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
    }
