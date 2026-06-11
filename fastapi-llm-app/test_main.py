import json

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def test_find_incident_uses_app_relative_default_path(monkeypatch):
    monkeypatch.delenv("INCIDENTS_FILE", raising=False)

    incident = main._find_incident("INC001")

    assert incident["incident_id"] == "INC001"
    assert incident["service"] == "checkout-api"


def test_find_incident_returns_404_for_unknown_incident(monkeypatch):
    monkeypatch.delenv("INCIDENTS_FILE", raising=False)

    with pytest.raises(HTTPException) as exc_info:
        main._find_incident("NOPE")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Incident not found: NOPE"


def test_incidents_file_can_be_overridden(monkeypatch, tmp_path):
    incidents_file = tmp_path / "custom-incidents.json"
    incidents_file.write_text(
        json.dumps(
            [
                {
                    "incident_id": "INC999",
                    "service": "search-api",
                    "description": "Search API errors increased after deploy.",
                }
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("INCIDENTS_FILE", str(incidents_file))

    incident = main._find_incident("INC999")

    assert incident["service"] == "search-api"


def test_triage_endpoint_loads_default_incident(monkeypatch):
    monkeypatch.delenv("INCIDENTS_FILE", raising=False)
    monkeypatch.setattr(
        main,
        "_generate_claude_json",
        lambda prompt: {
            "severity": "high",
            "category": "availability",
            "assigned_team": "payments",
            "suggested_action_items": ["Scale checkout-api workers"],
        },
    )

    response = client.post("/triage", json={"incident_id": "INC001"})

    assert response.status_code == 200
    assert response.json()["severity"] == "high"
