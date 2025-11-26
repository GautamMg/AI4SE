import io
import logging
import os
import uuid

import numpy as np
from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    Header,
    HTTPException,
    UploadFile,
    status,
)
from PIL import Image

from . import db
from .eng_service import EngRunArtifacts, process_bscan
from .schemas import EngRunResponse, HealthResponse
from .security import auth_bearer

logger = logging.getLogger("aooct_eng_service")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(5 * 1024 * 1024)))
ENG_STORAGE_DIR = os.getenv("ENG_STORAGE_DIR", "./eng_storage")
os.makedirs(ENG_STORAGE_DIR, exist_ok=True)

seed = int(os.getenv("RANDOM_SEED", "1234"))
np.random.seed(seed)

_CONN = db.get_connection()
db.init_db(_CONN)

app = FastAPI(title="AO-OCT Analytics Engine API", version="1.0.0")


@app.get("/health", response_model=HealthResponse, tags=["ops"])
def health() -> HealthResponse:
    return HealthResponse(status="ok")


def _save_image_bytes(run_id: str, filename: str, data: bytes) -> str:
    run_dir = os.path.join(ENG_STORAGE_DIR, "runs", run_id)
    os.makedirs(run_dir, exist_ok=True)
    name = filename or "bscan.png"
    path = os.path.join(run_dir, name)
    with open(path, "wb") as f:
        f.write(data)
    return path


@app.post(
    "/api/v1/eng/runs",
    response_model=EngRunResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Analytics Engine"],
)
async def create_eng_run(
    model_name: str = Form(...),
    model_version: str | None = Form(None),
    confidence_threshold: float = Form(0.7),
    bscan_image: UploadFile = File(...),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    caller=Depends(auth_bearer),
) -> EngRunResponse:
    data = await bscan_image.read()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty image upload",
        )
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Uploaded image too large",
        )

    try:
        Image.open(io.BytesIO(data)).verify()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is not a valid image",
        ) from exc

    conn = _CONN

    if idempotency_key:
        existing = db.get_run_by_idempotency_key(conn, idempotency_key)
        if existing:
            logger.info(
                "audit: eng_run idempotent-hit idem_key=%s run_id=%s caller=%s",
                idempotency_key,
                existing["run_id"],
                caller["caller"],
            )
            return EngRunResponse(**existing)

    run_id = uuid.uuid4().hex
    input_path = _save_image_bytes(run_id, bscan_image.filename or "bscan.png", data)

    logger.info(
        "audit: eng_run start run_id=%s model=%s version=%s caller=%s",
        run_id,
        model_name,
        model_version,
        caller["caller"],
    )

    db.create_run(
        conn=conn,
        run_id=run_id,
        model_name=model_name,
        model_version=model_version,
        confidence_threshold=confidence_threshold,
        idempotency_key=idempotency_key,
        input_image_path=input_path,
        actor=caller["caller"],
    )

    try:
        artifacts: EngRunArtifacts = process_bscan(
            run_id=run_id,
            input_image_path=input_path,
            output_dir=os.path.join(ENG_STORAGE_DIR, "runs", run_id),
            model_name=model_name,
            model_version=model_version,
            confidence_threshold=confidence_threshold,
        )
        db.update_run_success(
            conn=conn,
            run_id=run_id,
            overlay_image_uri=artifacts.overlay_image_uri,
            metrics_csv_uri=artifacts.metrics_csv_uri,
            metrics_json_uri=artifacts.metrics_json_uri,
            manifest_uri=artifacts.manifest_uri,
            dip_columns=artifacts.dip_columns,
        )
        run_dict = db.get_run_by_run_id(conn, run_id)
        logger.info(
            "audit: eng_run success run_id=%s dips=%d caller=%s",
            run_id,
            len(artifacts.dip_columns),
            caller["caller"],
        )
        return EngRunResponse(**run_dict)
    except Exception as exc:  # noqa: BLE001
        db.update_run_failure(conn, run_id, str(exc))
        logger.exception("audit: eng_run failure run_id=%s error=%s", run_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Processing failed",
        ) from exc


@app.get(
    "/api/v1/eng/runs/{run_id}",
    response_model=EngRunResponse,
    tags=["Analytics Engine"],
)
def get_eng_run(
    run_id: str,
    caller=Depends(auth_bearer),
) -> EngRunResponse:
    conn = _CONN
    run_dict = db.get_run_by_run_id(conn, run_id)
    if not run_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    logger.info(
        "audit: eng_run get run_id=%s caller=%s status=%s",
        run_id,
        caller["caller"],
        run_dict["status"],
    )
    return EngRunResponse(**run_dict)

