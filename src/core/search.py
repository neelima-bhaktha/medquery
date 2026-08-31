import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

# pyrefly: ignore [missing-import]
from src.core.router import classify_query

# pyrefly: ignore [missing-import]
from src.core.sources import (
    Source,
    search_europepmc,
    search_medlineplus,
    search_openfda,
)

logger = logging.getLogger(__name__)

SOURCE_MAP = {
    "europepmc": search_europepmc,
    "medlineplus": search_medlineplus,
    "openfda": search_openfda,
}


def search_medical_sources(
    query: str,
    mode: str = "deterministic",
    limit_per_source: int = 3,
    sources_override: Optional[List[str]] = None,
    max_workers: int = 3,
) -> List[Source]:
    """
    Search medical sources in parallel using ThreadPoolExecutor.

    Args:
        query: Medical search query string.
        mode: Routing mode ('deterministic' or 'agent').
        limit_per_source: Maximum results per source API.
        sources_override: Specific list of sources to query (bypasses router).
        max_workers: Max parallel thread workers.

    Returns:
        Normalized, deduplicated list of Source objects.
    """
    if sources_override:
        target_sources = [s.lower() for s in sources_override if s.lower() in SOURCE_MAP]
    elif mode == "deterministic":
        target_sources = classify_query(query)
    else:
        # Default fallback to all sources if unrecognized mode
        target_sources = ["medlineplus", "europepmc", "openfda"]

    logger.info(f"Searching medical query '{query}' using sources: {target_sources}")

    all_sources: List[Source] = []

    # Run source searches in parallel with ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_source = {
            executor.submit(SOURCE_MAP[source_name], query, limit_per_source): source_name
            for source_name in target_sources
            if source_name in SOURCE_MAP
        }

        for future in as_completed(future_to_source):
            source_name = future_to_source[future]
            try:
                source_results = future.result(timeout=10)
                all_sources.extend(source_results)
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Parallel fetch for source '{source_name}' failed: {e}")

    # Deduplicate results based on URL and title similarity
    deduped_sources: List[Source] = []
    seen_urls = set()
    seen_titles = set()

    for item in all_sources:
        normalized_url = item.url.lower().rstrip("/")
        normalized_title = item.title.lower().strip()

        if normalized_url not in seen_urls and normalized_title not in seen_titles:
            seen_urls.add(normalized_url)
            seen_titles.add(normalized_title)
            deduped_sources.append(item)

    return deduped_sources
