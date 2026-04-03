"""Cross-Agency Knowledge Hub — FastAPI application."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Cross-Agency Knowledge Hub API",
    description="Federated search across California state government knowledge bases",
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
        "service": "cross-agency-knowledge-hub",
        "mock_mode": os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
    }
