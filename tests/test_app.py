import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
import app.main as main_module
from datetime import datetime

client = TestClient(main_module.app)

def test_healthz_endpoint():
    """GET /healthz should return status ok"""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_moderate_endpoint(monkeypatch):
    """POST /moderate should return mapped labels and scores"""
    monkeypatch.setattr(main_module, 'moderate_named', lambda text: {'not_offensive': 0.9, 'hate_speech': 0.1})
    response = client.post("/moderate", json={"text": "any"})
    assert response.status_code == 200
    assert response.json() == {'not_offensive': 0.9, 'hate_speech': 0.1}

def test_parse_timestamps_empty():
    """parse_timestamps on empty lines returns empty list"""
    from scripts.compute_rps import parse_timestamps
    assert parse_timestamps([]) == []

def test_parse_timestamps_valid():
    """parse_timestamps should extract datetime objects from mixed lines"""
    from scripts.compute_rps import parse_timestamps
    lines = [
        "INFO:2025-07-01T12:00:00 Something happened",
        "Bad line",
        "2025-07-01T12:00:01",
    ]
    results = parse_timestamps(lines)
    assert len(results) == 2
    assert all(isinstance(ts, datetime) for ts in results)
    assert results[0].strftime("%Y-%m-%dT%H:%M:%S") == "2025-07-01T12:00:00"
    assert results[1].strftime("%Y-%m-%dT%H:%M:%S") == "2025-07-01T12:00:01"