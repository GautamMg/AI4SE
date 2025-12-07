from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

API_TOKEN = "secret-token"


def auth_headers():
    return {"Authorization": f"Bearer {API_TOKEN}"}


def test_happy_path_scan_and_upload(tmp_path, monkeypatch):
    root = tmp_path / "mission-happy"
    root.mkdir()
    for i in range(3):
        (root / f"img_{i}.jpg").write_bytes(b"x" * 10)

    # Point HPC storage to a temp dir (stub client uses env on init, but we at least ensure path exists)
    from app.tapis_client import TapisClientStub

    hpc_dir = tmp_path / "hpc"
    TapisClientStub(str(hpc_dir)).ensure_base_dir()

    payload = {
        "root_path": str(root),
        "max_files_per_batch": 10,
        "max_batch_bytes": 1024 * 1024,
    }
    resp = client.post(
        "/api/v1/missions/happy/scan-and-batch",
        json=payload,
        headers=auth_headers(),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["batches"]
    batch_id = data["batches"][0]["batch_id"]

    upload_resp = client.post(
        f"/api/v1/batches/{batch_id}/upload",
        json={},
        headers=auth_headers(),
    )
    assert upload_resp.status_code == 200
    body = upload_resp.json()
    assert body["status"] == "COMPLETED"
    assert body["remote_path"]
