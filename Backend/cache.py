"""
SpaceGlass — SQLite Local Cache Engine (Backend/cache.py).
Caches recently retrieved Calendar and Tasks payloads for offline resilience and
rate-limit protection while strictly distinguishing cached data (`source="cache"`)
from live synchronized data (`source="live"`).
"""
from __future__ import annotations

import contextlib
import json
import sqlite3
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Tuple


class LocalCache:
    """Thread-safe SQLite key-value cache with explicit timestamp and source metadata."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = self._resolve_usable_db_path(db_path)
        self._lock = threading.Lock()
        self._init_db()

    @staticmethod
    def _resolve_usable_db_path(preferred_path: Path) -> Path:
        """Ensure the SQLite database path supports file locking (falls back to temp dir on FUSE/network mounts)."""
        preferred_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            conn = sqlite3.connect(preferred_path)
            try:
                conn.execute("PRAGMA journal_mode=MEMORY;")
                conn.execute("CREATE TABLE IF NOT EXISTS _probe (id INT);")
            finally:
                conn.close()
            return preferred_path
        except sqlite3.OperationalError:
            fallback = Path(tempfile.gettempdir()) / "spaceglass_cache" / preferred_path.name
            fallback.parent.mkdir(parents=True, exist_ok=True)
            return fallback

    @contextlib.contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=MEMORY;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache_entries (
                    cache_key TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL,
                    stored_at REAL NOT NULL,
                    ttl_seconds INTEGER NOT NULL,
                    synced_iso TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sync_metadata (
                    meta_key TEXT PRIMARY KEY,
                    meta_value TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def set(self, key: str, payload: Dict[str, Any], ttl_seconds: int = 300) -> str:
        """Store a live response payload and record its exact synchronization timestamp."""
        now_ts = time.time()
        synced_iso = datetime.now(timezone.utc).isoformat()
        stored_copy = dict(payload)
        stored_copy["last_synced"] = synced_iso

        serialized = json.dumps(stored_copy)
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO cache_entries (cache_key, payload_json, stored_at, ttl_seconds, synced_iso)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    payload_json = excluded.payload_json,
                    stored_at = excluded.stored_at,
                    ttl_seconds = excluded.ttl_seconds,
                    synced_iso = excluded.synced_iso
                """,
                (key, serialized, now_ts, ttl_seconds, synced_iso),
            )
            conn.execute(
                """
                INSERT INTO sync_metadata (meta_key, meta_value)
                VALUES ('last_sync_iso', ?)
                ON CONFLICT(meta_key) DO UPDATE SET meta_value = excluded.meta_value
                """,
                (synced_iso,),
            )
            conn.commit()
        return synced_iso

    def get(self, key: str, allow_expired: bool = True) -> Optional[Tuple[Dict[str, Any], bool]]:
        """
        Retrieve cached entry.
        Returns (payload_with_source_cache, is_fresh) or None if key does not exist.
        Note: Cached payloads ALWAYS carry `source="cache"` and `cached=True` so cached
        data is never misrepresented as a fresh live API call.
        """
        now_ts = time.time()
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT payload_json, stored_at, ttl_seconds, synced_iso FROM cache_entries WHERE cache_key = ?",
                (key,),
            ).fetchone()

        if not row:
            return None

        payload_json, stored_at, ttl_seconds, synced_iso = row
        age_seconds = max(0.0, now_ts - float(stored_at))
        is_fresh = age_seconds <= float(ttl_seconds)

        if not is_fresh and not allow_expired:
            return None

        data = json.loads(payload_json)
        data["source"] = "cache"
        data["cached"] = True
        data["cache_age_seconds"] = round(age_seconds, 1)
        data["last_synced"] = synced_iso
        return data, is_fresh

    def invalidate_prefix(self, prefix: str) -> int:
        """Invalidate all cache entries matching a key prefix (e.g., 'tasks:' after task mutation)."""
        with self._lock, self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM cache_entries WHERE cache_key LIKE ?",
                (f"{prefix}%",),
            )
            conn.commit()
            return cur.rowcount

    def clear_all(self) -> None:
        """Clear all cached items (used on Google account disconnect)."""
        with self._lock, self._connect() as conn:
            conn.execute("DELETE FROM cache_entries")
            conn.execute("DELETE FROM sync_metadata")
            conn.commit()

    def get_last_sync_time(self) -> Optional[str]:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT meta_value FROM sync_metadata WHERE meta_key = 'last_sync_iso'"
            ).fetchone()
        return row[0] if row else None
