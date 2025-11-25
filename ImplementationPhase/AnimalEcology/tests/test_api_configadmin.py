from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

BASE_HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Actor-Id": "scientist-1",
    "X-Actor-Role": "WildlifeScientist",
}


def _sample_payload() -> dict:
    return {
        "aois": [
            {
                "id": "aoi-1",
                "name": "River Bend",
                "polygon_ref": "s3://bucket/aoi/river-bend.geojson",
                "altitude_m": 120,
                "overlap_percent": 60,
            }
        ],
        "species_thresholds": [
            {
                "aoi_id": "aoi-1",
                "species": "elephant",
                "min_confidence": 0.8,
            }
        ],
        "model_config": {
            "model_version_id": "detector-v1",
            "rollout_group": "edge-ring-1",
            "notes": "Initial deployment",
        },
    }


def test_create_change_set_contract_and_happy_path() -> None:
    """US-14/US-15/US-20: create config and verify response shape."""
    response = client.post(
        "/config/change-sets",
        json=_sample_payload(),
        headers=BASE_HEADERS,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["config_version"].startswith("v")
    assert body["actor_id"] == "scientist-1"
    assert body["actor_role"] == "WildlifeScientist"
    assert isinstance(body["aois"], list) and body["aois"]
    assert isinstance(body["species_thresholds"], list) and body["species_thresholds"]
    assert "signature" in body and len(body["signature"]) == 64


def test_get_latest_config_contract() -> None:
    """US-20: latest config can be fetched after creation."""
    client.post(
        "/config/change-sets",
        json=_sample_payload(),
        headers=BASE_HEADERS,
    )
    response = client.get("/config/latest", headers=BASE_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["config_version"].startswith("v")
    assert body["aois"][0]["id"] == "aoi-1"


def test_auth_failure() -> None:
    """Security: invalid token must be rejected."""
    response = client.post(
        "/config/change-sets",
        json=_sample_payload(),
        headers={"Authorization": "Bearer wrong-token"},
    )
    assert response.status_code == 401


def test_health_endpoint() -> None:
    """Observability: health endpoint returns status and metrics."""
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "metrics" in body
    assert isinstance(body["metrics"], dict)
