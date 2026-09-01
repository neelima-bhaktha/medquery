from typing import List, Optional

from crewai import Agent, Task
from pydantic import BaseModel, Field


class ArticleFinding(BaseModel):
    """Pydantic model representing key findings extracted from a single medical source."""

    source_name: str = Field(default="Medical Source", description="Name of database.")
    title: str = Field(default="Medical Article", description="Title of article or label.")
    url: str = Field(default="", description="Source URL.")
    key_findings: List[str] = Field(default_factory=list, description="Key medical findings or warnings extracted.")


class MedicalResearchReport(BaseModel):
    """Pydantic model representing structured research output from Task 1."""

    query: str = Field(default="", description="Medical query string.")
    summary_of_evidence: Optional[str] = Field(
        default="Evidence gathered from medical sources.", description="Executive summary of evidence."
    )
    findings: List[ArticleFinding] = Field(
        default_factory=list, description="Extracted findings from fetched articles."
    )


def get_research_task(agent: Agent, query: str) -> Task:
    """
    Task 1: Search medical databases, fetch key articles, and generate structured evidence report.
    """
    return Task(
        description=(
            f"Analyze query: '{query}' using provided sources_context input.\n"
            "If sources_context input is present, extract evidence directly from it.\n"
            "Otherwise use search_medical_sources and fetch_article tools.\n"
            "Compile evidence into a structured medical research report."
        ),
        expected_output="Structured research report containing query summary and key medical findings.",
        agent=agent,
    )


def get_explanation_task(agent: Agent, query: str, research_task: Task) -> Task:
    """
    Task 2: Translate research report into a clear medical explanation.
    Receives Task 1 output via context=[research_task].
    """
    desc = (
        f"Review query '{query}' and research report in context.\n"
        "RULES:\n"
        "1. Answer ONLY from retrieved report context.\n"
        "2. Refuse personal medical diagnosis or dosing rules.\n"
        "3. Include Executive Summary, Evidence Breakdown with links, and Interpretation.\n"
        "4. End with exact line:\n"
        "'This information is for educational purposes only and does not constitute medical advice. "
        "Always consult a qualified healthcare professional for medical diagnosis or treatment.'"
    )
    expected = (
        "Markdown medical report from retrieved evidence, concluding with mandatory line: "
        "'This information is for educational purposes only and does not constitute medical advice. "
        "Always consult a qualified healthcare professional for medical diagnosis or treatment.'"
    )

    return Task(
        description=desc,
        expected_output=expected,
        context=[research_task],
        agent=agent,
    )
