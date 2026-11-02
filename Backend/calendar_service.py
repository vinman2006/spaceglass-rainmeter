"""
SpaceGlass — Google Calendar API v3 Service (Backend/calendar_service.py).
Provides real Google Calendar integration:
- Month grid aggregation (`GET /api/calendar/month?year=YYYY&month=MM`)
- Chronological upcoming events (`GET /api/calendar/events`)
- Individual event lookup (`GET /api/calendar/events/{event_id}`)
- Handles recurring event expansion (`singleEvents=True`), all-day events,
  pagination (`pageToken`), cancelled event filtering, and timezone conversion.
- Never fabricates events in production mode.
"""
from __future__ import annotations

import calendar
import logging
from datetime import date, datetime, time as dt_time, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import unquote

from dateutil import parser as date_parser
from dateutil import tz

from Backend.cache import LocalCache
from Backend.config import ConfigManager
from Backend.google_auth import GoogleAuthError, GoogleAuthManager

logger = logging.getLogger("spaceglass.calendar")

# Map Google Calendar colorId (1..11) to SpaceGlass cosmic palette RGB strings
GOOGLE_COLOR_ID_TO_RGB: Dict[str, str] = {
    "1": "166,108,219",   # Lavender -> Cosmic Violet
    "2": "88,166,255",    # Sage -> Cosmic Blue
    "3": "166,108,219",   # Grape -> Cosmic Violet
    "4": "255,122,24",    # Flamingo -> Primary Orange
    "5": "255,180,92",    # Banana -> Amber
    "6": "255,122,24",    # Tangerine -> Primary Orange
    "7": "88,166,255",    # Peacock -> Cosmic Blue
    "8": "197,190,207",   # Graphite -> Muted
    "9": "88,166,255",    # Blueberry -> Cosmic Blue
    "10": "88,166,255",   # Basil -> Cosmic Blue
    "11": "255,122,24",   # Tomato -> Primary Orange
}
DEFAULT_CYCLE_COLORS = ["166,108,219", "88,166,255", "255,122,24", "255,180,92"]


def is_leap_year(year: int) -> bool:
    """Return True if year is a leap year in the proleptic Gregorian calendar."""
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def get_days_in_month(year: int, month: int) -> int:
    """Return the exact number of days in (year, month), accounting for leap years."""
    if not (1 <= month <= 12):
        raise ValueError(f"Month must be in 1..12, got {month}")
    if year < 1970 or year > 2100:
        raise ValueError(f"Year must be in 1970..2100, got {year}")
    return calendar.monthrange(year, month)[1]


def format_event_display_time(
    start_dt: datetime,
    end_dt: datetime,
    is_all_day: bool,
    reference_now: Optional[datetime] = None,
) -> str:
    """
    Format an event's start/end time into the compact SpaceGlass subtitle format
    shown in the reference screenshot:
      - "Tomorrow · 10:30 – 11:30 AM"
      - "Today · 2:00 – 3:00 PM"
      - "Tue, Nov 3 · 11:59 PM"
      - "Wed, Nov 4 · All day"
    """
    local_tz = start_dt.tzinfo or tz.tzlocal()
    now_local = (reference_now or datetime.now(local_tz)).astimezone(local_tz)
    today_date = now_local.date()
    tomorrow_date = today_date + timedelta(days=1)
    ev_date = start_dt.date()

    if ev_date == today_date:
        day_prefix = "Today"
    elif ev_date == tomorrow_date:
        day_prefix = "Tomorrow"
    else:
        day_prefix = f"{start_dt.strftime('%a, %b')} {start_dt.day}"

    if is_all_day:
        return f"{day_prefix} · All day"

    def _fmt_clock(dt_obj: datetime, include_ampm: bool = True) -> str:
        hour12 = dt_obj.hour % 12 or 12
        minute = dt_obj.strftime("%M")
        if include_ampm:
            ampm = "AM" if dt_obj.hour < 12 else "PM"
            return f"{hour12}:{minute} {ampm}"
        return f"{hour12}:{minute}"

    # If start and end are identical (e.g., assignment due time 11:59 PM) or <1 min apart
    if abs((end_dt - start_dt).total_seconds()) < 60:
        return f"{day_prefix} · {_fmt_clock(start_dt, True)}"

    same_meridiem = (start_dt.hour < 12) == (end_dt.hour < 12) and (ev_date == end_dt.date())
    start_str = _fmt_clock(start_dt, include_ampm=not same_meridiem)
    end_str = _fmt_clock(end_dt, include_ampm=True)
    return f"{day_prefix} · {start_str} – {end_str}"


def normalize_google_event(
    raw_event: Dict[str, Any],
    index: int = 0,
    local_tz: Optional[Any] = None,
    reference_now: Optional[datetime] = None,
) -> Optional[Dict[str, Any]]:
    """
    Convert a raw Google Calendar API event resource into a normalized SpaceGlass dictionary.
    Returns None if the event is cancelled or malformed.
    """
    if raw_event.get("status") == "cancelled":
        return None

    target_tz = local_tz or tz.tzlocal()
    start_info = raw_event.get("start") or {}
    end_info = raw_event.get("end") or {}

    is_all_day = "date" in start_info and "dateTime" not in start_info

    try:
        if is_all_day:
            start_date = date.fromisoformat(start_info["date"])
            end_date_raw = date.fromisoformat(end_info.get("date", start_info["date"]))
            # Google Calendar all-day end dates are exclusive; keep inclusive end date
            inclusive_end_date = max(start_date, end_date_raw - timedelta(days=1))
            start_dt = datetime.combine(start_date, dt_time(0, 0), tzinfo=target_tz)
            end_dt = datetime.combine(inclusive_end_date, dt_time(23, 59, 59), tzinfo=target_tz)
        else:
            start_dt = date_parser.isoparse(start_info["dateTime"]).astimezone(target_tz)
            if "dateTime" in end_info:
                end_dt = date_parser.isoparse(end_info["dateTime"]).astimezone(target_tz)
            else:
                end_dt = start_dt
    except Exception as exc:
        logger.warning("Skipping event with invalid date format: %s", exc)
        return None

    color_id = str(raw_event.get("colorId", ""))
    color_rgb = GOOGLE_COLOR_ID_TO_RGB.get(
        color_id,
        DEFAULT_CYCLE_COLORS[index % len(DEFAULT_CYCLE_COLORS)],
    )

    display_time = format_event_display_time(start_dt, end_dt, is_all_day, reference_now=reference_now)
    time_label = "All day" if is_all_day else start_dt.strftime("%I:%M %p").lstrip("0")

    return {
        "id": raw_event.get("id", ""),
        "title": raw_event.get("summary") or "(No title)",
        "description": raw_event.get("description") or "",
        "location": raw_event.get("location") or "",
        "start_iso": start_dt.isoformat(),
        "end_iso": end_dt.isoformat(),
        "start_date": start_dt.date().isoformat(),
        "end_date": end_dt.date().isoformat(),
        "is_all_day": is_all_day,
        "display_time": display_time,
        "time_label": time_label,
        "color_id": color_id,
        "color_rgb": color_rgb,
        "html_link": raw_event.get("htmlLink") or "https://calendar.google.com/calendar/r",
        "recurring_event_id": raw_event.get("recurringEventId"),
    }


class CalendarService:
    """Interacts with the official Google Calendar v3 API with pagination and local caching."""

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

    def _build_service(self) -> Any:
        if self._client_factory is not None:
            return self._client_factory()
        creds = self.auth_mgr.get_valid_credentials()
        from googleapiclient.discovery import build

        return build("calendar", "v3", credentials=creds, cache_discovery=False)

    def _fetch_events_window(
        self,
        calendar_id: str,
        time_min: datetime,
        time_max: datetime,
        max_total: int = 250,
    ) -> List[Dict[str, Any]]:
        """Fetch and paginate through Google Calendar events within [time_min, time_max]."""
        service = self._build_service()
        raw_items: List[Dict[str, Any]] = []
        page_token: Optional[str] = None

        while True:
            req = service.events().list(
                calendarId=calendar_id,
                timeMin=time_min.astimezone(timezone.utc).isoformat(),
                timeMax=time_max.astimezone(timezone.utc).isoformat(),
                singleEvents=True,
                orderBy="startTime",
                maxResults=min(250, max_total),
                pageToken=page_token,
            )
            resp = req.execute()
            batch = resp.get("items", [])
            raw_items.extend(batch)
            page_token = resp.get("nextPageToken")
            if not page_token or len(raw_items) >= max_total:
                break

        local_tz = tz.tzlocal()
        normalized: List[Dict[str, Any]] = []
        for idx, item in enumerate(raw_items):
            norm = normalize_google_event(item, index=idx, local_tz=local_tz)
            if norm is not None:
                normalized.append(norm)

        normalized.sort(key=lambda e: e["start_iso"])
        return normalized

    def get_month_data(self, year: int, month: int, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Return calendar metadata and per-day event indicators for (year, month).
        Supports leap years, multi-day all-day events, and offline cache fallback.
        """
        total_days = get_days_in_month(year, month)
        first_weekday_mon0, _ = calendar.monthrange(year, month)  # 0=Mon..6=Sun
        first_weekday_sun0 = (first_weekday_mon0 + 1) % 7
        cal_id = self.config_mgr.settings.selected_calendar_id or "primary"
        cache_key = f"calendar:month:{cal_id}:{year:04d}-{month:02d}"

        if not force_refresh:
            cached = self.cache.get(cache_key, allow_expired=False)
            if cached is not None:
                data, _ = cached
                return data

        local_tz = tz.tzlocal()
        start_of_month = datetime(year, month, 1, 0, 0, 0, tzinfo=local_tz)
        end_of_month = datetime(year, month, total_days, 23, 59, 59, tzinfo=local_tz)

        try:
            events = self._fetch_events_window(cal_id, start_of_month, end_of_month)
            days_map: Dict[str, Dict[str, Any]] = {}

            for ev in events:
                ev_start = date.fromisoformat(ev["start_date"])
                ev_end = date.fromisoformat(ev["end_date"])
                cur = max(ev_start, date(year, month, 1))
                last = min(ev_end, date(year, month, total_days))
                while cur <= last:
                    d_key = str(cur.day)
                    if d_key not in days_map:
                        days_map[d_key] = {
                            "count": 0,
                            "color_rgb": ev["color_rgb"],
                            "events": [],
                        }
                    days_map[d_key]["count"] += 1
                    days_map[d_key]["events"].append(
                        {
                            "id": ev["id"],
                            "title": ev["title"],
                            "time_label": ev["time_label"],
                            "display_time": ev["display_time"],
                            "html_link": ev["html_link"],
                            "color_rgb": ev["color_rgb"],
                        }
                    )
                    cur += timedelta(days=1)

            payload = {
                "authenticated": True,
                "source": "live",
                "cached": False,
                "year": year,
                "month": month,
                "month_name": calendar.month_name[month],
                "days_in_month": total_days,
                "is_leap_year": is_leap_year(year),
                "first_weekday_sunday_0": first_weekday_sun0,
                "first_weekday_monday_0": first_weekday_mon0,
                "days": days_map,
                "total_events": len(events),
            }
            self.cache.set(cache_key, payload, ttl_seconds=self.config_mgr.settings.calendar_refresh_seconds)
            return payload

        except GoogleAuthError as auth_err:
            return {
                "authenticated": False,
                "source": "none",
                "cached": False,
                "error_code": auth_err.code,
                "error": auth_err.message,
                "year": year,
                "month": month,
                "month_name": calendar.month_name[month],
                "days_in_month": total_days,
                "is_leap_year": is_leap_year(year),
                "first_weekday_sunday_0": first_weekday_sun0,
                "first_weekday_monday_0": first_weekday_mon0,
                "days": {},
                "total_events": 0,
            }
        except Exception as exc:
            logger.warning("Live month calendar fetch failed (%s), checking offline cache.", exc)
            stale = self.cache.get(cache_key, allow_expired=True)
            if stale is not None:
                stale_data, _ = stale
                stale_data["warning"] = f"Showing offline cached calendar ({type(exc).__name__})."
                return stale_data
            return {
                "authenticated": True,
                "source": "error",
                "cached": False,
                "error": f"Unable to retrieve calendar month: {type(exc).__name__}",
                "year": year,
                "month": month,
                "month_name": calendar.month_name[month],
                "days_in_month": total_days,
                "is_leap_year": is_leap_year(year),
                "first_weekday_sunday_0": first_weekday_sun0,
                "first_weekday_monday_0": first_weekday_mon0,
                "days": {},
                "total_events": 0,
            }

    def get_upcoming_events(self, limit: int = 5, force_refresh: bool = False) -> Dict[str, Any]:
        """Return the next `limit` upcoming events sorted chronologically."""
        limit = max(1, min(limit, 20))
        cal_id = self.config_mgr.settings.selected_calendar_id or "primary"
        cache_key = f"calendar:upcoming:{cal_id}:{limit}"

        if not force_refresh:
            cached = self.cache.get(cache_key, allow_expired=False)
            if cached is not None:
                data, _ = cached
                return data

        local_tz = tz.tzlocal()
        now_local = datetime.now(local_tz)
        horizon = now_local + timedelta(days=60)

        try:
            events = self._fetch_events_window(cal_id, now_local, horizon, max_total=50)
            upcoming = events[:limit]
            payload = {
                "authenticated": True,
                "source": "live",
                "cached": False,
                "calendar_id": cal_id,
                "events": upcoming,
                "count": len(upcoming),
                "empty_message": "No upcoming events. Enjoy your free time!" if not upcoming else "",
            }
            self.cache.set(cache_key, payload, ttl_seconds=self.config_mgr.settings.calendar_refresh_seconds)
            return payload

        except GoogleAuthError as auth_err:
            return {
                "authenticated": False,
                "source": "none",
                "cached": False,
                "error_code": auth_err.code,
                "error": auth_err.message,
                "events": [],
                "count": 0,
            }
        except Exception as exc:
            logger.warning("Live upcoming events fetch failed (%s), checking offline cache.", exc)
            stale = self.cache.get(cache_key, allow_expired=True)
            if stale is not None:
                stale_data, _ = stale
                stale_data["warning"] = f"Offline cached events ({type(exc).__name__})."
                return stale_data
            raise

    def get_event_details(self, event_id: str) -> Dict[str, Any]:
        """Retrieve details for a single Google Calendar event by URL-decoded ID."""
        clean_id = unquote(event_id).strip()
        if not clean_id:
            raise ValueError("event_id must not be empty")
        cal_id = self.config_mgr.settings.selected_calendar_id or "primary"
        service = self._build_service()
        raw = service.events().get(calendarId=cal_id, eventId=clean_id).execute()
        norm = normalize_google_event(raw, index=0, local_tz=tz.tzlocal())
        if norm is None:
            raise LookupError(f"Event '{clean_id}' was cancelled or could not be parsed.")
        return {
            "authenticated": True,
            "source": "live",
            "event": norm,
        }
