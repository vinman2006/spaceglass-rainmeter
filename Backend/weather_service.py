"""
SpaceGlass — Legitimate Weather Service (Backend/weather_service.py).
Retrieves real weather conditions for the user's configured city/coordinates:
- Supports OpenWeatherMap API (if user configures `openweather_api_key`)
- Supports Open-Meteo API out of the box (no API key required)
- Never fabricates weather data: if `weather_enabled=False` or network/API is
  unreachable and no valid cache exists, returns `available=False` so the
  Rainmeter Clock widget hides the weather block gracefully.
"""
from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional

from Backend.cache import LocalCache
from Backend.config import ConfigManager

logger = logging.getLogger("spaceglass.weather")


def map_wmo_code_to_icon(wmo_code: int) -> str:
    """Map WMO weather interpretation code to SpaceGlass icon filename."""
    if wmo_code == 0:
        return "weather_clear.png"
    if wmo_code in (1, 2, 3, 45, 48):
        return "weather_partly_cloudy.png"
    return "weather_rain.png"


class WeatherService:
    """Fetches real weather data from Open-Meteo or OpenWeatherMap with graceful fallback."""

    def __init__(self, config_mgr: ConfigManager, cache: LocalCache) -> None:
        self.config_mgr = config_mgr
        self.cache = cache

    def get_current_weather(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        unit: Optional[str] = None,
    ) -> Dict[str, Any]:
        s = self.config_mgr.settings
        if not s.weather_enabled:
            return {"available": False, "reason": "weather_disabled"}

        target_city = (city or s.city_name or "").strip()
        target_lat = lat if lat is not None else s.latitude
        target_lon = lon if lon is not None else s.longitude
        target_unit = (unit or s.temperature_unit or "C").upper()

        if not target_city and (target_lat is None or target_lon is None):
            return {"available": False, "reason": "unconfigured"}

        cache_key = f"weather:{target_city}:{target_lat}:{target_lon}:{target_unit}"
        cached = self.cache.get(cache_key, allow_expired=False)
        if cached is not None:
            data, _ = cached
            return data

        try:
            if s.openweather_api_key.strip():
                live = self._fetch_openweather(target_city, target_lat, target_lon, target_unit, s.openweather_api_key.strip())
            else:
                live = self._fetch_open_meteo(target_city, target_lat, target_lon, target_unit)
            self.cache.set(cache_key, live, ttl_seconds=900)
            return live
        except Exception as exc:
            logger.warning("Weather API unreachable (%s). Checking cache.", type(exc).__name__)
            stale = self.cache.get(cache_key, allow_expired=True)
            if stale is not None:
                stale_data, _ = stale
                return stale_data
            return {"available": False, "reason": f"unreachable:{type(exc).__name__}"}

    def _fetch_open_meteo(self, city: str, lat: float, lon: float, unit: str) -> Dict[str, Any]:
        temp_unit = "fahrenheit" if unit == "F" else "celsius"
        params = urllib.parse.urlencode(
            {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,weather_code",
                "temperature_unit": temp_unit,
            }
        )
        url = f"https://api.open-meteo.com/v1/forecast?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "SpaceGlass/1.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        current = data.get("current") or {}
        temp_val = current.get("temperature_2m")
        if temp_val is None:
            return {"available": False, "reason": "no_temperature_in_response"}

        wmo_code = int(current.get("weather_code", 1))
        return {
            "available": True,
            "source": "live",
            "provider": "open-meteo",
            "city": city or "Nagpur",
            "temperature": round(float(temp_val), 1),
            "unit": unit,
            "weather_code": wmo_code,
            "icon": map_wmo_code_to_icon(wmo_code),
        }

    def _fetch_openweather(
        self,
        city: str,
        lat: float,
        lon: float,
        unit: str,
        api_key: str,
    ) -> Dict[str, Any]:
        units_param = "imperial" if unit == "F" else "metric"
        params = urllib.parse.urlencode(
            {
                "lat": lat,
                "lon": lon,
                "units": units_param,
                "appid": api_key,
            }
        )
        url = f"https://api.openweathermap.org/data/2.5/weather?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "SpaceGlass/1.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        main_block = data.get("main") or {}
        temp_val = main_block.get("temp")
        if temp_val is None:
            return {"available": False, "reason": "no_temperature_in_response"}

        weather_list = data.get("weather") or [{}]
        wid = int(weather_list[0].get("id", 801))
        if wid == 800:
            icon = "weather_clear.png"
        elif 200 <= wid < 700:
            icon = "weather_rain.png"
        else:
            icon = "weather_partly_cloudy.png"

        return {
            "available": True,
            "source": "live",
            "provider": "openweathermap",
            "city": city or data.get("name") or "Nagpur",
            "temperature": round(float(temp_val), 1),
            "unit": unit,
            "weather_code": wid,
            "icon": icon,
        }
