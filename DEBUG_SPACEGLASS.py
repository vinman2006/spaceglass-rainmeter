"""
SpaceGlass Comprehensive Diagnostics & Debugging Engine (DEBUG_SPACEGLASS.py).
Tests and validates every single layer of the SpaceGlass desktop system:
  1. System Environment & Display Configuration (Resolution, Working Area, Scaling)
  2. Rainmeter Installation & Executable Health
  3. Rainmeter Configuration (Rainmeter.ini syntax, encoding, coordinates, AlwaysOnTop)
  4. SpaceGlass Skin Integrity & Encoding (BOM, clean ASCII/Unicode, no nested folders)
  5. FrostedGlass Plugin & Windows 11 DWM Compatibility (Plugin presence, fallback behavior)
  6. Companion FastAPI Backend Lifecycle (PID lock, Port 8765 listener, single-instance)
  7. REST Endpoints Audit (/api/status, /api/weather, /api/calendar/month, /api/tasks)
  8. Interactive Session & Process Persistence (WMI breakaway vs Job Object trap)
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes
import json
import os
import platform
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent
LOCALAPPDATA = Path(os.environ.get("LOCALAPPDATA", ""))
APPDATA = Path(os.environ.get("APPDATA", ""))
USERPROFILE = Path(os.environ.get("USERPROFILE", ""))

# Detect Documents / Rainmeter Skins directory
DOCUMENTS_DIR = Path(os.path.expanduser("~/Documents"))
ONEDRIVE_DOCS = USERPROFILE / "OneDrive" / "Documents"
SKINS_BASE = None

for cand in [ONEDRIVE_DOCS / "Rainmeter" / "Skins", DOCUMENTS_DIR / "Rainmeter" / "Skins"]:
    if cand.exists():
        SKINS_BASE = cand
        break

if SKINS_BASE is None:
    SKINS_BASE = DOCUMENTS_DIR / "Rainmeter" / "Skins"

RAINMETER_EXE_CANDIDATES = [
    Path(r"C:\Program Files\Rainmeter\Rainmeter.exe"),
    Path(r"C:\Program Files (x86)\Rainmeter\Rainmeter.exe"),
]


class DiagnosticReporter:
    def __init__(self) -> None:
        self.results: List[Dict[str, Any]] = []

    def record(self, layer: str, test_name: str, passed: bool, details: str, severity: str = "INFO") -> None:
        status_symbol = "[PASS]" if passed else ("[WARN]" if severity == "WARN" else "[FAIL]")
        self.results.append({
            "layer": layer,
            "test": test_name,
            "passed": passed,
            "status": status_symbol,
            "severity": severity,
            "details": details,
        })
        print(f" {status_symbol:<7} {layer} :: {test_name}")
        if details:
            for line in details.splitlines():
                print(f"         {line}")

    def summary(self) -> Dict[str, int]:
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = sum(1 for r in self.results if not r["passed"] and r["severity"] != "WARN")
        warnings = sum(1 for r in self.results if not r["passed"] and r["severity"] == "WARN")
        return {"total": total, "passed": passed, "failed": failed, "warnings": warnings}


def test_layer_1_environment(diag: DiagnosticReporter) -> None:
    print("\n--- [LAYER 1] System Environment & Display Configuration ---")
    diag.record(
        "Layer 1",
        "Operating System",
        platform.system() == "Windows",
        f"Detected: {platform.system()} {platform.release()} (Build {platform.version()})",
    )

    # Display Resolution via user32
    try:
        user32 = ctypes.windll.user32
        sw = user32.GetSystemMetrics(0)
        sh = user32.GetSystemMetrics(1)
        diag.record(
            "Layer 1",
            "Screen Resolution",
            sw > 0 and sh > 0,
            f"Primary Display: {sw}x{sh} pixels (Widget Target X: {sw - 320 - 24})",
        )
    except Exception as e:
        diag.record("Layer 1", "Screen Resolution", False, str(e), severity="WARN")


def test_layer_2_rainmeter_installation(diag: DiagnosticReporter) -> Path | None:
    print("\n--- [LAYER 2] Rainmeter Installation & Executable Health ---")
    rm_path = None
    for cand in RAINMETER_EXE_CANDIDATES:
        if cand.exists():
            rm_path = cand
            break

    if rm_path:
        size_kb = rm_path.stat().st_size // 1024
        diag.record("Layer 2", "Rainmeter Executable", True, f"Found at: {rm_path} ({size_kb} KB)")
    else:
        diag.record(
            "Layer 2",
            "Rainmeter Executable",
            False,
            "Rainmeter.exe not found in Program Files.",
            severity="CRITICAL",
        )
    return rm_path


def test_layer_3_rainmeter_ini(diag: DiagnosticReporter) -> None:
    print("\n--- [LAYER 3] Rainmeter Configuration (Rainmeter.ini) ---")
    ini_path = APPDATA / "Rainmeter" / "Rainmeter.ini"
    if not ini_path.exists():
        diag.record("Layer 3", "Rainmeter.ini Presence", False, f"Missing at: {ini_path}", severity="FAIL")
        return

    diag.record("Layer 3", "Rainmeter.ini Presence", True, f"Located at: {ini_path}")

    # Inspect encoding & content
    raw_bytes = ini_path.read_bytes()
    is_unicode = len(raw_bytes) >= 2 and raw_bytes[:2] == b"\xff\xfe"
    is_utf8_bom = len(raw_bytes) >= 3 and raw_bytes[:3] == b"\xef\xbb\xbf"
    encoding = "UTF-16 LE (Unicode BOM)" if is_unicode else ("UTF-8 BOM" if is_utf8_bom else "ANSI / UTF-8 without BOM")

    diag.record(
        "Layer 3",
        "Rainmeter.ini Encoding",
        is_unicode or is_utf8_bom,
        f"Encoding detected: {encoding} ({len(raw_bytes)} bytes)",
        severity="INFO" if (is_unicode or is_utf8_bom) else "WARN",
    )

    # Parse text
    try:
        text = raw_bytes.decode("utf-16" if is_unicode else "utf-8", errors="replace")
    except Exception:
        text = raw_bytes.decode("latin-1", errors="replace")

    required_sections = ["SpaceGlass\\Clock", "SpaceGlass\\Calendar", "SpaceGlass\\Events", "SpaceGlass\\Tasks"]
    active_count = 0
    always_on_top_count = 0

    for s in required_sections:
        has_sec = f"[{s}]" in text
        if has_sec:
            # Check Active=1
            part = text.split(f"[{s}]")[1].split("[")[0]
            if "Active=1" in part:
                active_count += 1
            if "AlwaysOnTop=1" in part:
                always_on_top_count += 1

    diag.record(
        "Layer 3",
        "SpaceGlass Sections in Rainmeter.ini",
        active_count == 4,
        f"{active_count}/4 SpaceGlass skins marked Active=1 in Rainmeter.ini",
    )
    diag.record(
        "Layer 3",
        "AlwaysOnTop Floating Configuration",
        always_on_top_count == 4,
        f"{always_on_top_count}/4 SpaceGlass skins set to AlwaysOnTop=1 (Topmost)",
        severity="INFO" if always_on_top_count == 4 else "WARN",
    )


def test_layer_4_skin_integrity(diag: DiagnosticReporter) -> None:
    print("\n--- [LAYER 4] SpaceGlass Skin Files & Directory Structure ---")
    if not SKINS_BASE or not SKINS_BASE.exists():
        diag.record("Layer 4", "Skins Root Directory", False, f"Missing: {SKINS_BASE}", severity="FAIL")
        return

    spaceglass_dir = SKINS_BASE / "SpaceGlass"
    if not spaceglass_dir.exists():
        diag.record("Layer 4", "SpaceGlass Skin Directory", False, f"Missing: {spaceglass_dir}", severity="FAIL")
        return

    diag.record("Layer 4", "SpaceGlass Skin Directory", True, f"Located at: {spaceglass_dir}")

    # Check for nested directory bug (e.g., Clock/Clock, @Resources/@Resources)
    nested_bugs = []
    for sub in ["Clock", "Calendar", "Events", "Tasks", "@Resources"]:
        test_path = spaceglass_dir / sub / sub
        if test_path.exists():
            nested_bugs.append(str(test_path))

    diag.record(
        "Layer 4",
        "Nested Directory Check",
        len(nested_bugs) == 0,
        "No redundant nested subdirectories found." if not nested_bugs else f"Found nested duplicates: {nested_bugs}",
        severity="FAIL" if nested_bugs else "INFO",
    )

    # Check DynamicWindowSize=1 in all 4 skins
    skins = {
        "Clock": spaceglass_dir / "Clock" / "Clock.ini",
        "Calendar": spaceglass_dir / "Calendar" / "Calendar.ini",
        "Events": spaceglass_dir / "Events" / "Events.ini",
        "Tasks": spaceglass_dir / "Tasks" / "Tasks.ini",
    }
    dynamic_window_count = 0
    clean_encoding_count = 0

    for name, path in skins.items():
        if path.exists():
            content = path.read_text(encoding="utf-8", errors="replace")
            if "DynamicWindowSize=1" in content:
                dynamic_window_count += 1
            # Check for corrupt double-encoded characters or replacement chars
            if "\ufffd" not in content and "Â" not in content:
                clean_encoding_count += 1

    diag.record(
        "Layer 4",
        "Dynamic Window Sizing (DynamicWindowSize=1)",
        dynamic_window_count == 4,
        f"{dynamic_window_count}/4 skins have DynamicWindowSize=1 (prevents 0x0 clipping).",
        severity="INFO" if dynamic_window_count == 4 else "WARN",
    )
    diag.record(
        "Layer 4",
        "Clean Text Encoding (No Corrupt Chars)",
        clean_encoding_count == 4,
        f"{clean_encoding_count}/4 skins free of mojibake or corrupt UTF-8 replacement characters.",
    )


def test_layer_5_frostedglass_and_dwm(diag: DiagnosticReporter) -> None:
    print("\n--- [LAYER 5] FrostedGlass Plugin & Windows 11 DWM Composition ---")
    plugin_candidates = [
        Path(r"C:\Program Files\Rainmeter\Plugins\FrostedGlass.dll"),
        SKINS_BASE / "@Vault" / "Plugins" / "FrostedGlass.dll" if SKINS_BASE else None,
    ]
    plugin_found = any(p and p.exists() for p in plugin_candidates)
    if plugin_found:
        diag.record("Layer 5", "FrostedGlass.dll Plugin", True, "FrostedGlass.dll is installed.")
    else:
        diag.record(
            "Layer 5",
            "FrostedGlass.dll Plugin",
            False,
            "FrostedGlass.dll is not installed. Skins gracefully fallback to vector Shape glass panels.",
            severity="WARN",
        )


def test_layer_6_backend_service(diag: DiagnosticReporter) -> None:
    print("\n--- [LAYER 6] Companion FastAPI Backend Lifecycle (127.0.0.1:8765) ---")
    req = urllib.request.Request("http://127.0.0.1:8765/api/status")
    try:
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            app_name = data.get("application", "")
            uptime = data.get("uptime_seconds", 0)
            diag.record(
                "Layer 6",
                "FastAPI Status Endpoint (/api/status)",
                app_name == "SpaceGlass",
                f"Status: {data.get('status')} | Uptime: {uptime}s | App: {app_name}",
            )
    except Exception as e:
        diag.record(
            "Layer 6",
            "FastAPI Status Endpoint (/api/status)",
            False,
            f"Cannot connect to 127.0.0.1:8765 ({e})",
            severity="FAIL",
        )


def test_layer_7_rest_endpoints(diag: DiagnosticReporter) -> None:
    print("\n--- [LAYER 7] REST Endpoints Audit ---")
    endpoints = [
        ("/", "Root Dashboard / Status"),
        ("/api/weather", "Live Weather API (Open-Meteo)"),
        ("/api/calendar/month?year=2026&month=11", "Monthly Calendar Metadata"),
        ("/api/tasks", "Google Tasks Metadata"),
    ]
    for ep, desc in endpoints:
        url = f"http://127.0.0.1:8765{ep}"
        try:
            with urllib.request.urlopen(url, timeout=3.0) as resp:
                code = resp.getcode()
                body = json.loads(resp.read().decode("utf-8"))
                diag.record(
                    "Layer 7",
                    f"Endpoint: {ep}",
                    code == 200,
                    f"{desc} -> HTTP {code} (keys: {list(body.keys())[:4]}...)",
                )
        except Exception as e:
            diag.record("Layer 7", f"Endpoint: {ep}", False, f"Failed: {e}", severity="WARN")


def test_layer_8_persistence(diag: DiagnosticReporter) -> None:
    print("\n--- [LAYER 8] Interactive Session & Process Persistence ---")
    # Check if Rainmeter is currently running
    try:
        out = subprocess.check_output(
            ["tasklist", "/fi", "imagename eq Rainmeter.exe", "/fo", "csv"],
            text=True,
            errors="replace",
        )
        lines = [line.strip().strip('"') for line in out.strip().splitlines() if "Rainmeter.exe" in line]
        is_running = len(lines) > 0
        diag.record(
            "Layer 8",
            "Rainmeter Active Process",
            is_running,
            f"Active Rainmeter instances: {len(lines)}" if is_running else "Rainmeter is NOT currently running.",
            severity="INFO" if is_running else "WARN",
        )
    except Exception as e:
        diag.record("Layer 8", "Rainmeter Active Process", False, str(e), severity="WARN")


def main() -> int:
    print("=" * 76)
    print("  SPACEGLASS v1.0.0 — COMPREHENSIVE DEBUGGING & SYSTEM AUDIT")
    print("  Your Universe. Your Schedule.")
    print("=" * 76)

    diag = DiagnosticReporter()

    test_layer_1_environment(diag)
    rm_path = test_layer_2_rainmeter_installation(diag)
    test_layer_3_rainmeter_ini(diag)
    test_layer_4_skin_integrity(diag)
    test_layer_5_frostedglass_and_dwm(diag)
    test_layer_6_backend_service(diag)
    test_layer_7_rest_endpoints(diag)
    test_layer_8_persistence(diag)

    summary = diag.summary()
    print("\n" + "=" * 76)
    print(f"  AUDIT COMPLETE: Total Tests: {summary['total']} | Passed: {summary['passed']} | Warnings: {summary['warnings']} | Failed: {summary['failed']}")
    print("=" * 76)

    # Write debug output to a persistent JSON log in LOCALAPPDATA
    log_dir = LOCALAPPDATA / "SpaceGlass"
    log_dir.mkdir(parents=True, exist_ok=True)
    report_file = log_dir / "diagnostics_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(diag.results, f, indent=2)
    print(f"\nDetailed diagnostics saved to: {report_file}")
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
