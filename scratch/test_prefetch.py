import logging
import time

from src.core.scraper import scrape_article
from src.core.search import search_medical_sources

logging.basicConfig(level=logging.INFO)

query = "paracetamol"
print(f"Testing pre-fetch for query: '{query}'")
t0 = time.time()
sources = search_medical_sources(query)[:3]
print(f"Found {len(sources)} sources in {time.time() - t0:.2f}s:")
for s in sources:
    print(f" - [{s.source_type}] {s.title} ({s.url})")

pre_fetched = []
for s in sources[:2]:
    scraped = scrape_article(s.url)
    text = scraped.get("text", s.snippet)[:800]
    pre_fetched.append(f"Source: {s.title}\nURL: {s.url}\nType: {s.source_type}\nText:\n{text}")

context_str = "\n\n---\n\n".join(pre_fetched)
print(f"Pre-fetched context character length: {len(context_str)}")
