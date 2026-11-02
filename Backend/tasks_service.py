"""
SpaceGlass — Google Tasks API v1 Service (Backend/tasks_service.py).
Provides full two-way synchronization with Google Tasks:
1. Retrieve task lists (`GET /api/tasks/lists`)
2. Retrieve tasks for a list (`GET /api/tasks?list_id={id}`)
   - Separates overdue, today, upcoming active tasks, and completed tasks
3. Create a task (`POST /api/tasks`) with anti-duplicate submission protection
4. Complete / reopen / update a task (`PATCH /api/tasks/{task_id}`)
5. Delete a task (`DELETE /api/tasks/{task_id}`)
"""
from __future__ import annotations

import logging
import threading
import time
from datetime import date, datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import unquote

from dateutil import parser as date_parser

from Backend.cache import LocalCache
from Backend.config import ConfigManager
from Backend.google_auth import GoogleAuthError, GoogleAuthManager

logger = logging.getLogger("spaceglass.tasks")


def parse_task_due_info(
    due_iso: Optional[str],
    status: str,
    reference_today: Optional[date] = None,
) -> Tuple[Optional[str], str, bool, bool]:
    """
    Parse a Google Tasks RFC 3339 due timestamp into:
      (due_date_iso, human_due_label, is_overdue, is_due_today)
    """
    if not due_iso:
        return None, "", False, False
    try:
        parsed_dt = date_parser.isoparse(due_iso)
        due_d = parsed_dt.date()
        today_d = reference_today or date.today()
        is_completed = status == "completed"

        if due_d < today_d:
            return due_d.isoformat(), f"Overdue ({due_d.strftime('%b %d')})", not is_completed, False
        if due_d == today_d:
            return due_d.isoformat(), "Today", False, True
        if (due_d - today_d).days == 1:
            return due_d.isoformat(), "Tomorrow", False, False
        return due_d.isoformat(), f"{due_d.strftime('%b')} {due_d.day}", False, False
    except Exception:
        return None, "", False, False


def normalize_google_task(
    raw_task: Dict[str, Any],
    list_id: str,
    list_title: str = "My Tasks",
    reference_today: Optional[date] = None,
) -> Optional[Dict[str, Any]]:
    """Convert a Google Tasks API task resource into a normalized SpaceGlass task dict."""
    if raw_task.get("deleted"):
        return None
    title = (raw_task.get("title") or "").strip()
    if not title and raw_task.get("status") != "completed":
        return None

    status = raw_task.get("status", "needsAction")
    due_date_iso, due_label, is_overdue, is_due_today = parse_task_due_info(
        raw_task.get("due"),
        status=status,
        reference_today=reference_today,
    )

    return {
        "id": raw_task.get("id", ""),
        "list_id": list_id,
        "list_title": list_title,
        "title": title or "(Untitled task)",
        "notes": raw_task.get("notes") or "",
        "status": status,
        "completed": status == "completed",
        "due_iso": raw_task.get("due"),
        "due_date": due_date_iso,
        "due_label": due_label,
        "is_overdue": is_overdue,
        "is_due_today": is_due_today,
        "updated": raw_task.get("updated") or "",
        "position": raw_task.get("position") or "",
        "web_view_link": raw_task.get("webViewLink") or "https://tasks.google.com/",
    }


class TasksService:
    """Two-way Google Tasks v1 service with anti-duplicate creation guard and local caching."""

    def __init__(
        self,
        config_mgr: ConfigManager,
        auth_mgr: GoogleAuthManager,
        cache: LocalCache,
        client_factory: Optional[Callable[[], Any]] = None,
    ) -> None:
        self.config_mgr = config_mgr
        self.auth_mgr = auth_mgr
        self.cache = cache
        self._client_factory = client_factory
        self._dedup_lock = threading.Lock()
        self._recent_creations: Dict[str, Tuple[float, Dict[str, Any]]] = {}

    def _build_service(self) -> Any:
        if self._client_factory is not None:
            return self._client_factory()
        creds = self.auth_mgr.get_valid_credentials()
        from googleapiclient.discovery import build

        return build("tasks", "v1", credentials=creds, cache_discovery=False)

    def get_task_lists(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Retrieve all Google Task lists from the user's account."""
        cache_key = "tasks:lists"
        if not force_refresh:
            cached = self.cache.get(cache_key, allow_expired=False)
            if cached is not None:
                data, _ = cached
                return data

        try:
            service = self._build_service()
            items: List[Dict[str, Any]] = []
            page_token: Optional[str] = None
            while True:
                resp = service.tasklists().list(maxResults=100, pageToken=page_token).execute()
                for entry in resp.get("items", []):
                    items.append(
                        {
                            "id": entry.get("id", ""),
                            "title": entry.get("title", "My Tasks"),
                            "updated": entry.get("updated", ""),
                        }
                    )
                page_token = resp.get("nextPageToken")
                if not page_token:
                    break

            payload = {
                "authenticated": True,
                "source": "live",
                "cached": False,
                "lists": items,
                "count": len(items),
            }
            self.cache.set(cache_key, payload, ttl_seconds=self.config_mgr.settings.tasks_refresh_seconds)
            return payload

        except GoogleAuthError as auth_err:
            return {
                "authenticated": False,
                "source": "none",
                "cached": False,
                "error_code": auth_err.code,
                "error": auth_err.message,
                "lists": [],
                "count": 0,
            }
        except Exception as exc:
            stale = self.cache.get(cache_key, allow_expired=True)
            if stale is not None:
                stale_data, _ = stale
                stale_data["warning"] = f"Offline cached task lists ({type(exc).__name__})."
                return stale_data
            raise

    def get_tasks(
        self,
        list_id: Optional[str] = None,
        include_completed: bool = True,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """Retrieve and categorize tasks (overdue, today, active, completed) for a selected task list."""
        target_list_id = unquote(list_id or self.config_mgr.settings.selected_task_list_id or "@default").strip()
        cache_key = f"tasks:items:{target_list_id}:{int(include_completed)}"

        if not force_refresh:
            cached = self.cache.get(cache_key, allow_expired=False)
            if cached is not None:
                data, _ = cached
                return data

        try:
            lists_resp = self.get_task_lists(force_refresh=force_refresh)
            available_lists = lists_resp.get("lists", [])
            list_title = self.config_mgr.settings.selected_task_list_name or "My Tasks"
            for lst in available_lists:
                if lst["id"] == target_list_id or (target_list_id == "@default" and lst == available_lists[0]):
                    list_title = lst["title"]
                    break

            service = self._build_service()
            raw_tasks: List[Dict[str, Any]] = []
            page_token: Optional[str] = None

            while True:
                resp = (
                    service.tasks()
                    .list(
                        tasklist=target_list_id,
                        showCompleted=include_completed,
                        showHidden=include_completed,
                        maxResults=100,
                        pageToken=page_token,
                    )
                    .execute()
                )
                raw_tasks.extend(resp.get("items", []))
                page_token = resp.get("nextPageToken")
                if not page_token:
                    break

            active_tasks: List[Dict[str, Any]] = []
            overdue_tasks: List[Dict[str, Any]] = []
            today_tasks: List[Dict[str, Any]] = []
            completed_tasks: List[Dict[str, Any]] = []

            for item in raw_tasks:
                norm = normalize_google_task(item, list_id=target_list_id, list_title=list_title)
                if norm is None:
                    continue
                if norm["completed"]:
                    completed_tasks.append(norm)
                else:
                    active_tasks.append(norm)
                    if norm["is_overdue"]:
                        overdue_tasks.append(norm)
                    elif norm["is_due_today"]:
                        today_tasks.append(norm)

            # Sort active tasks: overdue first, then due today, then by position
            active_tasks.sort(
                key=lambda t: (
                    0 if t["is_overdue"] else (1 if t["is_due_today"] else 2),
                    t["due_date"] or "9999-12-31",
                    t["position"],
                )
            )

            payload = {
                "authenticated": True,
                "source": "live",
                "cached": False,
                "list_id": target_list_id,
                "list_title": list_title,
                "available_lists": available_lists,
                "active_tasks": active_tasks,
                "overdue_tasks": overdue_tasks,
                "today_tasks": today_tasks,
                "completed_tasks": completed_tasks if include_completed else [],
                "total_active": len(active_tasks),
                "total_completed": len(completed_tasks),
            }
            self.cache.set(cache_key, payload, ttl_seconds=self.config_mgr.settings.tasks_refresh_seconds)
            return payload

        except GoogleAuthError as auth_err:
            return {
                "authenticated": False,
                "source": "none",
                "cached": False,
                "error_code": auth_err.code,
                "error": auth_err.message,
                "list_id": target_list_id,
                "list_title": self.config_mgr.settings.selected_task_list_name,
                "available_lists": [],
                "active_tasks": [],
                "overdue_tasks": [],
                "today_tasks": [],
                "completed_tasks": [],
                "total_active": 0,
                "total_completed": 0,
            }
        except Exception as exc:
            logger.warning("Live tasks fetch failed (%s), checking offline cache.", exc)
            stale = self.cache.get(cache_key, allow_expired=True)
            if stale is not None:
                stale_data, _ = stale
                stale_data["warning"] = f"Showing offline cached tasks ({type(exc).__name__})."
                return stale_data
            raise

    def create_task(
        self,
        title: str,
        list_id: Optional[str] = None,
        notes: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new task in Google Tasks.
        Includes a 10-second idempotency window on (list_id, normalized_title, due_date)
        to prevent accidental duplicate task creation from rapid double-clicks.
        """
        clean_title = (title or "").strip()
        if not clean_title:
            raise ValueError("Task title must not be empty.")

        target_list_id = unquote(list_id or self.config_mgr.settings.selected_task_list_id or "@default").strip()
        dedup_key = f"{target_list_id}:{clean_title.lower()}:{due_date or ''}"

        now_ts = time.time()
        with self._dedup_lock:
            existing = self._recent_creations.get(dedup_key)
            if existing and (now_ts - existing[0]) < 10.0:
                dup_resp = dict(existing[1])
                dup_resp["deduplicated"] = True
                return dup_resp

        body: Dict[str, Any] = {"title": clean_title}
        if notes:
            body["notes"] = notes.strip()
        if due_date:
            # Google Tasks API expects RFC 3339 timestamp (e.g., YYYY-MM-DDT00:00:00.000Z)
            if "T" not in due_date:
                parsed_d = date.fromisoformat(due_date.strip())
                body["due"] = f"{parsed_d.isoformat()}T00:00:00.000Z"
            else:
                body["due"] = due_date.strip()

        service = self._build_service()
        created_raw = service.tasks().insert(tasklist=target_list_id, body=body).execute()
        normalized = normalize_google_task(created_raw, list_id=target_list_id)

        self.cache.invalidate_prefix("tasks:")
        result = {
            "authenticated": True,
            "source": "live",
            "deduplicated": False,
            "task": normalized,
        }
        with self._dedup_lock:
            self._recent_creations[dedup_key] = (time.time(), result)
        return result

    def update_task(
        self,
        task_id: str,
        list_id: Optional[str] = None,
        title: Optional[str] = None,
        notes: Optional[str] = None,
        status: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a task's completion state ('completed' or 'needsAction') or details via PATCH."""
        clean_task_id = unquote(task_id).strip()
        if not clean_task_id:
            raise ValueError("task_id must not be empty.")
        target_list_id = unquote(list_id or self.config_mgr.settings.selected_task_list_id or "@default").strip()

        patch_body: Dict[str, Any] = {}
        if title is not None:
            clean_title = title.strip()
            if not clean_title:
                raise ValueError("Updated task title cannot be empty.")
            patch_body["title"] = clean_title
        if notes is not None:
            patch_body["notes"] = notes
        if status is not None:
            if status not in ("completed", "needsAction"):
                raise ValueError("status must be 'completed' or 'needsAction'.")
            patch_body["status"] = status
            if status == "needsAction":
                patch_body["completed"] = None
            else:
                patch_body["completed"] = datetime.now(timezone.utc).isoformat()
        if due_date is not None:
            if due_date == "":
                patch_body["due"] = None
            elif "T" not in due_date:
                parsed_d = date.fromisoformat(due_date.strip())
                patch_body["due"] = f"{parsed_d.isoformat()}T00:00:00.000Z"
            else:
                patch_body["due"] = due_date.strip()

        service = self._build_service()
        try:
            updated_raw = (
                service.tasks()
                .patch(tasklist=target_list_id, task=clean_task_id, body=patch_body)
                .execute()
            )
        except Exception as exc:
            err_text = str(exc)
            if "404" in err_text or "notFound" in err_text:
                self.cache.invalidate_prefix("tasks:")
                raise LookupError(f"Task '{clean_task_id}' was deleted externally from Google Tasks.") from exc
            raise

        self.cache.invalidate_prefix("tasks:")
        return {
            "authenticated": True,
            "source": "live",
            "task": normalize_google_task(updated_raw, list_id=target_list_id),
        }

    def delete_task(self, task_id: str, list_id: Optional[str] = None) -> Dict[str, Any]:
        """Delete a task from Google Tasks and invalidate local task cache."""
        clean_task_id = unquote(task_id).strip()
        if not clean_task_id:
            raise ValueError("task_id must not be empty.")
        target_list_id = unquote(list_id or self.config_mgr.settings.selected_task_list_id or "@default").strip()

        service = self._build_service()
        try:
            service.tasks().delete(tasklist=target_list_id, task=clean_task_id).execute()
        except Exception as exc:
            err_text = str(exc)
            if "404" in err_text or "notFound" in err_text:
                self.cache.invalidate_prefix("tasks:")
                return {
                    "authenticated": True,
                    "deleted": True,
                    "task_id": clean_task_id,
                    "note": "Task was already deleted externally.",
                }
            raise

        self.cache.invalidate_prefix("tasks:")
        return {
            "authenticated": True,
            "deleted": True,
            "task_id": clean_task_id,
        }
