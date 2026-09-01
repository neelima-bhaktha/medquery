from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Input payload for medical search query."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Medical query, drug name, or symptom string.",
        json_schema_extra={"example": "ibuprofen side effects and dosage"},
    )


class QueryResponse(BaseModel):
    """Output response containing generated Markdown report and execution metadata."""

    query: str = Field(..., description="The original medical query.")
    answer: Optional[str] = Field(default="", description="Synthesized medical response from Explainer Agent.")
    report: Optional[str] = Field(default="", description="Generated Markdown medical report from Explainer Agent.")
    status: str = Field(..., description="Execution status (e.g., success, error, refused).")
    refused: bool = Field(default=False, description="Whether query execution was refused due to rate limit/safety.")
    refusal_reason: Optional[str] = Field(default=None, description="Detailed explanation for query refusal.")
    created_at: str = Field(..., description="ISO 8601 timestamp of response generation.")
    sources: List[Dict[str, Any]] = Field(
        default_factory=list, description="List of verified sources retrieved by Agent 1."
    )
    stats: Dict[str, Any] = Field(default_factory=dict, description="Execution telemetry statistics.")


class HealthResponse(BaseModel):
    """Health status response schema."""

    status: str = Field(..., json_schema_extra={"example": "ok"})
    app: str = Field(..., json_schema_extra={"example": "MedQuery Medical Crew REST API"})
    version: str = Field(..., json_schema_extra={"example": "1.0.0"})
    trusted_sources_count: int = Field(..., json_schema_extra={"example": 9})


class SourcesResponse(BaseModel):
    """Whitelisted trusted domains response schema."""

    trusted_domains: List[str] = Field(..., description="List of approved medical domains.")
