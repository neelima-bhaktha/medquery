import logging
import time
from typing import List
import requests
from src.core.sources.base import Source

logger = logging.getLogger(__name__)

MEDLINEPLUS_SERVICE_URL = "https://connect.medlineplus.gov/service"


def search_medlineplus(query: str, limit: int = 3, timeout: int = 5) -> List[Source]:
    """
    Search MedlinePlus Web Service for patient & consumer health information.
    Returns normalized Source objects.
    """
    results: List[Source] = []
    headers = {"User-Agent": "MedQueryMedicalCrew/1.0"}

    # Attempt 1: MedlinePlus Connect Web Service API (JSON)
    params = {
        "knowledgeResponseType": "application/json",
        "mainSearchCriteria.v.cs": "2.16.840.1.113883.6.103",
        "mainSearchCriteria.v.c": query,
    }

    try:
        time.sleep(0.1)
        response = requests.get(MEDLINEPLUS_SERVICE_URL, params=params, headers=headers, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            feed = data.get("feed", {})
            entries = feed.get("entry", [])
            if isinstance(entries, dict):
                entries = [entries]

            for entry in entries[:limit]:
                title_obj = entry.get("title", {})
                title = title_obj.get("_value", "MedlinePlus Medical Topic") if isinstance(title_obj, dict) else str(title_obj)

                summary_obj = entry.get("summary", {})
                snippet = summary_obj.get("_value", title) if isinstance(summary_obj, dict) else str(summary_obj)

                link_objs = entry.get("link", [])
                if isinstance(link_objs, dict):
                    link_objs = [link_objs]

                url = "https://medlineplus.gov"
                for link in link_objs:
                    if isinstance(link, dict) and link.get("href"):
                        url = link.get("href")
                        break

                results.append(
                    Source(
                        title=title,
                        url=url,
                        snippet=snippet,
                        source_type="medlineplus",
                        score=1.0,
                    )
                )

    except Exception as e:
        logger.warning(f"MedlinePlus primary search failed for query '{query}': {e}")

    # Fallback search if Connect API returned 0 results or failed
    if not results:
        try:
            fallback_url = "https://service.nlm.nih.gov/medlineplus/spaces/search"
            fallback_params = {"term": query, "db": "mplus", "retmode": "json"}
            resp = requests.get(fallback_url, params=fallback_params, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("results", [])
                for item in items[:limit]:
                    title = item.get("title", "MedlinePlus Health Topic")
                    url = item.get("url", f"https://medlineplus.gov/search.html?q={query}")
                    snippet = item.get("snippet", title)
                    results.append(
                        Source(
                            title=title,
                            url=url,
                            snippet=snippet,
                            source_type="medlineplus",
                            score=1.0,
                        )
                    )
        except Exception as e:
            logger.warning(f"MedlinePlus fallback search failed for query '{query}': {e}")

    # Direct fallback search page entry if API returns empty
    if not results:
        results.append(
            Source(
                title=f"MedlinePlus Search: {query}",
                url=f"https://medlineplus.gov/search.html?q={query}",
                snippet=f"Official MedlinePlus consumer health topic resources and information for '{query}'.",
                source_type="medlineplus",
                score=0.8,
            )
        )

    return results[:limit]
