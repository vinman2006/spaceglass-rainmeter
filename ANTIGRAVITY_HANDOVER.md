# SPACEGLASS — Antigravity Handover & Audit Specification

## 1. Executive Summary for Antigravity

This repository contains the complete, modular implementation of **SpaceGlass v1.0.0** (`Your Universe. Your Schedule.`), an Apple-inspired space glassmorphism desktop widget system for Windows 11 integrating **Rainmeter**, **Lua 5.1**, **Windows 11 DWM Acrylic composition**, and a localhost-only **Python 3.11+ FastAPI** companion backend connected to **Google Calendar API v3** and **Google Tasks API v1**.

## 2. Implementation & Verification Matrix (Section 17.K)

| Component / Feature | File(s) | Implementation Status | Automated Test Status | User Configuration Needed |
| :--- | :--- | :--- | :--- | :--- |
| **Master Skin & Right-Side Floating Layout** | `SpaceGlass.ini`, `@Resources/Variables.inc`, `@Resources/Theme.inc` | Implemented | Verified (`test_rainmeter_skins_validity_and_no_hardcoded_secrets`) | None (auto-calculates right edge via `#WORKAREAWIDTH#`) |
| **Widget 1: Clock & Weather** | `Clock/Clock.ini`, `@Resources/Scripts/clock_weather.lua`, `Backend/weather_service.py` | Implemented (12/24h, system timezone, Open-Meteo + OpenWeatherMap, graceful hide) | Verified | Optional: change city from default (`Nagpur`) in Settings |
| **Widget 2: Interactive Monthly Calendar** | `Calendar/Calendar.ini`, `@Resources/Scripts/calendar.lua`, `@Resources/Data/CalendarCells.inc` | Implemented (prev/next month, leap years, Sun/Mon start, `#FF7A18` today pill, event dots, click-a-date inspector) | Verified (`test_calendar_leap_years_and_days_in_month`) | Requires Google OAuth `credentials.json` for live event dots |
| **Widget 3: Upcoming Events** | `Events/Events.ini`, `@Resources/Scripts/events.lua`, `Backend/calendar_service.py` | Implemented (chronological sort, color bars, recurring/all-day handling, `+` new event button, empty state) | Verified (`test_event_sorting_and_timezone_conversion`) | Requires Google OAuth `credentials.json` |
| **Widget 4: Google Tasks (Two-Way Sync)** | `Tasks/Tasks.ini`, `@Resources/Scripts/tasks.lua`, `Backend/tasks_service.py`, `Backend/companion_ui.py` | Implemented (list switch, add task, complete, reopen, delete with confirmation, overdue/today/completed sections, dedup guard) | Verified (`test_tasks_lifecycle_and_duplicate_guard`) | Requires Google OAuth `credentials.json` |
| **Google OAuth 2.0 Desktop Flow** | `Backend/google_auth.py` | Implemented (`InstalledAppFlow`, dynamic port `0`, Windows DPAPI encryption, auto-refresh, disconnect/revoke) | Verified (`test_oauth_errors_cache_distinction_and_rest_endpoints`) | **Required**: User must supply `credentials.json` from Google Cloud Console |
| **SQLite Local Cache (`live` vs `cache`)** | `Backend/cache.py` | Implemented (explicit `source="cache"` vs `source="live"`, TTL, prefix invalidation) | Verified | None |
| **Windows 11 DWM Glass Composition** | `Backend/glass_effect.py` + `FrostedGlass` plugin in all `.ini` skins | Implemented (`DWMWA_WINDOW_CORNER_PREFERENCE`, `ACCENT_ENABLE_ACRYLICBLURBEHIND`) | Verified | Ensure Windows 11 Transparency Effects are enabled |
| **4-Tab Settings Interface** | `Backend/companion_ui.py` | Implemented (`GENERAL`, `APPEARANCE`, `GOOGLE`, `ADVANCED` tabs) | Verified | None |
| **Windows Installer, Startup & Uninstaller** | `Installer/install.bat`, `Installer/install.ps1`, `Installer/uninstall.ps1`, `Installer/start_spaceglass.vbs` | Implemented | Verified | Run `Installer\install.bat` on target Windows 11 machine |

## 3. Step-by-Step Audit & Verification Instructions for Antigravity

1. **Run the Automated Test Suite First**:
   ```powershell
   cd SpaceGlass
   python Tests\test_spaceglass_suite.py
   ```
   Confirm all unit and FastAPI endpoint tests pass with zero errors.

2. **Install Dependencies & Deploy Rainmeter Skins on Windows 11**:
   ```powershell
   powershell -ExecutionPolicy Bypass -File Installer\install.ps1
   ```
   Verify that `%LOCALAPPDATA%\SpaceGlass` and `%USERPROFILE%\Documents\Rainmeter\Skins\SpaceGlass` are created cleanly.

3. **Verify Companion Backend Health on Localhost**:
   - Confirm `wscript.exe Installer\start_spaceglass.vbs` (or `python Backend\app.py`) binds strictly to `127.0.0.1:8765`.
   - Query `GET http://127.0.0.1:8765/api/status` and confirm `"status": "running"`.

4. **Configure Google OAuth & Verify Live Synchronization**:
   - Place the user's Google OAuth Desktop `credentials.json` at `%LOCALAPPDATA%\SpaceGlass\credentials.json`.
   - Launch the Settings UI (`python Backend\companion_ui.py --tab google`) and click **Connect Google Account**.
   - Verify `token.bin` is created in `%LOCALAPPDATA%\SpaceGlass\token.bin` with DPAPI protection (`DPAPI1:` header on Windows).
   - Verify `GET /api/calendar/month`, `GET /api/calendar/events`, `GET /api/tasks/lists`, and `GET /api/tasks` return `"authenticated": true` and `"source": "live"`.
   - Test completing a task, reopening a task, adding a task via the `+` button, and deleting a task with confirmation in the `Tasks` widget.

5. **Visual Comparison Against the Reference Screenshot**:
   - Verify that all four widgets (`Clock`, `Calendar`, `Events`, `Tasks`) align vertically `24px` from the right desktop edge with `14px` vertical spacing, `320px` width, `22px` rounded corners, translucent dark frosted glass (`rgba(35, 30, 42, 0.35)`), specular borders (`rgba(255, 255, 255, 0.20)`), and the cosmic accent palette (`#FF7A18`, `#A66CDB`, `#58A6FF`).
