# ConfigAdminAPI Slice

Minimal implementation of the ConfigAdminAPI container for the
Edge-to-Cloud Wildlife Intrusion Response system. It supports:

- Creating versioned, signed config change sets (AOIs, species thresholds, model config).
- Fetching the latest config for edge nodes that missed a push.
- Basic health + metrics.

## Prerequisites

- Python 3.11+
- `pip`
- Optional: Docker

## Local run

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export API_TOKEN=dev-token
export DB_PATH=data/config.db
export CONFIG_SIGNING_SALT=dev-salt

uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Sample requests

Create a config change set:

```bash
curl -X POST http://localhost:8000/config/change-sets   -H "Authorization: Bearer dev-token"   -H "Content-Type: application/json"   -H "X-Actor-Id: scientist-1"   -H "X-Actor-Role: WildlifeScientist"   -d '{
    "aois": [{
      "id": "aoi-1",
      "name": "River Bend",
      "polygon_ref": "s3://bucket/aoi/river-bend.geojson",
      "altitude_m": 120,
      "overlap_percent": 60
    }],
    "species_thresholds": [{
      "aoi_id": "aoi-1",
      "species": "elephant",
      "min_confidence": 0.8
    }],
    "model_config": {
      "model_version_id": "detector-v1",
      "rollout_group": "edge-ring-1",
      "notes": "Initial deployment"
    }
  }'
```

Fetch the latest config:

```bash
curl http://localhost:8000/config/latest   -H "Authorization: Bearer dev-token"   -H "X-Actor-Id: edge-service-1"   -H "X-Actor-Role: EdgeCaptureScoring"
```

Health:

```bash
curl http://localhost:8000/health
```

## Tests

```bash
pytest -q
```

## Docker

```bash
make docker-build
make docker-run
# API on http://localhost:8000
```
