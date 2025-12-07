import logging
import os
from typing import Dict

from fastapi import Depends, FastAPI, HTTPException, status

from . import db
from .schemas import (
    BatchInfo,
    HealthResponse,
    ScanAndBatchRequest,
    ScanAndBatchResponse,
    UploadBatchRequest,
    UploadBatchResponse,
)
from .security import auth_bearer
from .tapis_client import TapisClientStub

logger = logging.getLogger("edge_transfer_service")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

app = FastAPI(title="Edge TransferModule API", version="1.0.0")

_CONN = db.get_connection()
db.init_db(_CONN)
_TAPIS = TapisClientStub(base_dir=os.getenv("HPC_STORAGE_DIR", "./hpc_storage"))
_TAPIS.ensure_base_dir()

METRICS: Dict[str, int] = {
    "batches_created": 0,
    "batches_uploaded": 0,
    "upload_failures": 0,
}


@app.get("/health", response_model=HealthResponse, tags=["ops"])
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/metrics", tags=["ops"])
def metrics() -> Dict[str, int]:
    return METRICS


@app.post(
    "/api/v1/missions/{mission_id}/scan-and-batch",
    response_model=ScanAndBatchResponse,
    tags=["transfer"],
)
def scan_and_batch(
    mission_id: str,
    payload: ScanAndBatchRequest,
    caller=Depends(auth_bearer),
) -> ScanAndBatchResponse:
    root_path = payload.root_path
    if not os.path.isdir(root_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="root_path must be an existing directory",
        )

    logger.info(
        "audit: scan_and_batch start mission=%s root=%s caller=%s",
        mission_id,
        root_path,
        caller["caller"],
    )

    conn = _CONN
    db.get_or_create_mission(conn, mission_id, root_path)
    db.scan_new_files(conn, mission_id, root_path)
    batch_rows = db.create_batches(
        conn,
        mission_id,
        payload.max_files_per_batch,
        payload.max_batch_bytes,
    )
    METRICS["batches_created"] += len(batch_rows)

    batches = [
        BatchInfo(
            batch_id=row["batch_id"],
            mission_id=row["mission_id"],
            file_count=row["file_count"],
            total_bytes=row["total_bytes"],
            status=row["status"],
        )
        for row in batch_rows
    ]

    logger.info(
        "audit: scan_and_batch complete mission=%s created_batches=%d",
        mission_id,
        len(batches),
    )

    return ScanAndBatchResponse(mission_id=mission_id, batches=batches)


@app.post(
    "/api/v1/batches/{batch_id}/upload",
    response_model=UploadBatchResponse,
    tags=["transfer"],
)
def upload_batch(
    batch_id: int,
    payload: UploadBatchRequest,
    caller=Depends(auth_bearer),
) -> UploadBatchResponse:
    conn = _CONN
    batch = db.get_batch(conn, batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found",
        )

    session = db.get_or_create_upload_session(conn, batch_id, payload.session_key)
    session_key = session["session_key"]

    # If already completed, be idempotent and do nothing.
    if session["status"] == "COMPLETED":
        logger.info(
            "audit: upload_batch idempotent hit batch_id=%s session_key=%s caller=%s",
            batch_id,
            session_key,
            caller["caller"],
        )
        return UploadBatchResponse(
            batch_id=batch_id,
            session_key=session_key,
            status="COMPLETED",
            remote_path=session.get("remote_path"),
            retry_count=session.get("retry_count", 0),
        )

    files = db.get_files_for_batch(conn, batch_id)
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files associated with this batch",
        )

    logger.info(
        "audit: upload_batch start batch_id=%s session_key=%s file_count=%d caller=%s",
        batch_id,
        session_key,
        len(files),
        caller["caller"],
    )

    try:
        remote_path = _TAPIS.upload_batch(session_key, files)
        db.mark_session_success(conn, session_key, remote_path)
        METRICS["batches_uploaded"] += 1
        logger.info(
            "audit: upload_batch success batch_id=%s session_key=%s remote_path=%s",
            batch_id,
            session_key,
            remote_path,
        )
        session = db.get_session_by_key(conn, session_key)
        return UploadBatchResponse(
            batch_id=batch_id,
            session_key=session_key,
            status=session["status"],
            remote_path=session["remote_path"],
            retry_count=session["retry_count"],
        )
    except Exception as exc:  # noqa: BLE001
        METRICS["upload_failures"] += 1
        db.mark_session_failure(conn, session_key, str(exc))
        logger.error(
            "audit: upload_batch failure batch_id=%s session_key=%s error=%s",
            batch_id,
            session_key,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Upload failed",
        ) from exc
