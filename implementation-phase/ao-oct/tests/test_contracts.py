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
    assert "/health" in paths
    assert "get" in paths["/health"]
    assert "/api/v1/eng/runs" in paths
    assert "post" in paths["/api/v1/eng/runs"]
    assert "/api/v1/eng/runs/{run_id}" in paths
    assert "get" in paths["/api/v1/eng/runs/{run_id}"]


def test_create_run_contract_validation(tmp_path):
    from PIL import Image

    img_path = tmp_path / "bscan.png"
    img = Image.new("L", (64, 64), color=128)
    img.save(img_path)

    with img_path.open("rb") as f:
        files = {"bscan_image": ("bscan.png", f, "image/png")}
        data = {"model_name": "ISOSNet-healthy", "confidence_threshold": 0.7}
        resp = client.post(
            "/api/v1/eng/runs",
            files=files,
            data=data,
            headers=auth_headers(),
        )

    assert resp.status_code == 201
    body = resp.json()
    assert "run_id" in body
    assert body["status"] in ("PROCESSING", "SUCCEEDED", "FAILED")
    assert body["model_name"] == "ISOSNet-healthy"
    assert isinstance(body["dip_columns"], list)
    assert isinstance(body["dip_count"], int)


def test_get_run_contract_validation(tmp_path):
    from PIL import Image

    img_path = tmp_path / "bscan2.png"
    img = Image.new("L", (32, 32), color=64)
    img.save(img_path)

    with img_path.open("rb") as f:
        files = {"bscan_image": ("bscan2.png", f, "image/png")}
        data = {"model_name": "ISOSNet-healthy"}
        create_resp = client.post(
            "/api/v1/eng/runs",
            files=files,
            data=data,
            headers=auth_headers(),
        )
    assert create_resp.status_code == 201
    run_id = create_resp.json()["run_id"]

    get_resp = client.get(
        f"/api/v1/eng/runs/{run_id}",
        headers=auth_headers(),
    )
    assert get_resp.status_code == 200
    body = get_resp.json()
    assert body["run_id"] == run_id
    assert "overlay_image_uri" in body
    assert "metrics_csv_uri" in body
    assert "metrics_json_uri" in body

