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


def create_researcher_agent(llm: Any, enable_tools: bool = False) -> Agent:
    """
    Agent 1 (Medical Researcher).
    When enable_tools=False (default), zero tools are attached so evidence is extracted
    directly from pre-fetched input context in 1 LLM call with minimal token usage.
    """
    tools = [MedicalSearchTool(), FetchArticleTool()] if enable_tools else []
    return Agent(
        role=RESEARCHER_ROLE,
        goal=RESEARCHER_GOAL,
        backstory=RESEARCHER_BACKSTORY,
        tools=tools,
        llm=llm,
        verbose=True,
        max_iter=3,
        allow_delegation=False,
    )


def create_explainer_agent(llm: Any) -> Agent:
    """
    Agent 2 (Medical Explainer): Zero tools, max_iter=3.
    Receives Task 1 report via context=[research_task] and synthesizes patient-friendly response.
    """
    return Agent(
        role=EXPLAINER_ROLE,
        goal=EXPLAINER_GOAL,
        backstory=EXPLAINER_BACKSTORY,
        tools=[],  # Strictly zero tools
        llm=llm,
        verbose=True,
        max_iter=3,
        allow_delegation=False,
    )
