# pyrefly: ignore [missing-import]
from src.core.router import classify_query

# pyrefly: ignore [missing-import]
from src.core.search import search_medical_sources

# pyrefly: ignore [missing-import]
from src.core.sources import (
    Source,
    search_europepmc,
    search_medlineplus,
    search_openfda,
)


def test_source_dataclass():
    s = Source(
        title="Test Title",
        url="https://example.com",
        snippet="Test snippet text",
        source_type="openfda",
    )
    assert s.title == "Test Title"
    assert s.url == "https://example.com"
    assert s.source_type == "openfda"
    assert s.score == 1.0
    assert isinstance(s.extra_meta, dict)


def test_classify_query_drug():
    sources = classify_query("ibuprofen dosage and side effects")
    assert "openfda" in sources
    assert "medlineplus" in sources


def test_classify_query_research():
    sources = classify_query("clinical trial evidence for metformin in long covid")
    assert "europepmc" in sources


def test_classify_query_condition():
    sources = classify_query("chest pain and shortness of breath symptoms")
    assert "medlineplus" in sources
    assert "europepmc" in sources


def test_classify_query_fallback():
    sources = classify_query("general health question 12345")
    assert len(sources) == 3
    assert set(sources) == {"medlineplus", "europepmc", "openfda"}


def test_live_search_europepmc():
    results = search_europepmc("diabetes metformin", limit=2)
    assert isinstance(results, list)
    if results:
        assert isinstance(results[0], Source)
        assert results[0].source_type == "europepmc"
        assert results[0].url.startswith("http")


def test_live_search_medlineplus():
    results = search_medlineplus("hypertension", limit=2)
    assert isinstance(results, list)
    assert len(results) > 0
    assert results[0].source_type == "medlineplus"


def test_live_search_openfda():
    results = search_openfda("aspirin", limit=2)
    assert isinstance(results, list)
    if results:
        assert results[0].source_type == "openfda"


def test_search_medical_sources_parallel():
    results = search_medical_sources("ibuprofen side effects", limit_per_source=2)
    assert isinstance(results, list)
    assert len(results) > 0
    # Ensure all items are normalized Source instances
    for item in results:
        assert isinstance(item, Source)
        assert item.title
        assert item.url
        assert item.snippet
