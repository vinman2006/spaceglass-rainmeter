"""
SpaceGlass — Localhost FastAPI Companion Backend (Backend/app.py).
Provides REST endpoints for Rainmeter skins and the SpaceGlass Settings UI:
  - GET    /api/status
  - GET    /api/calendar/month?year=2026&month=11
  - GET    /api/calendar/events
  - GET    /api/calendar/events/{event_id}
  - GET    /api/tasks/lists
  - GET    /api/tasks?list_id={id}
  - POST   /api/tasks
  - PATCH  /api/tasks/{task_id}
  - DELETE /api/tasks/{task_id}
  - POST   /api/google/connect
  - POST   /api/google/disconnect
  - POST   /api/sync
  - GET    /api/weather
  - GET    /api/settings
  - PUT    /api/settings
  - POST   /api/settings/reset

Security & Performance Guarantees:
  - Strictly binds to 127.0.0.1 (never exposed to the public internet).
  - Single-instance PID check prevents duplicate backend processes.
  - Background periodic sync refreshes Calendar (~5 min) and Tasks (~90 sec).
  - Never fabricates events, tasks, or weather in production mode.
"""
from __future__ import annotations

import asyncio
import contextlib
import importlib.util
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Ensure project root and Backend package are importable across all filesystems
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

from Backend.cache import LocalCache
from Backend.calendar_service import CalendarService
from Backend.config import ConfigManager, SpaceGlassSettings
from Backend.glass_effect import refresh_rainmeter_glass_windows
from Backend.google_auth import GoogleAuthError, GoogleAuthManager
from Backend.tasks_service import TasksService
from Backend.weather_service import WeatherService


class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    list_id: Optional[str] = "@default"
    notes: Optional[str] = None
    due_date: Optional[str] = None


class TaskUpdateRequest(BaseModel):
    list_id: Optional[str] = "@default"
    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    notes: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None


def create_app(
    config_mgr: Optional[ConfigManager] = None,
    auth_mgr: Optional[GoogleAuthManager] = None,
    cache: Optional[LocalCache] = None,
    calendar_service: Optional[CalendarService] = None,
    tasks_service: Optional[TasksService] = None,
    weather_service: Optional[WeatherService] = None,
    enable_background_sync: bool = True,
) -> FastAPI:
    """Create and wire the SpaceGlass FastAPI application (supports dependency injection for tests)."""
    cfg = config_mgr or ConfigManager()

    if not logging.root.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[
                logging.FileHandler(cfg.log_path, encoding="utf-8"),
                logging.StreamHandler(sys.stdout),
            ],
        )
    logger = logging.getLogger("spaceglass.app")

    local_cache = cache or LocalCache(cfg.cache_db_path)
    auth = auth_mgr or GoogleAuthManager(cfg)
    cal_svc = calendar_service or CalendarService(cfg, auth, local_cache)
    tsk_svc = tasks_service or TasksService(cfg, auth, local_cache)
    wth_svc = weather_service or WeatherService(cfg, local_cache)

    start_time = time.time()

    async def _periodic_sync_loop() -> None:
        """Background sync loop: refreshes tasks every ~90s and calendar every ~5m when authenticated."""
        last_cal_sync = 0.0
        last_task_sync = 0.0
        while True:
            try:
                now = time.time()
                status = auth.get_auth_status()
                if status.get("authenticated"):
                    if now - last_task_sync >= cfg.settings.tasks_refresh_seconds:
                        await asyncio.to_thread(
                            tsk_svc.get_tasks,
                            cfg.settings.selected_task_list_id,
                            cfg.settings.show_completed_tasks,
                            True,
                        )
                        last_task_sync = now
                    if now - last_cal_sync >= cfg.settings.calendar_refresh_seconds:
                        dt_now = datetime.now()
                        await asyncio.to_thread(cal_svc.get_month_data, dt_now.year, dt_now.month, True)
                        await asyncio.to_thread(cal_svc.get_upcoming_events, 5, True)
                        last_cal_sync = now
                await asyncio.to_thread(
                    refresh_rainmeter_glass_windows,
                    cfg.settings.blur_type,
                    cfg.settings.glass_alpha,
                )
            except Exception as exc:
                logger.debug("Background sync cycle note: %s", exc)
            await asyncio.sleep(30)

    @contextlib.asynccontextmanager
    async def lifespan(_app: FastAPI):
        bg_task = None
        if enable_background_sync:
            bg_task = asyncio.create_task(_periodic_sync_loop())
        try:
            yield
        finally:
            if bg_task:
                bg_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await bg_task

    app = FastAPI(
        title="SpaceGlass Companion Backend",
        description="Localhost-only REST API for SpaceGlass Windows 11 Desktop Widgets",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Reject non-localhost requests as an extra defense-in-depth layer
    @app.middleware("http")
    async def enforce_localhost_only(request: Request, call_next):
        client_host = request.client.host if request.client else "127.0.0.1"
        if client_host not in ("127.0.0.1", "::1", "localhost", "testclient"):
            return JSONResponse(
                status_code=403,
                content={"error": "Forbidden: SpaceGlass API is restricted to localhost only."},
            )
        return await call_next(request)

    @app.get("/")
    @app.get("/api/status")
    def get_status() -> Dict[str, Any]:
        auth_status = auth.get_auth_status()
        last_sync = local_cache.get_last_sync_time()
        return {
            "application": "SpaceGlass",
            "tagline": "Your Universe. Your Schedule.",
            "version": "1.0.0",
            "status": "running",
            "uptime_seconds": round(time.time() - start_time, 1),
            "google_authenticated": auth_status["authenticated"],
            "credentials_configured": auth_status["credentials_configured"],
            "auth_details": auth_status,
            "last_sync_time": last_sync,
            "api_connectivity": "ready" if auth_status["authenticated"] else "awaiting_google_auth",
        }

    @app.get("/api/calendar/month")
    def get_calendar_month(
        year: int = Query(..., ge=1970, le=2100),
        month: int = Query(..., ge=1, le=12),
        refresh: bool = Query(default=False),
    ) -> Dict[str, Any]:
        try:
            return cal_svc.get_month_data(year=year, month=month, force_refresh=refresh)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            logger.error("Error in /api/calendar/month: %s", exc)
            raise HTTPException(status_code=502, detail=f"Calendar API error: {type(exc).__name__}") from exc

    @app.get("/api/calendar/events")
    def get_upcoming_events(
        limit: int = Query(default=5, ge=1, le=20),
        refresh: bool = Query(default=False),
    ) -> Dict[str, Any]:
        try:
            return cal_svc.get_upcoming_events(limit=limit, force_refresh=refresh)
        except Exception as exc:
            logger.error("Error in /api/calendar/events: %s", exc)
            raise HTTPException(status_code=502, detail=f"Upcoming events error: {type(exc).__name__}") from exc

    @app.get("/api/calendar/events/{event_id:path}")
    def get_event_by_id(event_id: str) -> Dict[str, Any]:
        try:
            return cal_svc.get_event_details(event_id)
        except GoogleAuthError as exc:
            raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": exc.message}) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except Exception as exc:
            err_str = str(exc)
            if "404" in err_str or "notFound" in err_str:
                raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found.") from exc
            raise HTTPException(status_code=502, detail=f"Failed to fetch event details: {type(exc).__name__}") from exc

    @app.get("/api/tasks/lists")
    def get_task_lists(refresh: bool = Query(default=False)) -> Dict[str, Any]:
        try:
            return tsk_svc.get_task_lists(force_refresh=refresh)
        except Exception as exc:
            logger.error("Error in /api/tasks/lists: %s", exc)
            raise HTTPException(status_code=502, detail=f"Failed to load task lists: {type(exc).__name__}") from exc

    @app.get("/api/tasks")
    def get_tasks(
        list_id: str = Query(default="@default"),
        include_completed: bool = Query(default=True),
        refresh: bool = Query(default=False),
    ) -> Dict[str, Any]:
        try:
            return tsk_svc.get_tasks(
                list_id=list_id,
                include_completed=include_completed,
                force_refresh=refresh,
            )
        except Exception as exc:
            logger.error("Error in /api/tasks: %s", exc)
            raise HTTPException(status_code=502, detail=f"Failed to load tasks: {type(exc).__name__}") from exc

    @app.post("/api/tasks", status_code=201)
    def create_task(req: TaskCreateRequest) -> Dict[str, Any]:
        try:
            return tsk_svc.create_task(
                title=req.title,
                list_id=req.list_id,
                notes=req.notes,
                due_date=req.due_date,
            )
        except GoogleAuthError as exc:
            raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": exc.message}) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            logger.error("Error creating task: %s", exc)
            raise HTTPException(status_code=502, detail=f"Task creation failed: {type(exc).__name__}") from exc

    @app.patch("/api/tasks/{task_id:path}")
    def patch_task(task_id: str, req: TaskUpdateRequest) -> Dict[str, Any]:
        try:
            return tsk_svc.update_task(
                task_id=task_id,
                list_id=req.list_id,
                title=req.title,
                notes=req.notes,
                status=req.status,
                due_date=req.due_date,
            )
        except GoogleAuthError as exc:
            raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": exc.message}) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except Exception as exc:
            logger.error("Error updating task: %s", exc)
            raise HTTPException(status_code=502, detail=f"Task update failed: {type(exc).__name__}") from exc

    @app.delete("/api/tasks/{task_id:path}")
    def delete_task(
        task_id: str,
        list_id: str = Query(default="@default"),
    ) -> Dict[str, Any]:
        try:
            return tsk_svc.delete_task(task_id=task_id, list_id=list_id)
        except GoogleAuthError as exc:
            raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": exc.message}) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            logger.error("Error deleting task: %s", exc)
            raise HTTPException(status_code=502, detail=f"Task deletion failed: {type(exc).__name__}") from exc

    @app.post("/api/google/connect")
    def connect_google(open_browser: bool = Query(default=True)) -> Dict[str, Any]:
        try:
            res = auth.start_oauth_flow(open_browser=open_browser)
            now = datetime.now()
            cal_svc.get_month_data(now.year, now.month, force_refresh=True)
            cal_svc.get_upcoming_events(limit=5, force_refresh=True)
            tsk_svc.get_tasks(force_refresh=True)
            return res
        except GoogleAuthError as exc:
            raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": exc.message}) from exc

    @app.post("/api/google/disconnect")
    def disconnect_google() -> Dict[str, Any]:
        res = auth.disconnect()
        local_cache.clear_all()
        return res

    @app.post("/api/sync")
    def trigger_manual_sync() -> Dict[str, Any]:
        auth_state = auth.get_auth_status()
        if not auth_state["authenticated"]:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "not_authenticated",
                    "message": "Connect your Google account before triggering synchronization.",
                },
            )
        now = datetime.now()
        month_data = cal_svc.get_month_data(now.year, now.month, force_refresh=True)
        upcoming_data = cal_svc.get_upcoming_events(limit=5, force_refresh=True)
        tasks_data = tsk_svc.get_tasks(
            list_id=cfg.settings.selected_task_list_id,
            include_completed=cfg.settings.show_completed_tasks,
            force_refresh=True,
        )
        return {
            "synced": True,
            "last_sync_time": local_cache.get_last_sync_time(),
            "calendar_events_in_month": month_data.get("total_events", 0),
            "upcoming_events_count": upcoming_data.get("count", 0),
            "active_tasks_count": tasks_data.get("total_active", 0),
        }

    @app.get("/api/weather")
    def get_weather(
        city: Optional[str] = Query(default=None),
        lat: Optional[float] = Query(default=None),
        lon: Optional[float] = Query(default=None),
        unit: Optional[str] = Query(default=None),
    ) -> Dict[str, Any]:
        return wth_svc.get_current_weather(city=city, lat=lat, lon=lon, unit=unit)

    @app.get("/api/settings")
    def get_settings() -> Dict[str, Any]:
        return cfg.settings.to_dict()

    @app.put("/api/settings")
    def update_settings(new_settings: SpaceGlassSettings) -> Dict[str, Any]:
        saved = cfg.save(new_settings)
        refresh_rainmeter_glass_windows(saved.blur_type, saved.glass_alpha)
        return saved.to_dict()

    @app.post("/api/settings/reset")
    def reset_settings() -> Dict[str, Any]:
        reset = cfg.reset_to_defaults()
        return reset.to_dict()

    return app


def acquire_single_instance_lock(lock_file: Path) -> bool:
    """Prevent duplicate instances of the SpaceGlass backend from running simultaneously."""
    if lock_file.exists():
        try:
            old_pid = int(lock_file.read_text(encoding="utf-8").strip())
            if old_pid != os.getpid():
                if os.name == "nt":
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    handle = kernel32.OpenProcess(0x1000, False, old_pid)
                    if handle:
                        kernel32.CloseHandle(handle)
                        return False
                else:
                    os.kill(old_pid, 0)
                    return False
        except (ValueError, OSError):
            pass
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    lock_file.write_text(str(os.getpid()), encoding="utf-8")
    return True


app = create_app(enable_background_sync=False)


if __name__ == "__main__":
    import uvicorn

    cfg_mgr = ConfigManager()
    if not acquire_single_instance_lock(cfg_mgr.lock_path):
        print("SpaceGlass backend is already running on 127.0.0.1. Exiting duplicate instance.")
        sys.exit(0)

    try:
        live_app = create_app(config_mgr=cfg_mgr, enable_background_sync=True)
        uvicorn.run(
            live_app,
            host="127.0.0.1",
            port=cfg_mgr.settings.port,
            log_level="info",
        )
    finally:
        with contextlib.suppress(Exception):
            if cfg_mgr.lock_path.exists():
                cfg_mgr.lock_path.unlink()
