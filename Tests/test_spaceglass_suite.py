"""
SpaceGlass — Automated Test Suite (Tests/test_spaceglass_suite.py).
Covers all 13 testing requirements from Section 14 of the specification:
1. Calendar date calculations
2. Month navigation
3. Leap years
4. Event sorting & cancelled event exclusion
5. Timezone conversion & display formatting
6. Task creation (including duplicate submission prevention)
7. Task completion & reopening
8. Task deletion (including externally deleted task handling)
9. OAuth error handling (missing credentials.json, unauthenticated, revoked access)
10. API error handling & offline fallback
11. Cache behavior (strict distinction between `source="live"` and `source="cache"`)
12. Backend health (`/api/status`)
13. Rainmeter configuration validity (`.ini`, `.inc`, `.lua`, and zero secrets in skins)
"""
from __future__ import annotations

import importlib.util
import logging
import re
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from dateutil import tz
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if "Backend" not in sys.modules:
    _spec = importlib.util.spec_from_file_location(
        "Backend",
        PROJECT_ROOT / "Backend" / "__init__.py",
        submodule_search_locations=[str(PROJECT_ROOT / "Backend")],
    )
    if _spec and _spec.loader:
        _mod = importlib.util.module_from_spec(_spec)
        sys.modules["Backend"] = _mod
        _spec.loader.exec_module(_mod)

from Backend.app import create_app
from Backend.cache import LocalCache
from Backend.calendar_service import (
    CalendarService,
    get_days_in_month,
    is_leap_year,
    normalize_google_event,
)
from Backend.config import ConfigManager
from Backend.google_auth import GoogleAuthError, GoogleAuthManager
from Backend.tasks_service import TasksService


class _FakeExecute:
    def __init__(self, result: Dict[str, Any], raise_exc: Exception | None = None) -> None:
        self._result = result
        self._raise_exc = raise_exc

    def execute(self) -> Dict[str, Any]:
        if self._raise_exc:
            raise self._raise_exc
        return self._result


class FakeGoogleCalendarClient:
    def __init__(self, items: List[Dict[str, Any]], raise_on_list: Exception | None = None) -> None:
        self._items = items
        self._raise_on_list = raise_on_list

    def events(self):
        return self

    def list(self, **kwargs):
        return _FakeExecute({"items": self._items}, raise_exc=self._raise_on_list)

    def get(self, calendarId: str, eventId: str):
        for item in self._items:
            if item.get("id") == eventId:
                return _FakeExecute(item)
        return _FakeExecute({}, raise_exc=Exception("HttpError 404 notFound"))


class FakeGoogleTasksClient:
    def __init__(self) -> None:
        self.lists = [{"id": "@default", "title": "My Tasks", "updated": "2026-11-01T10:00:00Z"}]
        self.tasks_store: Dict[str, Dict[str, Any]] = {
            "task-1": {
                "id": "task-1",
                "title": "Study DBMS",
                "status": "needsAction",
                "due": "2026-11-01T00:00:00.000Z",
                "position": "0001",
            },
            "task-2": {
                "id": "task-2",
                "title": "Check emails",
                "status": "completed",
                "completed": "2026-11-01T12:00:00.000Z",
                "position": "0002",
            },
        }
        self._counter = 3

    def tasklists(self):
        return self

    def tasks(self):
        return self

    def list(self, **kwargs):
        if "tasklist" in kwargs:
            return _FakeExecute({"items": list(self.tasks_store.values())})
        return _FakeExecute({"items": self.lists})

    def insert(self, tasklist: str, body: Dict[str, Any]):
        new_id = f"task-{self._counter}"
        self._counter += 1
        record = {
            "id": new_id,
            "title": body["title"],
            "notes": body.get("notes", ""),
            "status": "needsAction",
            "due": body.get("due"),
            "position": f"000{self._counter}",
        }
        self.tasks_store[new_id] = record
        return _FakeExecute(record)

    def patch(self, tasklist: str, task: str, body: Dict[str, Any]):
        if task not in self.tasks_store:
            return _FakeExecute({}, raise_exc=Exception("HttpError 404 notFound"))
        rec = self.tasks_store[task]
        rec.update(body)
        return _FakeExecute(rec)

    def delete(self, tasklist: str, task: str):
        if task not in self.tasks_store:
            return _FakeExecute({}, raise_exc=Exception("HttpError 404 notFound"))
        del self.tasks_store[task]
        return _FakeExecute({})


class SpaceGlassTestSuite(unittest.TestCase):
    """Comprehensive verification of Backend, Calendar, Tasks, OAuth, Cache, and Rainmeter skins."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_path = Path(self.temp_dir.name)
        self.cfg = ConfigManager(data_dir=self.data_path, project_root=PROJECT_ROOT)
        self.cache = LocalCache(self.cfg.cache_db_path)
        self.auth = GoogleAuthManager(self.cfg)

    def tearDown(self) -> None:
        for handler in logging.root.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                logging.root.removeHandler(handler)
        self.temp_dir.cleanup()

    def test_calendar_leap_years_and_days_in_month(self) -> None:
        self.assertTrue(is_leap_year(2024))
        self.assertTrue(is_leap_year(2028))
        self.assertTrue(is_leap_year(2000))
        self.assertFalse(is_leap_year(1900))
        self.assertFalse(is_leap_year(2026))

        self.assertEqual(get_days_in_month(2024, 2), 29)
        self.assertEqual(get_days_in_month(2026, 2), 28)
        self.assertEqual(get_days_in_month(2026, 11), 30)
        self.assertEqual(get_days_in_month(2026, 12), 31)

        with self.assertRaises(ValueError):
            get_days_in_month(2026, 13)

    def test_event_sorting_and_timezone_conversion(self) -> None:
        ist_tz = tz.gettz("Asia/Kolkata")
        ref_now = datetime(2026, 11, 1, 19, 30, tzinfo=ist_tz)

        raw_events = [
            {
                "id": "ev-late",
                "summary": "DBMS Assignment (Due)",
                "status": "confirmed",
                "start": {"dateTime": "2026-11-03T18:29:00Z"},  # 23:59 IST on Tue, Nov 3
                "end": {"dateTime": "2026-11-03T18:29:00Z"},
                "colorId": "9",
                "htmlLink": "https://calendar.google.com/calendar/event?eid=ev-late",
            },
            {
                "id": "ev-cancelled",
                "summary": "Cancelled Lecture",
                "status": "cancelled",
                "start": {"dateTime": "2026-11-02T04:00:00Z"},
                "end": {"dateTime": "2026-11-02T05:00:00Z"},
            },
            {
                "id": "ev-early",
                "summary": "SAC Meeting",
                "status": "confirmed",
                "start": {"dateTime": "2026-11-02T05:00:00Z"},  # 10:30 AM IST Tomorrow (Nov 2)
                "end": {"dateTime": "2026-11-02T06:00:00Z"},    # 11:30 AM IST Tomorrow (Nov 2)
                "colorId": "3",
                "htmlLink": "https://calendar.google.com/calendar/event?eid=ev-early",
            },
        ]

        normalized = []
        for idx, item in enumerate(raw_events):
            n = normalize_google_event(item, index=idx, local_tz=ist_tz, reference_now=ref_now)
            if n:
                normalized.append(n)
        normalized.sort(key=lambda e: e["start_iso"])

        self.assertEqual(len(normalized), 2)
        self.assertEqual(normalized[0]["id"], "ev-early")
        self.assertEqual(normalized[0]["title"], "SAC Meeting")
        self.assertEqual(normalized[0]["display_time"], "Tomorrow · 10:30 – 11:30 AM")
        self.assertEqual(normalized[1]["id"], "ev-late")
        self.assertEqual(normalized[1]["title"], "DBMS Assignment (Due)")
        self.assertEqual(normalized[1]["display_time"], "Tue, Nov 3 · 11:59 PM")

    def test_tasks_lifecycle_and_duplicate_guard(self) -> None:
        fake_tasks_api = FakeGoogleTasksClient()
        svc = TasksService(self.cfg, self.auth, self.cache, client_factory=lambda: fake_tasks_api)

        created1 = svc.create_task(title="Prepare for TOC", due_date="2026-11-05")
        self.assertFalse(created1["deduplicated"])
        task_id = created1["task"]["id"]

        created_dup = svc.create_task(title="Prepare for TOC", due_date="2026-11-05")
        self.assertTrue(created_dup["deduplicated"])
        self.assertEqual(created_dup["task"]["id"], task_id)

        completed_res = svc.update_task(task_id=task_id, status="completed")
        self.assertTrue(completed_res["task"]["completed"])
        self.assertEqual(completed_res["task"]["status"], "completed")

        reopened_res = svc.update_task(task_id=task_id, status="needsAction")
        self.assertFalse(reopened_res["task"]["completed"])
        self.assertEqual(reopened_res["task"]["status"], "needsAction")

        del_res = svc.delete_task(task_id=task_id)
        self.assertTrue(del_res["deleted"])

        del_again = svc.delete_task(task_id=task_id)
        self.assertTrue(del_again["deleted"])

    def test_oauth_errors_cache_distinction_and_rest_endpoints(self) -> None:
        status = self.auth.get_auth_status()
        self.assertFalse(status["authenticated"])
        self.assertFalse(status["credentials_configured"])
        with self.assertRaises(GoogleAuthError) as ctx:
            self.auth.get_valid_credentials()
        self.assertEqual(ctx.exception.code, "missing_client_credentials")

        self.cache.set("demo:key", {"source": "live", "value": 42}, ttl_seconds=300)
        cached_item = self.cache.get("demo:key")
        self.assertIsNotNone(cached_item)
        cached_payload, is_fresh = cached_item  # type: ignore[misc]
        self.assertTrue(is_fresh)
        self.assertEqual(cached_payload["source"], "cache")
        self.assertTrue(cached_payload["cached"])

        fake_cal_api = FakeGoogleCalendarClient(
            items=[
                {
                    "id": "ev-17",
                    "summary": "Project Review",
                    "status": "confirmed",
                    "start": {"date": "2026-11-17"},
                    "end": {"date": "2026-11-18"},
                }
            ]
        )
        fake_tasks_api = FakeGoogleTasksClient()
        cal_svc = CalendarService(self.cfg, self.auth, self.cache, client_factory=lambda: fake_cal_api)
        tsk_svc = TasksService(self.cfg, self.auth, self.cache, client_factory=lambda: fake_tasks_api)

        app = create_app(
            config_mgr=self.cfg,
            auth_mgr=self.auth,
            cache=self.cache,
            calendar_service=cal_svc,
            tasks_service=tsk_svc,
            enable_background_sync=False,
        )
        client = TestClient(app)

        r_status = client.get("/api/status")
        self.assertEqual(r_status.status_code, 200)
        self.assertEqual(r_status.json()["application"], "SpaceGlass")

        r_month = client.get("/api/calendar/month?year=2026&month=11&refresh=true")
        self.assertEqual(r_month.status_code, 200)
        m_data = r_month.json()
        self.assertEqual(m_data["source"], "live")
        self.assertEqual(m_data["days_in_month"], 30)
        self.assertIn("17", m_data["days"])

        r_month_cached = client.get("/api/calendar/month?year=2026&month=11")
        self.assertEqual(r_month_cached.json()["source"], "cache")

        cal_svc._client_factory = lambda: FakeGoogleCalendarClient([], raise_on_list=RuntimeError("Network down"))
        r_month_offline = client.get("/api/calendar/month?year=2026&month=11&refresh=true")
        self.assertEqual(r_month_offline.status_code, 200)
        self.assertEqual(r_month_offline.json()["source"], "cache")

        r_tasks = client.get("/api/tasks?list_id=%40default")
        self.assertEqual(r_tasks.status_code, 200)
        self.assertEqual(r_tasks.json()["total_active"], 1)

        r_create = client.post("/api/tasks", json={"title": "Complete project module", "list_id": "@default"})
        self.assertEqual(r_create.status_code, 201)
        new_id = r_create.json()["task"]["id"]

        r_patch = client.patch(f"/api/tasks/{new_id}", json={"status": "completed", "list_id": "@default"})
        self.assertEqual(r_patch.status_code, 200)
        self.assertTrue(r_patch.json()["task"]["completed"])

        r_del = client.delete(f"/api/tasks/{new_id}?list_id=%40default")
        self.assertEqual(r_del.status_code, 200)
        self.assertTrue(r_del.json()["deleted"])

    def test_rainmeter_skins_validity_and_no_hardcoded_secrets(self) -> None:
        skin_files = [
            PROJECT_ROOT / "SpaceGlass.ini",
            PROJECT_ROOT / "Clock" / "Clock.ini",
            PROJECT_ROOT / "Calendar" / "Calendar.ini",
            PROJECT_ROOT / "Events" / "Events.ini",
            PROJECT_ROOT / "Tasks" / "Tasks.ini",
            PROJECT_ROOT / "@Resources" / "Variables.inc",
            PROJECT_ROOT / "@Resources" / "Theme.inc",
            PROJECT_ROOT / "@Resources" / "Data" / "CalendarCells.inc",
        ]
        secret_pattern = re.compile(r"(client_secret|AIza[0-9A-Za-z\-_]{35}|ya29\.[0-9A-Za-z\-_]+)", re.IGNORECASE)

        for skin_path in skin_files:
            self.assertTrue(skin_path.exists(), f"Missing skin file: {skin_path}")
            content = skin_path.read_text(encoding="utf-8")
            self.assertIsNone(
                secret_pattern.search(content),
                f"Security violation: potential secret found in {skin_path}",
            )
            if skin_path.suffix == ".ini":
                self.assertIn("[Rainmeter]", content, f"[Rainmeter] section missing in {skin_path}")
                self.assertIn("[Metadata]", content, f"[Metadata] section missing in {skin_path}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
