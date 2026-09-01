# Medical Crew

A two-agent system that answers medical questions using only evidence retrieved from trusted
sources. The first agent gathers and filters articles. The second agent answers the question using
that report and nothing else.

Built with CrewAI, FastAPI, and a hand-written retrieval layer.

---

## Design constraints

This project was built under three deliberate constraints:

1. **Minimal AI.** Exactly two language model calls per query. Everything else - routing, search,
   scraping, filtering, deduplication - is deterministic Python.
2. **Hand-written prompts.** No generated or framework-default agent instructions. Every role, goal,
   backstory, and expected output was written by hand and tuned against real runs.
3. **No search libraries.** No SerperDev, Brave Search, or `crewai-tools` scrapers. The retrieval
   layer calls medical APIs directly and parses the responses.

The constraints are the point. Any framework can wire two agents together; the interesting work is
in what sits underneath them.

---

## How it works

```
query
  |
  v
router            deterministic: which sources match this query type
  |
  v
source APIs       Europe PMC / MedlinePlus / openFDA, called in parallel
  |
  v
normalise         each API response mapped to a common Source object
  |
  v
filter            domain whitelist, minimum length, deduplication by DOI/PMID
  |
  v
Agent 1           writes a structured research report        [LLM call 1]
  |
  v
Agent 2           answers using only the report              [LLM call 2]
  |
  v
response
```

Agent 2 has no tools and no network access. If a fact is not in the report, it cannot appear in the
answer. This is the core safety property of the system.

---

## Sources

| Source | Provides | Notes |
| --- | --- | --- |
| Europe PMC | Peer-reviewed literature and abstracts | Primary. Mirrors PubMed and adds preprints |
| PubMed E-utilities | Same corpus as Europe PMC | Fallback only, to avoid duplicate results |
| MedlinePlus | Plain-language condition summaries | Patient-facing language |
| openFDA | Drug labels, warnings, adverse reactions | Regulatory text |

Europe PMC and PubMed are treated as one logical source because their corpora overlap almost
entirely. Querying both would return the same paper under two identifiers.

---

## Routing

Queries are classified in plain Python before any model call:

- Drug name detected: openFDA and MedlinePlus
- Condition or symptom: MedlinePlus and Europe PMC
- Research phrasing (evidence, trials, meta-analysis): Europe PMC only
- No medical intent detected: the crew does not run

Deterministic routing is the default because it is predictable and costs nothing. An agent-driven
alternative, where Agent 1 selects tools itself, is available behind a flag for comparison.

---

## Guardrails

- Requests are only made to whitelisted domains.
- Scraped pages below a minimum text length are discarded, which removes paywalls and cookie walls.
- Agent 2 is instructed to answer only from the provided report and to state clearly when the report
  does not cover something.
- Dosing and diagnostic requests are declined.
- Every response carries a notice that the output is not medical advice.
- If no sources survive filtering, Agent 2 is never called and the API returns a refusal.

---

## Project structure

```
medical-crew/
├── main.py                   entry point
├── src/
│   ├── core/                 pure Python, no CrewAI, no LLM
│   │   ├── sources/          one module per API, uniform signature
│   │   ├── router.py         query classification
│   │   ├── search.py         orchestration, merge, dedupe, truncate
│   │   ├── scraper.py        requests + BeautifulSoup extraction
│   │   ├── cache.py          disk cache keyed by URL
│   │   └── whitelist.py      allowed domains, robots.txt checks
│   ├── tools/                thin BaseTool wrappers over core/
│   ├── crew/                 agents, tasks, prompts, crew assembly
│   ├── config/               model settings, limits, source list
│   └── api.py                FastAPI application
├── static/                   demo console (single HTML file)
├── tests/
├── Dockerfile
└── compose.yaml
```

The separation between `core/` and `tools/` is intentional. Everything in `core/` runs without an
API key, which means the retrieval layer can be developed and tested without spending model calls,
and the test suite runs in CI for free.

---

## Setup

Requires Python 3.10 or later.

```bash
git clone <repository-url>
cd medical-crew

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env             # add your model API key
```

Run the API:

```bash
uvicorn src.api:app --reload --port 8000
```

Open `http://localhost:8000/` for the demo console.

The console is served by FastAPI itself so that the page and the API share an origin. Opening the
HTML file directly from disk will not work, because browsers block requests from `file://` origins.

---

## API

### `GET /health`

Returns `{"status": "ok"}` without touching the model. Used by the container health check and the
deployment smoke test.

### `POST /query`

Request:

```json
{ "query": "what are the early symptoms of type 2 diabetes" }
```

Response:

```json
{
  "answer": "text from Agent 2",
  "refused": false,
  "refusal_reason": null,
  "report": { "sources": [] },
  "stats": {
    "llm_calls": 2,
    "latency_ms": 13840,
    "tokens_in": 5920,
    "tokens_out": 410,
    "sources_found": 9,
    "sources_kept": 4,
    "routed_to": ["medlineplus", "europepmc"]
  }
}
```

`answer` is the only required field. The demo console renders the rest when present and falls back
to empty states when absent.

---

## Demo console

A single HTML page at `static/index.html`, served at the application root. It shows the retrieval
report and the final answer side by side, so the handoff between the two agents is visible rather
than described. The telemetry bar reports model calls, latency, token counts, and which sources were
routed to, which is how the minimal-AI constraint is verified rather than merely claimed.

Refusal paths are designed screens, not empty results. Off-topic queries and queries that return no
sources both produce an explicit explanation of why Agent 2 was not called.

---

## Caching

Fetched pages are cached on disk, keyed by a hash of the URL. During development this turns a four
second run into an instant one, avoids rate limits on repeated runs, and makes output changes
attributable to prompt edits rather than shifting API results.

The cache is mounted as a Docker volume so it survives container restarts. Entries expire after 24
hours. A `--no-cache` flag forces a live run for demonstrations.

---

## Token budget

Free-tier model limits are the practical constraint on this system. The measures that keep requests
inside them:

- Search results return title and snippet only, never full text.
- Scraped article text is truncated at a fixed character limit inside the tool, before it reaches
  the model.
- The number of sources passed forward is capped.
- Retrieval runs before the crew, so tool results do not accumulate in the message history across
  iterations.

A request that exceeds the per-minute token limit fails immediately rather than retrying, because
retrying a request larger than the entire budget cannot succeed.

---

## Testing

```bash
pytest tests/
ruff check .
```

Covered: scraper extraction, domain whitelist, query routing, deduplication, truncation, and an
end-to-end run with the model mocked. No test requires an API key.

---

## Docker

```bash
docker build -t medical-crew .
docker run --rm -p 8000:8000 --env-file .env medical-crew
```

Or with the persistent cache volume:

```bash
docker compose up
```

The image runs as a non-root user. API keys are passed at runtime and are never built into the
image.

---

## Continuous delivery

On push to `main`, GitHub Actions runs the linter and test suite, then builds and pushes an image
tagged with the commit SHA. Tests gate the build, so an image that fails its own test suite is never
published.

---

## Notes and limitations

- Answer quality depends entirely on retrieval quality. If the sources are thin, the correct
  behaviour is a refusal, not a confident answer.
- Small models are unreliable at tool selection, which is part of why deterministic routing is the
  default path.
- Scraped full text varies in quality across publishers. Abstracts are more consistent and are
  preferred where available.
- This is a student project for evaluating multi-agent retrieval patterns. It is not a clinical tool
  and must not be used for medical decisions.
