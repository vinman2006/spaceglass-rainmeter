"""
SpaceGlass — Central Backend Configuration & Rainmeter Variable Synchronizer.
Manages application settings, protected local storage paths, single-instance
lock management, and Rainmeter Variables.inc / Theme.inc synchronization.
Compatible with both Pydantic v1 and Pydantic v2.
"""
from __future__ import annotations

import json
import logging
import os
import platform
import re
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("spaceglass.config")


def get_app_data_dir() -> Path:
    """Return protected per-user application data directory for tokens, cache, and logs."""
    override = os.environ.get("SPACEGLASS_DATA_DIR")
    if override:
        path = Path(override)
    elif platform.system() == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
        path = Path(local_app_data) / "SpaceGlass"
    else:
        path = Path.home() / ".local" / "share" / "spaceglass"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_project_root() -> Path:
    """Return the root directory of the SpaceGlass installation."""
    return Path(__file__).resolve().parent.parent


class SpaceGlassSettings(BaseModel):
    """Validated user settings model covering General, Appearance, Google, and Advanced tabs."""

    # General
    enable_clock: bool = True
    enable_calendar: bool = True
    enable_events: bool = True
    enable_tasks: bool = True
    right_margin: int = Field(default=24, ge=0, le=500)
    top_margin: int = Field(default=20, ge=0, le=500)
    widget_gap: int = Field(default=14, ge=0, le=120)
    widget_width: int = Field(default=320, ge=240, le=520)
    start_with_windows: bool = True
    use_24_hour: bool = True
    week_start_monday: bool = False

    # Weather (Optional, never fabricated)
    weather_enabled: bool = True
    city_name: str = "Nagpur"
    latitude: float = 21.1458
    longitude: float = 79.0882
    temperature_unit: str = "C"
    openweather_api_key: str = ""

    # Appearance
    glass_alpha: int = Field(default=95, ge=20, le=240)
    blur_type: str = "Acrylic"
    corner_radius: int = Field(default=22, ge=8, le=40)
    font_size_body: int = Field(default=10, ge=8, le=16)
    accent_color: str = "orange"

    # Google
    selected_calendar_id: str = "primary"
    selected_task_list_id: str = "@default"
    selected_task_list_name: str = "My Tasks"
    calendar_refresh_seconds: int = Field(default=900, ge=60, le=3600)
    tasks_refresh_seconds: int = Field(default=900, ge=30, le=3600)
    show_completed_tasks: bool = True
    collapse_completed_tasks: bool = False

    # Backend server
    host: str = "127.0.0.1"
    port: int = Field(default=8765, ge=1024, le=65535)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize settings to a dictionary across both Pydantic v1 and v2."""
        if hasattr(self, "model_dump"):
            return self.model_dump()  # type: ignore[attr-defined]
        return self.dict()


ACCENT_RGB_MAP = {
    "orange": "255,122,24",
    "violet": "166,108,219",
    "blue": "88,166,255",
}


class ConfigManager:
    """Loads, validates, persists, and syncs SpaceGlass settings with Rainmeter."""

    def __init__(self, data_dir: Optional[Path] = None, project_root: Optional[Path] = None) -> None:
        self.data_dir = data_dir or get_app_data_dir()
        self.project_root = project_root or get_project_root()
        self.settings_path = self.data_dir / "settings.json"
        self.credentials_path = self.data_dir / "credentials.json"
        self.token_path = self.data_dir / "token.bin"
        self.cache_db_path = self.data_dir / "cache.sqlite3"
        self.log_path = self.data_dir / "spaceglass.log"
        self.lock_path = self.data_dir / "backend.pid"
        self.settings: SpaceGlassSettings = self.load()

    def load(self) -> SpaceGlassSettings:
        if self.settings_path.exists():
            try:
                raw = json.loads(self.settings_path.read_text(encoding="utf-8"))
                return SpaceGlassSettings(**raw)
            except Exception as exc:
                logger.warning("Failed to parse settings.json, falling back to defaults: %s", exc)
        settings = SpaceGlassSettings()
        self.save(settings)
        return settings

    def save(self, settings: Optional[SpaceGlassSettings] = None) -> SpaceGlassSettings:
        if settings is not None:
            self.settings = settings
        self.data_dir.mkdir(parents=True, exist_ok=True)
        tmp_path = self.settings_path.with_suffix(".tmp")
        tmp_path.write_text(
            json.dumps(self.settings.to_dict(), indent=2),
            encoding="utf-8",
        )
        tmp_path.replace(self.settings_path)
        self.sync_rainmeter_inc_files()
        return self.settings

    def reset_to_defaults(self) -> SpaceGlassSettings:
        default_settings = SpaceGlassSettings()
        return self.save(default_settings)

    def sync_rainmeter_inc_files(self) -> None:
        """Synchronize current settings into @Resources/Variables.inc and @Resources/Theme.inc."""
        resources_dir = self.project_root / "@Resources"
        vars_file = resources_dir / "Variables.inc"
        theme_file = resources_dir / "Theme.inc"

        s = self.settings
        if vars_file.exists():
            self._update_ini_keys(
                vars_file,
                {
                    "BackendHost": s.host,
                    "BackendPort": str(s.port),
                    "BackendBaseUrl": f"http://{s.host}:{s.port}",
                    "WidgetWidth": str(s.widget_width),
                    "RightMargin": str(s.right_margin),
                    "TopMargin": str(s.top_margin),
                    "WidgetGap": str(s.widget_gap),
                    "Use24Hour": "1" if s.use_24_hour else "0",
                    "CityName": s.city_name,
                    "Latitude": str(s.latitude),
                    "Longitude": str(s.longitude),
                    "TemperatureUnit": s.temperature_unit,
                    "WeatherEnabled": "1" if s.weather_enabled else "0",
                    "WeekStartMonday": "1" if s.week_start_monday else "0",
                    "CalendarRefreshSeconds": str(s.calendar_refresh_seconds),
                    "SelectedCalendarId": s.selected_calendar_id,
                    "EventsRefreshSeconds": str(s.calendar_refresh_seconds),
                    "SelectedTaskListId": s.selected_task_list_id,
                    "SelectedTaskListName": s.selected_task_list_name,
                    "TasksRefreshSeconds": str(s.tasks_refresh_seconds),
                    "ShowCompletedTasks": "1" if s.show_completed_tasks else "0",
                    "CollapseCompletedTasks": "1" if s.collapse_completed_tasks else "0",
                },
            )

        if theme_file.exists():
            accent_rgb = ACCENT_RGB_MAP.get(s.accent_color, "255,122,24")
            self._update_ini_keys(
                theme_file,
                {
                    "ActiveAccent": accent_rgb,
                    "GlassAlpha": str(s.glass_alpha),
                    "BlurType": s.blur_type,
                    "GlassCornerRadius": str(s.corner_radius),
                    "FontSizeBody": str(s.font_size_body),
                },
            )

    @staticmethod
    def _update_ini_keys(file_path: Path, updates: Dict[str, str]) -> None:
        try:
            content = file_path.read_text(encoding="utf-8")
            for key, val in updates.items():
                pattern = re.compile(rf"^({re.escape(key)}\s*=).*$", re.MULTILINE)
                if pattern.search(content):
                    content = pattern.sub(rf"\g<1>{val}", content)
            file_path.write_text(content, encoding="utf-8")
        except Exception as exc:
            logger.warning("Could not update Rainmeter include %s: %s", file_path, exc)

    def find_credentials_file(self) -> Optional[Path]:
        """Locate credentials.json in %LOCALAPPDATA%\\SpaceGlass or Config/ directory."""
        candidates = [
            self.credentials_path,
            self.project_root / "Config" / "credentials.json",
            self.project_root / "Backend" / "credentials.json",
        ]
        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                return candidate
        return None
