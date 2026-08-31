from typing import Any

from crewai import Agent

from src.crew.prompts import (
    EXPLAINER_BACKSTORY,
    EXPLAINER_GOAL,
    EXPLAINER_ROLE,
    RESEARCHER_BACKSTORY,
    RESEARCHER_GOAL,
    RESEARCHER_ROLE,
)
from src.tools import FetchArticleTool, MedicalSearchTool


def create_researcher_agent(llm: Any) -> Agent:
    """
    Agent 1 (Medical Researcher): Has both tools (search_medical_sources and fetch_article).
    Gathers evidence and compiles structured Pydantic research report.
    """
    return Agent(
        role=RESEARCHER_ROLE,
        goal=RESEARCHER_GOAL,
        backstory=RESEARCHER_BACKSTORY,
        tools=[MedicalSearchTool(), FetchArticleTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def create_explainer_agent(llm: Any) -> Agent:
    """
    Agent 2 (Medical Explainer): Has ZERO tools.
    Receives Task 1 report via context=[research_task] and synthesizes patient-friendly response.
    """
    return Agent(
        role=EXPLAINER_ROLE,
        goal=EXPLAINER_GOAL,
        backstory=EXPLAINER_BACKSTORY,
        tools=[],  # Strictly zero tools
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
