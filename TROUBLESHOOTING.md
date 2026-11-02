# SPACEGLASS — Troubleshooting Guide

## 1. Widgets Show "Not linked" or "Connect Google Account in Settings"

- **Cause**: Google OAuth has not been completed yet, or `credentials.json` has not been placed in the configuration folder.
- **Resolution**:
  1. Ensure your downloaded Google Cloud OAuth Desktop Client file is named `credentials.json` and placed in `%LOCALAPPDATA%\SpaceGlass\credentials.json` (or `SpaceGlass\Config\credentials.json`).
  2. Right-click any widget → **SpaceGlass Settings...** → **GOOGLE** tab → **Connect Google Account**.
  3. Complete the browser consent flow and click **Sync Now**.

## 2. Google Sign-In Displays "Access Blocked: SpaceGlass has not completed the Google verification process"

- **Cause**: Your Google Cloud OAuth Consent Screen is in "Testing" mode and your Google email address has not been added to the **Test users** list.
- **Resolution**:
  1. Open [Google Cloud Console > APIs & Services > OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent).
  2. Scroll to **Test users**, click **+ Add Users**, and add your Google account email.
  3. Retry **Connect Google Account** in SpaceGlass Settings (`GOOGLE` tab). When prompted in the browser, click **Continue**.

## 3. Widgets Display "Offline" or "Backend not running"

- **Cause**: The local Python FastAPI companion server (`127.0.0.1:8765`) is not running.
- **Resolution**:
  1. Double-click `Installer\start_spaceglass.vbs` inside your `Documents\Rainmeter\Skins\SpaceGlass` directory, or run:
     ```powershell
     python Backend\app.py
     ```
  2. Open `http://127.0.0.1:8765/api/status` in your browser to verify the JSON health response shows `"status": "running"`.
  3. If port `8765` is in use by another local process, change `"port"` in `%LOCALAPPDATA%\SpaceGlass\settings.json` and click **Save & Apply** in SpaceGlass Settings.

## 4. Widgets Show "Cached" in the Header

- **Cause**: SpaceGlass distinguishes live API responses (`source: "live"`) from cached responses (`source: "cache"`). When `"Cached"` appears briefly or during an internet outage, the widget is displaying the most recent locally cached Google Calendar/Tasks snapshot from `%LOCALAPPDATA%\SpaceGlass\cache.sqlite3`.
- **Resolution**:
  - Once internet connectivity returns, SpaceGlass automatically recovers on the next sync cycle (or you can right-click any widget and click **Sync Tasks Now** / **Refresh Upcoming Events**).

## 5. Frosted Glass Blur Looks Flat (No Background Blur)

- **Cause**: Windows 11 disables DWM Acrylic/Blur when system transparency effects are disabled or Energy Saver is active.
- **Resolution**:
  1. Open **Windows Settings > Personalization > Colors** and turn **Transparency effects** **On**.
  2. Ensure **Windows Energy Saver / Battery Saver** is turned off.
  3. Right-click a widget → **SpaceGlass Settings...** → **APPEARANCE** tab → verify **Windows 11 Blur Mode** is set to `Acrylic` or `Blur`, and adjust the **Glass Transparency** slider (`75`–`110` works best over dark nebula wallpapers).

## 6. Weather Information Is Hidden in the Clock Widget

- **Cause**: SpaceGlass never fabricates weather data. If `WeatherEnabled=0` or the computer has no internet connection when querying Open-Meteo/OpenWeatherMap for the first time, the weather meters hide gracefully.
- **Resolution**:
  1. Right-click the Clock widget → **Configure City & Weather...**.
  2. Check **Enable live Weather display**, verify your **Weather City** name, and click **Save & Apply**.

## 7. Inspecting Application Logs

- All backend requests, OAuth events, and API errors (with zero token leakage) are logged to:
  ```text
  %LOCALAPPDATA%\SpaceGlass\spaceglass.log
  ```
- You can open this file directly from **SpaceGlass Settings > ADVANCED > Open Logs**.
