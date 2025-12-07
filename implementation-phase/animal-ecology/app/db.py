import sqlite3
from pathlib import Path
from typing import Optional, Tuple

from .config import get_settings


def get_connection() -> sqlite3.Connection:
    """Create a SQLite connection with row access by name."""
    settings = get_settings()
    db_path: Path = settings.db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the config_versions table if it does not exist."""
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS config_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_version TEXT UNIQUE NOT NULL,
                actor_id TEXT NOT NULL,
                actor_role TEXT NOT NULL,
                created_at TEXT NOT NULL,
                aois_json TEXT NOT NULL,
                species_thresholds_json TEXT NOT NULL,
                model_config_json TEXT NOT NULL,
                signature TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def insert_config_version(
    actor_id: str,
    actor_role: str,
    created_at: str,
    aois_json: str,
    species_json: str,
    model_json: str,
    signature: str,
) -> Tuple[str, int]:
    """
    Insert a new config version row.

    Returns (config_version, numeric_id).
    """
    conn = get_connection()
    try:
        cur = conn.execute("SELECT MAX(id) AS max_id FROM config_versions")
        row = cur.fetchone()
        next_id = (row["max_id"] or 0) + 1
        config_version = f"v{next_id}"
        conn.execute(
            """
            INSERT INTO config_versions (
                config_version,
                actor_id,
                actor_role,
                created_at,
                aois_json,
                species_thresholds_json,
                model_config_json,
                signature
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                config_version,
                actor_id,
                actor_role,
                created_at,
                aois_json,
                species_json,
                model_json,
                signature,
            ),
        )
        conn.commit()
        return config_version, next_id
    finally:
        conn.close()


def fetch_latest_config_row() -> Optional[sqlite3.Row]:
    """Return the most recent config row, or None if no configs exist."""
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT * FROM config_versions ORDER BY id DESC LIMIT 1"
        )
        return cur.fetchone()
    finally:
        conn.close()
