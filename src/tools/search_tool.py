import logging
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from src.core.search import search_medical_sources

logger = logging.getLogger(__name__)

MAX_SEARCH_RESULTS = 3  # Cap returned search results ceiling


class SearchMedicalSourcesInput(BaseModel):
    """Input schema for search_medical_sources tool."""

    query: str = Field(
        ...,
        description="The medical query, drug name, or condition to search across trusted medical databases.",
    )


class MedicalSearchTool(BaseTool):
    """
    CrewAI Tool wrapper around core parallel search orchestrator.
    Queries Europe PMC, MedlinePlus, and openFDA, returning top 3 candidate URLs and snippets.
    """

    name: str = "search_medical_sources"
    description: str = (
        "Searches trusted medical databases (Europe PMC, MedlinePlus, openFDA). "
        "Returns up to 3 candidate article titles, URLs, and snippets. Use this tool first to find relevant URLs."
    )
    args_schema: Type[BaseModel] = SearchMedicalSourcesInput

    def _run(self, query: str) -> str:
        """
        Execute medical search, capped at top 3 results returning title, URL, and snippet only.
        """
        logger.info(f"[RETRIEVAL TRAIL] MedicalSearchTool invoked | Query: '{query}'")
        try:
            results = search_medical_sources(query)
            # Cap returned search items to top 3 ceiling
            results = results[:MAX_SEARCH_RESULTS]

            logger.info(
                f"[RETRIEVAL TRAIL] MedicalSearchTool complete | Query: '{query}' | Returned {len(results)} source(s)"
            )
            if not results:
                return f"No medical sources found for query: '{query}'."

            output_lines = [f"Found {len(results)} medical source(s) for query: '{query}':\n"]
            for idx, item in enumerate(results, start=1):
                output_lines.append(
                    f"[{idx}] {item.title}\n"
                    f"    Source Type: {item.source_type.upper()}\n"
                    f"    URL: {item.url}\n"
                    f"    Snippet: {item.snippet[:300]}\n"
                )

            return "\n".join(output_lines)
        except Exception as e:  # noqa: BLE001
            logger.error(f"[RETRIEVAL TRAIL] MedicalSearchTool error for query '{query}': {e}")
            return f"Error executing medical search for '{query}': {e}"
