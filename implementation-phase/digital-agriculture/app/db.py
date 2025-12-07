import hashlib
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple
import uuid

DB_PATH = os.getenv("EDGE_DB_PATH", "edge_transfer.db")

_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
_conn.row_factory = sqlite3.Row


def get_connection():
    return _conn


def init_db(conn=None):
    conn = conn or _conn
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS missions (
            id TEXT PRIMARY KEY,
            root_path TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_id TEXT NOT NULL,
            path TEXT NOT NULL,
            size INTEGER NOT NULL,
            hash TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL,
            FOREIGN KEY(mission_id) REFERENCES missions(id)
        );
        CREATE TABLE IF NOT EXISTS batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY(mission_id) REFERENCES missions(id)
        );
        CREATE TABLE IF NOT EXISTS batch_files (
            batch_id INTEGER NOT NULL,
            file_id INTEGER NOT NULL,
            PRIMARY KEY(batch_id, file_id),
            FOREIGN KEY(batch_id) REFERENCES batches(id),
            FOREIGN KEY(file_id) REFERENCES files(id)
        );
        CREATE TABLE IF NOT EXISTS upload_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER NOT NULL,
            session_key TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL,
            retry_count INTEGER NOT NULL DEFAULT 0,
            last_error TEXT,
            remote_path TEXT,
            FOREIGN KEY(batch_id) REFERENCES batches(id)
        );
        """
    )
    conn.commit()


def get_or_create_mission(conn, mission_id: str, root_path: str) -> str:
    cur = conn.cursor()
    cur.execute("SELECT id, root_path FROM missions WHERE id=?", (mission_id,))
    row = cur.fetchone()
    if row:
        return row["id"]
    cur.execute(
        "INSERT INTO missions(id, root_path) VALUES(?, ?)", (mission_id, root_path)
    )
    conn.commit()
    return mission_id


def _hash_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_new_files(conn, mission_id: str, root_path: str) -> int:
    cur = conn.cursor()
    new_count = 0
    for dirpath, _dirnames, filenames in os.walk(root_path):
        for name in filenames:
            full_path = os.path.join(dirpath, name)
            try:
                size = os.path.getsize(full_path)
            except OSError:
                continue
            file_hash = _hash_file(full_path)
            cur.execute("SELECT id FROM files WHERE hash=?", (file_hash,))
            if cur.fetchone():
                continue
            cur.execute(
                "INSERT INTO files(mission_id, path, size, hash, status) "
                "VALUES(?,?,?,?,?)",
                (mission_id, full_path, size, file_hash, "NEW"),
            )
            new_count += 1
    conn.commit()
    return new_count


def create_batches(
    conn, mission_id: str, max_files: int, max_bytes: int
) -> List[Dict]:
    cur = conn.cursor()
    cur.execute(
        "SELECT id, size FROM files "
        "WHERE mission_id=? AND status='NEW' ORDER BY id ASC",
        (mission_id,),
    )
    rows = cur.fetchall()
    batches: List[Dict] = []
    current_files: List[int] = []
    current_bytes = 0

    def flush_batch():
        nonlocal current_files, current_bytes
        if not current_files:
            return
        created_at = datetime.utcnow().isoformat() + "Z"
        cur.execute(
            "INSERT INTO batches(mission_id, created_at, status) VALUES(?,?,?)",
            (mission_id, created_at, "PENDING"),
        )
        batch_id = cur.lastrowid
        for file_id in current_files:
            cur.execute(
                "INSERT INTO batch_files(batch_id, file_id) VALUES(?,?)",
                (batch_id, file_id),
            )
            cur.execute(
                "UPDATE files SET status='BATCHED' WHERE id=?", (file_id,)
            )
        cur.execute(
            "SELECT COUNT(*) as cnt, SUM(size) as total_bytes FROM files "
            "JOIN batch_files ON files.id = batch_files.file_id WHERE batch_id=?",
            (batch_id,),
        )
        stats = cur.fetchone()
        batches.append(
            {
                "batch_id": batch_id,
                "mission_id": mission_id,
                "file_count": stats["cnt"] or 0,
                "total_bytes": stats["total_bytes"] or 0,
                "status": "PENDING",
            }
        )
        current_files = []
        current_bytes = 0

    for row in rows:
        file_id = row["id"]
        size = row["size"]
        if current_files and (
            len(current_files) >= max_files or current_bytes + size > max_bytes
        ):
            flush_batch()
        current_files.append(file_id)
        current_bytes += size
    flush_batch()
    conn.commit()
    return batches


def get_batch(conn, batch_id: int) -> Dict:
    cur = conn.cursor()
    cur.execute(
        "SELECT id, mission_id, status FROM batches WHERE id=?",
        (batch_id,),
    )
    row = cur.fetchone()
    if not row:
        return None
    return dict(row)


def get_files_for_batch(conn, batch_id: int) -> List[Tuple[str, int]]:
    cur = conn.cursor()
    cur.execute(
        "SELECT files.path, files.size FROM files "
        "JOIN batch_files ON files.id = batch_files.file_id "
        "WHERE batch_files.batch_id=?",
        (batch_id,),
    )
    rows = cur.fetchall()
    return [(r["path"], r["size"]) for r in rows]


def get_or_create_upload_session(
    conn, batch_id: int, requested_key: str | None = None
) -> Dict:
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM upload_sessions WHERE batch_id=? "
        "ORDER BY id DESC LIMIT 1",
        (batch_id,),
    )
    row = cur.fetchone()
    if row and row["status"] == "COMPLETED":
        return dict(row)
    if row and not requested_key:
        return dict(row)
    session_key = requested_key or (row["session_key"] if row else str(uuid.uuid4()))
    if not row:
        cur.execute(
            "INSERT INTO upload_sessions(batch_id, session_key, status, retry_count) "
            "VALUES(?,?,?,0)",
            (batch_id, session_key, "PENDING"),
        )
        session_id = cur.lastrowid
        cur.execute(
            "SELECT * FROM upload_sessions WHERE id=?",
            (session_id,),
        )
        row = cur.fetchone()
    conn.commit()
    return dict(row)


def mark_session_success(conn, session_key: str, remote_path: str) -> None:
    cur = conn.cursor()
    cur.execute(
        "UPDATE upload_sessions SET status='COMPLETED', remote_path=? "
        "WHERE session_key=?",
        (remote_path, session_key),
    )
    cur.execute(
        "UPDATE batches SET status='UPLOADED' WHERE id = ("
        "SELECT batch_id FROM upload_sessions WHERE session_key=?"
        ")",
        (session_key,),
    )
    cur.execute(
        "UPDATE files SET status='UPLOADED' WHERE id IN ("
        "SELECT file_id FROM batch_files WHERE batch_id = ("
        "SELECT batch_id FROM upload_sessions WHERE session_key=?"
        "))",
        (session_key,),
    )
    conn.commit()


def mark_session_failure(conn, session_key: str, error: str) -> None:
    cur = conn.cursor()
    cur.execute(
        "UPDATE upload_sessions "
        "SET status='FAILED', retry_count=retry_count+1, last_error=? "
        "WHERE session_key=?",
        (error, session_key),
    )
    conn.commit()


def get_session_by_key(conn, session_key: str) -> Dict | None:
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM upload_sessions WHERE session_key=?", (session_key,)
    )
    row = cur.fetchone()
    return dict(row) if row else None
