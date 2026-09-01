import logging
import time
from typing import List

import requests

from src.core.sources.base import Source

logger = logging.getLogger(__name__)

OPENFDA_URL = "https://api.fda.gov/drug/label.json"


def search_openfda(query: str, limit: int = 3, timeout: float = 2.5) -> List[Source]:
    """
    Search openFDA Drug Labeling API for drug indications, dosage, warnings, and brand names.
    Returns normalized Source objects.
    """
    results: List[Source] = []
    clean_query = query.strip().replace('"', "")
    headers = {"User-Agent": "MedQueryMedicalCrew/1.0"}

    # Search strategy: exact field match first, then broader text search
    search_queries = [
        f'openfda.brand_name:"{clean_query}"+openfda.generic_name:"{clean_query}"',
        f"openfda.brand_name:{clean_query}*+openfda.generic_name:{clean_query}*",
        f'indications_and_usage:"{clean_query}"',
        f"{clean_query}",
    ]

    for search_term in search_queries:
        if len(results) >= limit:
            break

        params = {"search": search_term, "limit": limit}

        try:
            time.sleep(0.1)
            response = requests.get(OPENFDA_URL, params=params, headers=headers, timeout=timeout)
            if response.status_code != 200:
                continue

            data = response.json()
            items = data.get("results", [])

            for item in items:
                openfda_info = item.get("openfda", {})
                brand_names = openfda_info.get("brand_name", [])
                generic_names = openfda_info.get("generic_name", [])

                brand_str = brand_names[0] if brand_names else ""
                generic_str = generic_names[0] if generic_names else ""

                if brand_str and generic_str:
                    title = f"FDA Drug Label: {brand_str} ({generic_str})"
                elif generic_str:
                    title = f"FDA Drug Label: {generic_str}"
                elif brand_str:
                    title = f"FDA Drug Label: {brand_str}"
                else:
                    title = f"FDA Drug Information for {clean_query}"

                # Extract key sections for snippet
                indications = item.get("indications_and_usage", [""])[0]
                warnings = item.get("warnings", [""])[0]
                dosage = item.get("dosage_and_administration", [""])[0]

                snippet_parts = []
                if indications:
                    snippet_parts.append(f"Indications: {indications[:250]}...")
                if warnings:
                    snippet_parts.append(f"Warnings: {warnings[:200]}...")
                if dosage and not snippet_parts:
                    snippet_parts.append(f"Dosage: {dosage[:200]}...")

                fallback_snippet = f"Official openFDA drug label for {clean_query}."
                snippet = " | ".join(snippet_parts) if snippet_parts else fallback_snippet

                # Construct openFDA reference URL
                spl_id = openfda_info.get("spl_id", [""])[0]
                if spl_id:
                    url = f"https://labels.fda.gov/labeldetails.cfm?setid={spl_id}"
                else:
                    url = f"https://api.fda.gov/drug/label.json?search={clean_query}"

                # Avoid duplicate URLs
                if not any(r.url == url for r in results):
                    results.append(
                        Source(
                            title=title,
                            url=url,
                            snippet=snippet,
                            source_type="openfda",
                            score=1.0,
                            extra_meta={
                                "brand_name": brand_str,
                                "generic_name": generic_str,
                                "spl_id": spl_id,
                            },
                        )
                    )
        except Exception as e:  # noqa: BLE001
            logger.warning(f"openFDA query '{search_term}' failed: {e}")

    return results[:limit]
