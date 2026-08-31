import logging
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

# pyrefly: ignore [missing-import]
from src.api.schemas import HealthResponse, QueryRequest, QueryResponse, SourcesResponse

# pyrefly: ignore [missing-import]
from src.core.whitelist import TRUSTED_DOMAINS

# pyrefly: ignore [missing-import]
from src.crew import run_medical_crew

logger = logging.getLogger("api")

app = FastAPI(
    title="MedQuery Medical Crew API",
    description=(
        "REST API wrapper for MedQuery's two-agent CrewAI multi-agent medical research system. "
        "Searches Europe PMC, MedlinePlus, and openFDA, and generates evidence-backed patient medical reports."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    Check API service health and active trusted source domain count.
    """
    return HealthResponse(
        status="ok",
        app="MedQuery Medical Crew REST API",
        version="1.0.0",
        trusted_sources_count=len(TRUSTED_DOMAINS),
    )


@app.get("/api/v1/sources", response_model=SourcesResponse, tags=["Sources"])
def get_trusted_sources():
    """
    Get list of hard-whitelisted medical domains used by MedQuery scraper.
    """
    return SourcesResponse(trusted_domains=sorted(list(TRUSTED_DOMAINS)))


@app.post("/api/v1/search", response_model=QueryResponse, tags=["Search"])
def execute_medical_search(payload: QueryRequest):
    """
    Execute multi-agent CrewAI search for a medical query.
    Agent 1 gathers evidence from whitelisted sources; Agent 2 synthesizes patient explanation.
    """
    logger.info(f"Received API search request for query: '{payload.query}'")
    try:
        report = run_medical_crew(payload.query)
        now_iso = datetime.now(timezone.utc).isoformat()
        return QueryResponse(
            query=payload.query,
            report=report,
            status="success",
            created_at=now_iso,
        )
    except Exception as e:  # noqa: BLE001
        logger.error(f"API search execution failed for query '{payload.query}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Medical crew execution error: {e}",
        ) from e
