from unittest.mock import patch

from fastapi.testclient import TestClient

# pyrefly: ignore [missing-import]
from src.api.app import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "MedQuery" in data["app"]
    assert data["trusted_sources_count"] > 0


def test_get_trusted_sources_endpoint():
    response = client.get("/api/v1/sources")
    assert response.status_code == 200
    data = response.json()
    assert "trusted_domains" in data
    assert "fda.gov" in data["trusted_domains"]
    assert "medlineplus.gov" in data["trusted_domains"]
    assert "europepmc.org" in data["trusted_domains"]


def test_search_endpoint_validation_error():
    # Empty payload
    res1 = client.post("/api/v1/search", json={})
    assert res1.status_code == 422

    # Short query (< 3 chars)
    res2 = client.post("/api/v1/search", json={"query": "ab"})
    assert res2.status_code == 422


@patch("src.api.app.run_medical_crew")
def test_search_endpoint_success(mock_run_crew):
    mock_run_crew.return_value = "## Mock Medical Report\n\n- Ibuprofen reduces pain.\n\nDisclaimer text."

    payload = {"query": "ibuprofen dosage and side effects"}
    response = client.post("/api/v1/search", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "ibuprofen dosage and side effects"
    assert "Mock Medical Report" in data["report"]
    assert data["status"] == "success"
    assert "created_at" in data
    mock_run_crew.assert_called_once_with("ibuprofen dosage and side effects")
