# AO-OCT Analytics Engine (ENG) Slice

Minimal AO-OCT Analytics Engine implementation for single B-scan analysis.

This slice:

- Ingests a single AO-OCT B-scan image.
- Runs deterministic segmentation-style analysis with a selected model name.
- Computes per-column confidence and uncertainty curves and flags dips.
- Stores run metadata in SQLite and artifacts on disk.

It corresponds to the `Analytics Engine (ENG)` container, with embedded API,
`Metadata DB (SQLite)`, and `Object Storage` responsibilities for this slice.

## Prerequisites

- Python 3.11+
- `pip`
- Optional: Docker

## Local run

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export API_TOKEN=secret-token
export ENG_DB_PATH=data/aooct_eng.db
export ENG_STORAGE_DIR=data/eng_storage

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health:

```bash
curl http://localhost:8000/health
```

Create a B-scan run:

```bash
curl -X POST "http://localhost:8000/api/v1/eng/runs" \
  -H "Authorization: Bearer secret-token" \
  -H "Idempotency-Key: demo-run-1" \
  -F "model_name=ISOSNet-healthy" \
  -F "confidence_threshold=0.7" \
  -F "bscan_image=@/path/to/bscan.png;type=image/png"
```

Fetch a run:

```bash
curl "http://localhost:8000/api/v1/eng/runs/<RUN_ID>" \
  -H "Authorization: Bearer secret-token"
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

