"""SQLite database for download history."""
import os
import json
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime

DB_PATH = os.path.join(os.path.expanduser("~"), ".bilibili_downloader", "history.db")


def _get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS downloads (
            id TEXT PRIMARY KEY,
            bvid TEXT NOT NULL,
            title TEXT NOT NULL,
            cover TEXT,
            quality TEXT,
            save_path TEXT NOT NULL,
            filename TEXT NOT NULL,
            status TEXT NOT NULL,
            progress INTEGER DEFAULT 0,
            speed TEXT,
            error TEXT,
            created_at TEXT NOT NULL,
            completed_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def add_record(record: Dict[str, Any]):
    conn = _get_conn()
    conn.execute("""
        INSERT OR REPLACE INTO downloads
        (id, bvid, title, cover, quality, save_path, filename, status, progress, speed, error, created_at, completed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record["id"], record["bvid"], record["title"], record.get("cover", ""),
        record["quality"], record["save_path"], record["filename"],
        record["status"], record.get("progress", 0), record.get("speed", ""),
        record.get("error", ""), record["created_at"], record.get("completed_at", None)
    ))
    conn.commit()
    conn.close()


def update_status(task_id: str, status: str, progress: int = 0, speed: str = "", error: str = ""):
    conn = _get_conn()
    conn.execute("""
        UPDATE downloads SET status=?, progress=?, speed=?, error=?
        WHERE id=?
    """, (status, progress, speed, error, task_id))
    conn.commit()
    conn.close()


def complete_task(task_id: str):
    now = datetime.now().isoformat()
    conn = _get_conn()
    conn.execute("""
        UPDATE downloads SET status=?, progress=100, completed_at=?
        WHERE id=?
    """, ("completed", now, task_id))
    conn.commit()
    conn.close()


def delete_record(task_id: str):
    conn = _get_conn()
    conn.execute("DELETE FROM downloads WHERE id=?", (task_id,))
    conn.commit()
    conn.close()


def get_all_records() -> List[Dict[str, Any]]:
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM downloads ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_record(task_id: str) -> Optional[Dict[str, Any]]:
    conn = _get_conn()
    row = conn.execute("SELECT * FROM downloads WHERE id=?", (task_id,)).fetchone()
    conn.close()
    return dict(row) if row else None
