import logging
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# pyrefly: ignore [missing-import]
from src.core.scraper import scrape_article

logger = logging.getLogger(__name__)


class FetchArticleInput(BaseModel):
    """Input schema for fetch_article tool."""

    url: str = Field(
        ...,
        description="The HTTP or HTTPS URL of the medical article or webpage to fetch and parse.",
    )


class FetchArticleTool(BaseTool):
    """
    CrewAI Tool wrapper around core scraper.
    Fetches and cleans article text from a URL (truncated to 2,000 chars).
    """

    name: str = "fetch_article"
    description: str = (
        "Fetches and extracts the main clean text content from a web article URL. "
        "Content is automatically cleaned and truncated to 2,000 characters. "
        "Use this tool to read detailed text from a candidate URL found during search."
    )
    args_schema: Type[BaseModel] = FetchArticleInput

    def _run(self, url: str) -> str:
        """
        Execute web page article fetch. Catches exceptions and returns formatted text or error message.
        """
        try:
            result = scrape_article(url)

            status = result.get("status", "unknown")
            if status == "blocked_by_robots":
                return (
                    f"Unable to fetch article from '{url}': "
                    "Scraping disallowed by robots.txt rules. Please try another URL."
                )
            elif status == "error":
                err_text = result.get("text", "Network or parsing error.")
                return f"Error fetching article from '{url}': {err_text}. Please try another URL."

            title = result.get("title", "Untitled Article")
            text = result.get("text", "").strip()
            cached_str = " (cached)" if result.get("cached") else ""

            if not text:
                return f"Article at '{url}' returned empty text content. Please try another URL."

            return f"--- Article Content: {title}{cached_str} ---\nURL: {url}\n\n{text}\n--- End of Article ---"
        except Exception as e:  # noqa: BLE001
            logger.error(f"Error in FetchArticleTool for URL '{url}': {e}")
            return f"Error fetching article from '{url}': {e}. Please try another URL."
