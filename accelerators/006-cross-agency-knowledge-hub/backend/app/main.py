"""Cross-Agency Knowledge Hub — FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models.schemas import ChatRequest, ChatResponse, DocumentResult
from app.pipeline import KnowledgeHubPipeline
from app.services.mock_service import MockKnowledgeService

settings = get_settings()

app = FastAPI(
    title="Cross-Agency Knowledge Hub API",
    description="Federated search across California state government knowledge bases",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = KnowledgeHubPipeline()
mock_service = MockKnowledgeService()


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "cross-agency-knowledge-hub",
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
        "max_results_per_agency": settings.max_results_per_agency,
        "cross_references_enabled": settings.enable_cross_references,
    }


@app.get("/api/search")
async def search(
    query: str = "",
    agency: str | None = None,
    doc_type: str | None = None,
):
    agencies = [agency] if agency else None
    doc_types = [doc_type] if doc_type else None
    request = ChatRequest(
        message=query or "search",
        agency_filter=agencies,
        document_types=doc_types,
    )
    result = await pipeline.process(request)
    return {
        "results": [d.model_dump() for d in result.documents] if result.documents else [],
        "total": len(result.documents) if result.documents else 0,
    }


@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: str):
    doc = mock_service.get_document_by_id(doc_id)
    if doc is None:
        return {"error": "Document not found"}, 404
    return doc.model_dump()
