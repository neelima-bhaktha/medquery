from typing import List

from crewai import Agent, Task
from pydantic import BaseModel, Field


class ArticleFinding(BaseModel):
    """Pydantic model representing key findings extracted from a single medical source."""

    source_name: str = Field(
        ...,
        description="Name of the medical database or source (e.g., Europe PMC, MedlinePlus, openFDA).",
    )
    title: str = Field(..., description="Title of the article or drug label.")
    url: str = Field(..., description="Full URL of the article or reference link.")
    key_findings: List[str] = Field(
        ...,
        description="List of key medical findings, trial results, warnings, or dosage details extracted.",
    )
    evidence_quality: str = Field(
        ...,
        description="Quality rating (e.g., High Quality Peer-Reviewed, Official FDA Label, Consumer Health Guide).",
    )


class MedicalResearchReport(BaseModel):
    """Pydantic model representing the complete structured research output from Task 1."""

    query: str = Field(..., description="The original medical query string.")
    summary_of_evidence: str = Field(
        ...,
        description="High-level executive summary of evidence collected across all sources.",
    )
    findings: List[ArticleFinding] = Field(
        ...,
        description="List of structured findings extracted from each fetched article.",
    )
    confidence_score: str = Field(
        ...,
        description="Overall confidence score (e.g., High, Moderate, Low) based on available evidence.",
    )


def get_research_task(agent: Agent, query: str) -> Task:
    """
    Task 1: Search medical databases, fetch key articles, and generate structured Pydantic report.
    """
    return Task(
        description=(
            f"1. Search trusted medical databases for the query: '{query}' using search_medical_sources.\n"
            "2. Identify the most relevant article URLs from the search results.\n"
            "3. Use fetch_article to extract full text content from 2-3 key URLs.\n"
            "4. Analyze the text content and extract key medical findings, drug indications, or clinical trial data.\n"
            "5. Compile the extracted evidence into a clean, structured Pydantic MedicalResearchReport."
        ),
        expected_output=(
            "A structured MedicalResearchReport containing query, summary of evidence, "
            "and a list of ArticleFinding objects (source_name, title, url, key_findings, evidence_quality)."
        ),
        output_pydantic=MedicalResearchReport,
        agent=agent,
    )


def get_explanation_task(agent: Agent, query: str, research_task: Task) -> Task:
    """
    Task 2: Translate structured research report into a clear, patient-friendly medical explanation.
    Receives Task 1 output via context=[research_task].
    """
    desc = (
        f"Review the user query '{query}' and the structured medical research report provided in your context.\n\n"
        "STRICT GROUNDING & SAFETY RULES:\n"
        "1. You MUST answer ONLY from the provided research report context. If the report doesn't cover a topic, "
        "explicitly state that the information is not available in the retrieved report instead of guessing.\n"
        "2. Refuse any requests for specific personal medical diagnoses or personalized prescription dosing rules.\n"
        "3. Synthesize findings into Executive Summary, Evidence Breakdown with clickable links, and Interpretation.\n"
        "4. Your response MUST conclude with the exact line:\n"
        "'This information is for educational purposes only and does not constitute medical advice. "
        "Always consult a qualified healthcare professional for medical diagnosis or treatment.'"
    )
    expected = (
        "A Markdown medical report derived exclusively from retrieved evidence, refusing personal diagnosis/dosing, "
        "and concluding with the mandatory line: 'This information is for educational purposes only and does not "
        "constitute medical advice. Always consult a qualified healthcare professional for medical diagnosis "
        "or treatment.'"
    )

    return Task(
        description=desc,
        expected_output=expected,
        context=[research_task],
        agent=agent,
    )
