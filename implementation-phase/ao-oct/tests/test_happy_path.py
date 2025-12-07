from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

API_TOKEN = "secret-token"


def auth_headers():
    return {"Authorization": f"Bearer {API_TOKEN}"}


def test_happy_path_create_and_fetch_run(tmp_path):
    from PIL import Image

    img_path = tmp_path / "happy.png"
    img = Image.new("L", (128, 64), color=180)
    img.save(img_path)

    with img_path.open("rb") as f:
        files = {"bscan_image": ("happy.png", f, "image/png")}
        data = {
            "model_name": "ISOSNet-healthy",
            "model_version": "1.0.0",
            "confidence_threshold": 0.6,
        }
        create_resp = client.post(
            "/api/v1/eng/runs",
            files=files,
            data=data,
            headers=auth_headers(),
        )

    assert create_resp.status_code == 201
    created = create_resp.json()
    run_id = created["run_id"]
    assert created["status"] == "SUCCEEDED"
    assert created["model_name"] == "ISOSNet-healthy"
    assert isinstance(created["dip_columns"], list)
    assert isinstance(created["dip_count"], int)

    get_resp = client.get(
        f"/api/v1/eng/runs/{run_id}",
        headers=auth_headers(),
    )
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["run_id"] == run_id
    assert fetched["overlay_image_uri"]
    assert fetched["metrics_csv_uri"]
    assert fetched["metrics_json_uri"]
    assert fetched["dip_count"] == created["dip_count"]

