import logging
import time

from src.core.scraper import scrape_article
from src.core.search import search_medical_sources
from src.crew import run_medical_crew

logging.basicConfig(level=logging.INFO)

query = "paracetamol"
print(f"Executing live query: '{query}'")
t0 = time.time()
sources = search_medical_sources(query)[:3]
pre_fetched = []
for s in sources[:2]:
    scraped = scrape_article(s.url)
    text = scraped.get("text", s.snippet)[:1000]
    pre_fetched.append(f"Source: {s.title}\nURL: {s.url}\nType: {s.source_type.upper()}\nContent:\n{text}")

sources_context = "\n\n---\n\n".join(pre_fetched)
print(f"Pre-fetched context size: {len(sources_context)} chars ({time.time() - t0:.2f}s)")

t1 = time.time()
report = run_medical_crew(query, sources_context=sources_context)
print(f"\nSUCCESS! Live Medical Crew finished in {time.time() - t1:.2f}s:\n")
print(report[:400])
