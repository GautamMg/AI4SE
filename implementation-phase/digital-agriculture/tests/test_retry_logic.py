from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

API_TOKEN = "secret-token"


def auth_headers():
    return {"Authorization": f"Bearer {API_TOKEN}"}


def test_retry_logic_with_fail_first(tmp_path, monkeypatch):
    root = tmp_path / "mission-retry"
    root.mkdir()
    (root / "a.jpg").write_bytes(b"abc")

    monkeypatch.setenv("TAPIS_FAIL_FIRST", "true")

    payload = {
        "root_path": str(root),
        "max_files_per_batch": 10,
        "max_batch_bytes": 1024 * 1024,
    }
    resp = client.post(
        "/api/v1/missions/retry/scan-and-batch",
        json=payload,
        headers=auth_headers(),
    )
    assert resp.status_code == 200
    batch_id = resp.json()["batches"][0]["batch_id"]

    first = client.post(
        f"/api/v1/batches/{batch_id}/upload",
        json={},
        headers=auth_headers(),
    )
    assert first.status_code == 502

    second = client.post(
        f"/api/v1/batches/{batch_id}/upload",
        json={},
        headers=auth_headers(),
    )
    assert second.status_code == 200
    body = second.json()
    assert body["status"] == "COMPLETED"
    assert body["retry_count"] >= 1

    monkeypatch.delenv("TAPIS_FAIL_FIRST", raising=False)
