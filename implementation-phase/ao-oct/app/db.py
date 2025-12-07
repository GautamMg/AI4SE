import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

DB_PATH = os.getenv("ENG_DB_PATH", "aooct_eng.db")

_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
_conn.row_factory = sqlite3.Row


def get_connection() -> sqlite3.Connection:
    return _conn


def init_db(conn: Optional[sqlite3.Connection] = None) -> None:
    conn = conn or _conn
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS eng_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL UNIQUE,
            idempotency_key TEXT,
            status TEXT NOT NULL,
            model_name TEXT NOT NULL,
            model_version TEXT,
            confidence_threshold REAL NOT NULL,
            input_image_path TEXT NOT NULL,
            overlay_image_uri TEXT,
            metrics_csv_uri TEXT,
            metrics_json_uri TEXT,
            manifest_uri TEXT,
            dip_columns_json TEXT,
            dip_count INTEGER NOT NULL DEFAULT 0,
            actor TEXT,
            error_message TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_eng_runs_idempotency
            ON eng_runs(idempotency_key);
        """
    )
    conn.commit()


def _now() -> str:
    return datetime.utcnow().isoformat(timespec="milliseconds") + "Z"


def create_run(
    conn: sqlite3.Connection,
    run_id: str,
    model_name: str,
    model_version: Optional[str],
    confidence_threshold: float,
    idempotency_key: Optional[str],
    input_image_path: str,
    actor: str,
) -> Dict:
    cur = conn.cursor()
    now = _now()
    cur.execute(
        """
        INSERT INTO eng_runs(
            run_id, idempotency_key, status,
            model_name, model_version,
            confidence_threshold,
            input_image_path,
            overlay_image_uri, metrics_csv_uri, metrics_json_uri, manifest_uri,
            dip_columns_json, dip_count,
            actor, error_message,
            created_at, updated_at
        )
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            run_id,
            idempotency_key,
            "PROCESSING",
            model_name,
            model_version,
            confidence_threshold,
            input_image_path,
            None,
            None,
            None,
            None,
            json.dumps([]),
            0,
            actor,
            None,
            now,
            now,
        ),
    )
    conn.commit()
    return get_run_by_run_id(conn, run_id)


def update_run_success(
    conn: sqlite3.Connection,
    run_id: str,
    overlay_image_uri: str,
    metrics_csv_uri: str,
    metrics_json_uri: str,
    manifest_uri: str,
    dip_columns: List[int],
) -> None:
    cur = conn.cursor()
    now = _now()
    dip_columns_json = json.dumps(dip_columns)
    cur.execute(
        """
        UPDATE eng_runs
        SET status='SUCCEEDED',
            overlay_image_uri=?,
            metrics_csv_uri=?,
            metrics_json_uri=?,
            manifest_uri=?,
            dip_columns_json=?,
            dip_count=?,
            updated_at=?
        WHERE run_id=?
        """,
        (
            overlay_image_uri,
            metrics_csv_uri,
            metrics_json_uri,
            manifest_uri,
            dip_columns_json,
            len(dip_columns),
            now,
            run_id,
        ),
    )
    conn.commit()


def update_run_failure(
    conn: sqlite3.Connection,
    run_id: str,
    error_message: str,
) -> None:
    cur = conn.cursor()
    now = _now()
    cur.execute(
        """
        UPDATE eng_runs
        SET status='FAILED',
            error_message=?,
            updated_at=?
        WHERE run_id=?
        """,
        (error_message, now, run_id),
    )
    conn.commit()


def _row_to_response_dict(row: sqlite3.Row) -> Dict:
    data = dict(row)
    dip_columns_raw = data.get("dip_columns_json") or "[]"
    try:
        dip_columns = json.loads(dip_columns_raw)
    except json.JSONDecodeError:
        dip_columns = []
    return {
        "run_id": data["run_id"],
        "status": data["status"],
        "model_name": data["model_name"],
        "model_version": data.get("model_version"),
        "confidence_threshold": float(data["confidence_threshold"]),
        "created_at": data["created_at"],
        "updated_at": data["updated_at"],
        "overlay_image_uri": data.get("overlay_image_uri"),
        "metrics_csv_uri": data.get("metrics_csv_uri"),
        "metrics_json_uri": data.get("metrics_json_uri"),
        "manifest_uri": data.get("manifest_uri"),
        "dip_columns": dip_columns,
        "dip_count": int(data.get("dip_count") or len(dip_columns)),
    }


def get_run_by_run_id(conn: sqlite3.Connection, run_id: str) -> Optional[Dict]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM eng_runs WHERE run_id=?", (run_id,))
    row = cur.fetchone()
    if not row:
        return None
    return _row_to_response_dict(row)


def get_run_by_idempotency_key(
    conn: sqlite3.Connection,
    idempotency_key: str,
) -> Optional[Dict]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM eng_runs WHERE idempotency_key=?", (idempotency_key,))
    row = cur.fetchone()
    if not row:
        return None
    return _row_to_response_dict(row)


def count_runs(conn: sqlite3.Connection) -> int:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS cnt FROM eng_runs")
    row = cur.fetchone()
    return int(row["cnt"] if row else 0)

