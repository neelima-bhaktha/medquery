from typing import List

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
    report: str = Field(..., description="Generated Markdown medical report from Explainer Agent.")
    status: str = Field(..., description="Execution status (e.g., success, error).")
    created_at: str = Field(..., description="ISO 8601 timestamp of response generation.")


class HealthResponse(BaseModel):
    """Health status response schema."""

    status: str = Field(..., json_schema_extra={"example": "ok"})
    app: str = Field(..., json_schema_extra={"example": "MedQuery Medical Crew REST API"})
    version: str = Field(..., json_schema_extra={"example": "1.0.0"})
    trusted_sources_count: int = Field(..., json_schema_extra={"example": 9})


class SourcesResponse(BaseModel):
    """Whitelisted trusted domains response schema."""

    trusted_domains: List[str] = Field(..., description="List of approved medical domains.")
