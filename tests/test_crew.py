from crewai import Process

from src.crew import (
    build_medical_crew,
    create_explainer_agent,
    create_researcher_agent,
    get_explanation_task,
    get_research_task,
)
from src.crew.tasks import MedicalResearchReport

TEST_MODEL = "groq/llama-3.3-70b-versatile"


def test_agent_tool_configurations():
    researcher = create_researcher_agent(TEST_MODEL, enable_tools=True)
    explainer = create_explainer_agent(TEST_MODEL)

    # Agent 1 (Researcher) MUST have both tools
    assert len(researcher.tools) == 2
    tool_names = [t.name for t in researcher.tools]
    assert "search_medical_sources" in tool_names
    assert "fetch_article" in tool_names

    # Agent 2 (Explainer) MUST have ZERO tools
    assert len(explainer.tools) == 0

    # Agent 2 backstory MUST contain grounding, refusal, and disclaimer rules
    assert "STRICT GROUNDING RULE" in explainer.backstory
    assert "REFUSAL RULE" in explainer.backstory
    assert "MANDATORY DISCLAIMER" in explainer.backstory


def test_task_configurations_and_context():
    query = "ibuprofen dosage and side effects"

    researcher = create_researcher_agent(TEST_MODEL)
    explainer = create_explainer_agent(TEST_MODEL)

    research_task = get_research_task(researcher, query)
    explanation_task = get_explanation_task(explainer, query, research_task)

    # Task 1 MUST output MedicalResearchReport Pydantic model
    assert research_task.output_pydantic == MedicalResearchReport

    # Task 2 MUST pass Task 1 in context
    assert explanation_task.context == [research_task]

    # Task 2 expected output MUST require mandatory disclaimer
    assert "does not constitute medical advice" in explanation_task.expected_output


def test_build_medical_crew():
    query = "metformin indications"

    crew = build_medical_crew(query, llm=TEST_MODEL)

    assert crew.process == Process.sequential
    assert len(crew.agents) == 2
    assert len(crew.tasks) == 2
