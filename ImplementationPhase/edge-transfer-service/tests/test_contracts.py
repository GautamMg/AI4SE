from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

API_TOKEN = "secret-token"


def auth_headers():
    return {"Authorization": f"Bearer {API_TOKEN}"}


def test_openapi_contains_endpoints():
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    paths = data["paths"]
    assert "/api/v1/missions/{mission_id}/scan-and-batch" in paths
    assert "post" in paths["/api/v1/missions/{mission_id}/scan-and-batch"]
    assert "/api/v1/batches/{batch_id}/upload" in paths
    assert "post" in paths["/api/v1/batches/{batch_id}/upload"]


def test_scan_and_batch_contract_validation(tmp_path):
    root = tmp_path / "mission1"
    root.mkdir()
    (root / "a.jpg").write_bytes(b"abc")
    payload = {
        "root_path": str(root),
        "max_files_per_batch": 10,
        "max_batch_bytes": 1024 * 1024,
    }
    resp = client.post(
        "/api/v1/missions/test-mission/scan-and-batch",
        json=payload,
        headers=auth_headers(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["mission_id"] == "test-mission"
    assert isinstance(body["batches"], list)


def test_upload_batch_contract_validation(tmp_path):
    # First create a batch
    root = tmp_path / "mission2"
    root.mkdir()
    (root / "a.jpg").write_bytes(b"123")
    payload = {
        "root_path": str(root),
        "max_files_per_batch": 10,
        "max_batch_bytes": 1024 * 1024,
    }
    resp = client.post(
        "/api/v1/missions/m2/scan-and-batch",
        json=payload,
        headers=auth_headers(),
    )
    assert resp.status_code == 200
    batches = resp.json()["batches"]
    assert batches
    batch_id = batches[0]["batch_id"]

    upload_resp = client.post(
        f"/api/v1/batches/{batch_id}/upload",
        json={},
        headers=auth_headers(),
    )
    assert upload_resp.status_code in (200, 502)
    body = upload_resp.json()
    assert "batch_id" in body
    assert "session_key" in body
