import logging
import time
from typing import List

import requests

from src.core.sources.base import Source

logger = logging.getLogger(__name__)

EUROPE_PMC_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def search_europepmc(query: str, limit: int = 3, timeout: float = 2.5) -> List[Source]:
    """
    Search Europe PMC REST API for scientific literature, trials, and research papers.
    Returns normalized Source objects.
    """
    results: List[Source] = []
    params = {
        "query": query,
        "format": "json",
        "pageSize": limit,
        "resultType": "core",
    }
    headers = {"User-Agent": "MedQueryMedicalCrew/1.0"}

    try:
        # Small delay for rate-limiting compliance
        time.sleep(0.1)
        response = requests.get(EUROPE_PMC_URL, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        data = response.json()

        items = data.get("resultList", {}).get("result", [])
        for item in items[:limit]:
            title = item.get("title", "Untitled Research Paper").rstrip(".")
            abstract = item.get("abstractText", "")
            pmid = item.get("pmid")
            doi = item.get("doi")
            journal = item.get("journalTitle", "")
            pub_year = item.get("pubYear", "")

            # Construct clean article URL
            if doi:
                url = f"https://doi.org/{doi}"
            elif pmid:
                url = f"https://europepmc.org/article/MED/{pmid}"
            else:
                item_id = item.get("id", "")
                url = f"https://europepmc.org/abstract/MED/{item_id}" if item_id else "https://europepmc.org"

            # Create informative snippet
            snippet_parts = []
            if journal or pub_year:
                snippet_parts.append(f"[{journal} {pub_year}]".strip())
            if abstract:
                snippet_parts.append(abstract)
            else:
                author = item.get("authorString", "")
                if author:
                    snippet_parts.append(f"Authors: {author}")

            snippet = " ".join(snippet_parts) if snippet_parts else title

            results.append(
                Source(
                    title=title,
                    url=url,
                    snippet=snippet,
                    source_type="europepmc",
                    score=1.0,
                    extra_meta={
                        "pmid": pmid,
                        "doi": doi,
                        "journal": journal,
                        "pub_year": pub_year,
                    },
                )
            )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"Europe PMC search failed for query '{query}': {e}")

    return results
