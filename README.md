# SPACEGLASS — Desktop Widget System for Windows 11

> **Your Universe. Your Schedule.**  
> Apple-inspired space glassmorphism desktop widgets for Windows 11 with live two-way Google Tasks and Google Calendar synchronization.

## 1. Overview

**SpaceGlass** is a full-stack Windows 11 desktop widget system combining modular **Rainmeter** skins, **Windows 11 DWM Acrylic/Mica composition**, and a localhost-only **Python 3.11+ FastAPI** companion backend. It displays four floating, independently movable frosted-glass widgets along the right edge of your desktop over your space nebula wallpaper:

1. **Clock & Weather (`Clock/Clock.ini`)**: Real-time system clock (`19:30`, 12h/24h toggle), current day and date (`Sun, Nov 1`), and optional live weather (`28° · Nagpur`) powered by Open-Meteo or OpenWeatherMap (gracefully hidden if disabled or unconfigured).
2. **Monthly Calendar (`Calendar/Calendar.ini`)**: Interactive monthly calendar with `<` and `>` month navigation, accurate leap-year math, Sunday-first or Monday-first week layout, `#FF7A18` orange pill highlight on today's date, colored event dots (`#A66CDB`, `#58A6FF`, `#FF7A18`), and click-a-date event inspection.
3. **Upcoming Events (`Events/Events.ini`)**: Chronological list of upcoming Google Calendar events with vertical color accent bars, all-day and recurring event support, click-to-open event links, and a `+` button to create new events in Google Calendar.
4. **Google Tasks (`Tasks/Tasks.ini`)**: Two-way synchronized Google Tasks widget with interactive completion checkboxes, `#FF7A18` orange checked badges with strikethrough styling, task reopening, task creation (`+`), task deletion with confirmation, task list switching, overdue badges, and a collapsible completed tasks section.

## 2. Project Structure

```text
SpaceGlass/
├── SpaceGlass.ini                  # Master suite launcher & right-stack layout controller
├── Clock/
│   └── Clock.ini                   # Widget 1: Clock & Weather skin
├── Calendar/
│   └── Calendar.ini                # Widget 2: Interactive Monthly Calendar skin
├── Events/
│   └── Events.ini                  # Widget 3: Upcoming Google Calendar Events skin
├── Tasks/
│   └── Tasks.ini                   # Widget 4: Two-Way Google Tasks skin
├── @Resources/
│   ├── Variables.inc               # User preferences, coordinates, and refresh rates
│   ├── Theme.inc                   # Color palette, glass alpha, DWM blur mode, typography
│   ├── Data/
│   │   └── CalendarCells.inc       # 42 dynamic date cells & event indicator dot meters
│   ├── Icons/                      # High-DPI PNG & SVG widget badges, checkboxes, weather icons
│   ├── Images/
│   │   └── glass_reflection.png    # Specular frosted-glass top-left light refraction overlay
│   └── Scripts/
│       ├── json_helper.lua         # Pure Lua 5.1 RFC 8259 JSON parser & URL encoder
│       ├── clock_weather.lua       # Clock 12/24h & weather response handler
│       ├── calendar.lua            # Gregorian leap-year math, navigation & event dot engine
│       ├── events.lua              # Upcoming events renderer & browser launcher
│       └── tasks.lua               # Interactive Google Tasks controller
├── Backend/
│   ├── __init__.py
│   ├── app.py                      # Localhost FastAPI server (127.0.0.1:8765) & sync scheduler
│   ├── config.py                   # Pydantic settings manager & Rainmeter .inc synchronizer
│   ├── google_auth.py              # Google OAuth 2.0 Desktop flow + Windows DPAPI token storage
│   ├── calendar_service.py         # Official Google Calendar API v3 integration
│   ├── tasks_service.py            # Official Google Tasks API v1 integration
│   ├── weather_service.py          # Open-Meteo & OpenWeatherMap integration
│   ├── cache.py                    # SQLite local cache (strictly tags `source: "cache"` vs `"live"`)
│   ├── glass_effect.py             # Windows 11 DWM Acrylic/Mica & rounded corner composition helper
│   ├── companion_ui.py             # 4-Tab Settings GUI + Quick Add/Delete Task dialogs
│   └── requirements.txt            # Python 3.11+ package dependencies
├── Config/
│   ├── settings.example.json       # Example user configuration
│   └── credentials.example.json    # Example Google OAuth Desktop client structure
├── Installer/
│   ├── install.bat                 # One-click Windows batch installer
│   ├── install.ps1                 # PowerShell installation & startup setup script
│   ├── uninstall.ps1               # Clean uninstaller with confirmation prompts
│   └── start_spaceglass.vbs        # Windowless background startup launcher
├── Tests/
│   └── test_spaceglass_suite.py    # Automated unit & FastAPI integration test suite
├── TROUBLESHOOTING.md              # Step-by-step diagnostic & troubleshooting guide
├── ANTIGRAVITY_HANDOVER.md         # Engineering handover & verification guide for Antigravity
├── README.md                       # This guide
└── .gitignore                      # Protects credentials.json, tokens, caches, and logs
```

## 3. Prerequisites (Windows 11)

1. **Windows 11** (22H2 or newer recommended for native DWM rounded corners and Acrylic backdrop).
2. **Python 3.11 or newer** installed from [python.org](https://www.python.org/downloads/) with **"Add Python to PATH"** checked.
3. **Rainmeter 4.5 or newer** installed from [rainmeter.net](https://www.rainmeter.net/).

## 4. Quick Installation

1. Extract the `SpaceGlass` folder to your computer.
2. Double-click `Installer\install.bat` (or run `powershell -ExecutionPolicy Bypass -File Installer\install.ps1`).
3. The installer will:
   - Verify Python 3.11+ and Rainmeter.
   - Install all required Python dependencies from `Backend\requirements.txt`.
   - Create `%LOCALAPPDATA%\SpaceGlass` for protected token and cache storage.
   - Copy the `SpaceGlass` skin suite into `%USERPROFILE%\Documents\Rainmeter\Skins\SpaceGlass` (asking for confirmation first if a folder already exists).
   - Optionally add a Windows Startup shortcut so the backend starts silently on sign-in.
   - Launch the companion backend on `http://127.0.0.1:8765` and activate all four widgets on the right side of your desktop.

## 5. How to Create & Configure Google OAuth `credentials.json`

SpaceGlass uses the official **Google OAuth 2.0 Desktop Application** flow so your credentials remain strictly under your control and are never hardcoded:

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g., `SpaceGlass Desktop Widgets`) and select it.
3. Navigate to **APIs & Services > Library** and enable both APIs:
   - **Google Calendar API**
   - **Google Tasks API**
4. Navigate to **APIs & Services > OAuth consent screen**:
   - Choose **External** (or Internal if using Google Workspace) and click **Create**.
   - Enter App name: `SpaceGlass`, your support email, and developer contact email.
   - Under **Scopes**, add:
     - `https://www.googleapis.com/auth/calendar.readonly`
     - `https://www.googleapis.com/auth/tasks`
   - Under **Test users**, add your own Google account email address.
5. Navigate to **APIs & Services > Credentials**:
   - Click **+ Create Credentials > OAuth client ID**.
   - Select Application type: **Desktop app** and name it `SpaceGlass Windows 11 Client`.
   - Click **Create**, then click **Download JSON**.
6. Rename the downloaded file to `credentials.json` and place it in:
   ```text
   %LOCALAPPDATA%\SpaceGlass\credentials.json
   ```
   *(Alternatively, you can place it in `SpaceGlass\Config\credentials.json`.)*
7. Right-click any SpaceGlass desktop widget and choose **SpaceGlass Settings...**, open the **GOOGLE** tab, and click **Connect Google Account**.
8. Complete the Google sign-in in your browser. Your widgets will immediately synchronize with your live Google Calendar and Google Tasks.

## 6. Glassmorphism Architecture & Documented Limitations

- **How SpaceGlass Achieves Frosted Glass**: Rainmeter's built-in `SolidColor` only draws flat alpha transparency without background blur. SpaceGlass combines Rainmeter's `FrostedGlass` plugin (`Type=Acrylic`, `Corner=Round`, `Backdrop=Dark`), multi-stop specular border gradients, a top-left radial refraction overlay (`glass_reflection.png`), and native Windows 11 DWM API calls (`DwmSetWindowAttribute` with `DWMWA_WINDOW_CORNER_PREFERENCE = 33` and `SetWindowCompositionAttribute` with `ACCENT_ENABLE_ACRYLICBLURBEHIND = 4` in `Backend/glass_effect.py`).
- **Known Windows 11 Limitations**:
  - Windows 11 automatically disables DWM Acrylic blur when **Energy Saver / Battery Saver** is active or when **Settings > Personalization > Colors > Transparency effects** is turned off.
  - On older GPU drivers where `Acrylic` exhibits drag latency when moving widgets, open **SpaceGlass Settings > APPEARANCE** and switch **Windows 11 Blur Mode** from `Acrylic` to `Blur`.

## 7. Running Automated Tests

To verify all backend services, calendar math, leap years, timezone conversions, OAuth error handling, caching, and Rainmeter skin files independently of Rainmeter:

```powershell
cd SpaceGlass
python Tests\test_spaceglass_suite.py
```
