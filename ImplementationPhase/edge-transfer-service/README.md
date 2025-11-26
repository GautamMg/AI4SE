# Edge TransferModule Service

Minimal FastAPI implementation of the **TransferModule** for batch uploads from an edge device to an HPC system (simulated Tapis client).

## Prerequisites

- Python 3.11+
- pip
- (optional) Docker

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run locally

```bash
export API_TOKEN=secret-token
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

## Sample flow

1. Create a mission folder and add images:

```bash
mkdir -p /tmp/mission1
echo "img" > /tmp/mission1/img1.jpg
echo "img" > /tmp/mission1/img2.jpg
```

2. Scan and create batches:

```bash
curl -X POST "http://localhost:8000/api/v1/missions/m1/scan-and-batch" \
  -H "Authorization: Bearer secret-token" \
  -H "Content-Type: application/json" \
  -d '{"root_path": "/tmp/mission1", "max_files_per_batch": 10, "max_batch_bytes": 1048576}'
```

3. Upload a batch (replace `<batch_id>` with the id from previous response):

```bash
curl -X POST "http://localhost:8000/api/v1/batches/<batch_id>/upload" \
  -H "Authorization: Bearer secret-token" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Tests

```bash
pytest -q
```

## Docker

Build:

```bash
docker build -t edge-transfer-service .
```

Run:

```bash
docker run --rm -p 8000:8000 edge-transfer-service
```
