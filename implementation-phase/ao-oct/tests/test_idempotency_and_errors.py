from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

API_TOKEN = "secret-token"


def auth_headers():
    return {"Authorization": f"Bearer {API_TOKEN}"}


def test_idempotent_retry_reuses_run_id(tmp_path):
    from PIL import Image

    img_path = tmp_path / "idem.png"
    img = Image.new("L", (64, 64), color=200)
    img.save(img_path)

    idem_key = "test-idem-key-1"

    with img_path.open("rb") as f1:
        files1 = {"bscan_image": ("idem.png", f1, "image/png")}
        data = {"model_name": "ISOSNet-healthy"}
        resp1 = client.post(
            "/api/v1/eng/runs",
            files=files1,
            data=data,
            headers={**auth_headers(), "Idempotency-Key": idem_key},
        )
    assert resp1.status_code == 201
    run_id1 = resp1.json()["run_id"]

    with img_path.open("rb") as f2:
        files2 = {"bscan_image": ("idem.png", f2, "image/png")}
        resp2 = client.post(
            "/api/v1/eng/runs",
            files=files2,
            data=data,
            headers={**auth_headers(), "Idempotency-Key": idem_key},
        )
    assert resp2.status_code == 201
    run_id2 = resp2.json()["run_id"]

    assert run_id1 == run_id2


def test_missing_auth_rejected(tmp_path):
    from PIL import Image

    img_path = tmp_path / "unauth.png"
    img = Image.new("L", (32, 32), color=50)
    img.save(img_path)

    with img_path.open("rb") as f:
        files = {"bscan_image": ("unauth.png", f, "image/png")}
        data = {"model_name": "ISOSNet-healthy"}
        resp = client.post(
            "/api/v1/eng/runs",
            files=files,
            data=data,
        )

    assert resp.status_code == 401


def test_oversized_upload_rejected(tmp_path, monkeypatch):
    from app import main as app_main

    monkeypatch.setenv("MAX_UPLOAD_BYTES", "1024")
    # Re-import or access the constant if necessary; TestClient reuses app.

    big_file = tmp_path / "big.bin"
    big_file.write_bytes(b"x" * 2048)

    with big_file.open("rb") as f:
        files = {"bscan_image": ("big.bin", f, "image/png")}
        data = {"model_name": "ISOSNet-healthy"}
        resp = client.post(
            "/api/v1/eng/runs",
            files=files,
            data=data,
            headers=auth_headers(),
        )

    assert resp.status_code == 413

