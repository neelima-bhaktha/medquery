import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# pyrefly: ignore [missing-import]
from src.api.schemas import HealthResponse, QueryRequest, QueryResponse, SourcesResponse

# pyrefly: ignore [missing-import]
from src.config.validation import validate_config

# pyrefly: ignore [missing-import]
from src.core.scraper import scrape_article

# pyrefly: ignore [missing-import]
from src.core.search import search_medical_sources

# pyrefly: ignore [missing-import]
from src.core.whitelist import TRUSTED_DOMAINS

# pyrefly: ignore [missing-import]
from src.crew import run_medical_crew

logger = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to run startup validation."""
    logger.info("Initializing MedQuery FastAPI REST Server...")
    validate_config()
    yield
    logger.info("Shutting down MedQuery FastAPI REST Server...")


app = FastAPI(
    title="MedQuery Medical Crew REST API",
    description="REST API interface for multi-agent medical evidence research and patient explanation.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    """Health check endpoint validating application configuration and API readiness."""
    return HealthResponse(
        status="ok",
        app="MedQuery Medical Crew REST API",
        version="1.0.0",
        trusted_sources_count=len(TRUSTED_DOMAINS),
    )


@app.get("/api/v1/sources", response_model=SourcesResponse, tags=["Sources"])
def get_trusted_sources():
    """Returns list of whitelisted trusted medical domains."""
    return SourcesResponse(trusted_domains=sorted(list(TRUSTED_DOMAINS)))


@app.post("/query", response_model=QueryResponse, tags=["Search"])
@app.post("/api/v1/search", response_model=QueryResponse, tags=["Search"], include_in_schema=False)
def execute_medical_search(payload: QueryRequest):
    """
    Execute multi-agent CrewAI search for a medical query.
    Pre-searches trusted sources deterministically, then invokes crew for report generation.
    """
    logger.info(f"Received API search request for query: '{payload.query}'")
    start_time = time.time()
    try:
        # 1. Deterministic parallel pre-search across medical source APIs
        found_sources = search_medical_sources(payload.query)[:3]

        pre_fetched = []
        api_sources = []
        for s in found_sources:
            api_sources.append(
                {
                    "title": s.title,
                    "url": s.url,
                    "snippet": s.snippet,
                    "origin": s.source_type,
                    "identifier": f"{s.source_type.upper()}:retrieved",
                    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                }
            )

        # Scrape top 2 candidate articles for compact text context
        for s in found_sources[:2]:
            scraped = scrape_article(s.url)
            # pyrefly: ignore [unsupported-operation]
            text = scraped.get("text", s.snippet)[:1000]
            pre_fetched.append(f"Source: {s.title}\nURL: {s.url}\nType: {s.source_type.upper()}\nContent:\n{text}")

        sources_context = "\n\n---\n\n".join(pre_fetched) if pre_fetched else "No medical sources retrieved."

        # 2. Run CrewAI crew with pre-fetched sources context (low token usage)
        report = run_medical_crew(payload.query, sources_context=sources_context)
        elapsed_ms = int((time.time() - start_time) * 1000)
        now_iso = datetime.now(timezone.utc).isoformat()

        stats_data = {
            "llm_calls": 2,
            "latency_ms": elapsed_ms,
            "tokens_in": len(sources_context) // 4 + 300,
            "tokens_out": len(report) // 4,
            "sources_found": len(found_sources),
            "sources_kept": len(api_sources),
            "routed_to": list({s.source_type for s in found_sources}),
        }

        return QueryResponse(
            query=payload.query,
            answer=report,
            report=report,
            status="success",
            created_at=now_iso,
            sources=api_sources,
            stats=stats_data,
        )
    except Exception as e:  # noqa: BLE001
        err_msg = str(e)
        logger.error(f"API search execution failed for query '{payload.query}': {err_msg}")

        now_iso = datetime.now(timezone.utc).isoformat()
        reason = (
            "The request exceeded the LLM rate/token limit or encountered a model constraint. "
            "Try a narrower query."
        )

        return QueryResponse(
            query=payload.query,
            answer=reason,
            report="",
            status="refused",
            refused=True,
            refusal_reason=reason,
            created_at=now_iso,
            sources=[],
            stats={
                "llm_calls": 0,
                "latency_ms": int((time.time() - start_time) * 1000),
                "tokens_in": 0,
                "tokens_out": 0,
                "sources_found": 0,
                "sources_kept": 0,
                "routed_to": [],
            },
        )


# --- Static Files Mount (MUST BE THE LAST ROUTE REGISTERED) ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")
if not os.path.exists(STATIC_DIR):
    STATIC_DIR = os.path.join(PROJECT_ROOT, "src", "static")

if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
