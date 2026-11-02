"""
SpaceGlass — Windows 11 DWM Acrylic / Mica & FrostedGlass Composition Engine (Backend/glass_effect.py).

Architectural Overview & Documented Limitations:
1. Rainmeter's standard `SolidColor` only produces an alpha-blended flat rectangle without
   real Gaussian backdrop blur.
2. To achieve authentic Apple-inspired frosted glassmorphism on Windows 11 where the orange
   nebula wallpaper blurs softly behind each floating widget panel, SpaceGlass combines two
   complementary Windows composition layers:
   a) Rainmeter's `FrostedGlass` plugin (`Measure=Plugin`, `Plugin=FrostedGlass`, `Type=Acrylic`,
      `Corner=Round`, `Backdrop=Dark`) inside every `.ini` skin.
   b) Direct Windows 11 DWM / User32 composition API calls in this module (`DwmSetWindowAttribute`
      with `DWMWA_WINDOW_CORNER_PREFERENCE = 33`, `DWMWA_SYSTEMBACKDROP_TYPE = 38`, and
      `SetWindowCompositionAttribute` with `ACCENT_ENABLE_ACRYLICBLURBEHIND = 4`), which can be
      applied to any top-level `HWND` (both Rainmeter skin windows and the SpaceGlass Settings window).
3. Known Windows 11 DWM Limitations:
   - Windows 11 disables DWM Acrylic blur automatically when Battery Saver / Energy Saver is active
     or when "Transparency effects" is turned off in Windows Settings > Personalization > Colors.
   - `ACCENT_ENABLE_ACRYLICBLURBEHIND` on Win32 desktop child windows can exhibit slight lag if
     dragged rapidly on older WDDM drivers; `FrostedGlass` with `Corner=Round` or `Type=Blur`
     can be toggled in SpaceGlass Settings > Appearance if the user prefers lighter GPU usage.
"""
from __future__ import annotations

import ctypes
import logging
import platform
from typing import List

logger = logging.getLogger("spaceglass.glass")

# Windows 11 DWM constants
DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWA_SYSTEMBACKDROP_TYPE = 38

DWMWCP_DEFAULT = 0
DWMWCP_DONOTROUND = 1
DWMWCP_ROUND = 2
DWMWCP_ROUNDSMALL = 3

# AccentState values for SetWindowCompositionAttribute
ACCENT_DISABLED = 0
ACCENT_ENABLE_BLURBEHIND = 3
ACCENT_ENABLE_ACRYLICBLURBEHIND = 4

WCA_ACCENT_POLICY = 19


class ACCENT_POLICY(ctypes.Structure):
    _fields_ = [
        ("AccentState", ctypes.c_int),
        ("AccentFlags", ctypes.c_int),
        ("GradientColor", ctypes.c_uint32),  # AABBGGRR
        ("AnimationId", ctypes.c_int),
    ]


class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
    _fields_ = [
        ("Attrib", ctypes.c_int),
        ("pvData", ctypes.c_void_p),
        ("cbData", ctypes.c_size_t),
    ]


def _abgr_hex(r: int, g: int, b: int, alpha: int) -> int:
    """Pack RGBA (0..255) into Windows 32-bit AABBGGRR unsigned int."""
    a = max(1, min(255, int(alpha)))
    return (a << 24) | ((b & 0xFF) << 16) | ((g & 0xFF) << 8) | (r & 0xFF)


def apply_win11_glass_to_hwnd(
    hwnd: int,
    blur_mode: str = "Acrylic",
    alpha: int = 95,
    tint_rgb: tuple[int, int, int] = (35, 30, 42),
    round_corners: bool = True,
) -> bool:
    """
    Apply Windows 11 DWM rounded corners, dark mode border, and Acrylic/Blur composition
    to a native Win32 window handle (HWND). Safe no-op on non-Windows platforms.
    """
    if platform.system() != "Windows" or not hwnd:
        return False

    try:
        dwmapi = ctypes.windll.dwmapi
        user32 = ctypes.windll.user32

        # 1. Enable immersive dark mode frame
        dark_val = ctypes.c_int(1)
        dwmapi.DwmSetWindowAttribute(
            ctypes.c_void_p(hwnd),
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(dark_val),
            ctypes.sizeof(dark_val),
        )

        # 2. Request native Windows 11 rounded window corners (prevents rectangular blur bleed)
        corner_pref = ctypes.c_int(DWMWCP_ROUND if round_corners else DWMWCP_DONOTROUND)
        dwmapi.DwmSetWindowAttribute(
            ctypes.c_void_p(hwnd),
            DWMWA_WINDOW_CORNER_PREFERENCE,
            ctypes.byref(corner_pref),
            ctypes.sizeof(corner_pref),
        )

        # 3. Apply AccentPolicy via SetWindowCompositionAttribute
        mode_norm = (blur_mode or "Acrylic").strip().lower()
        if mode_norm == "none":
            accent_state = ACCENT_DISABLED
        elif mode_norm == "blur":
            accent_state = ACCENT_ENABLE_BLURBEHIND
        else:
            accent_state = ACCENT_ENABLE_ACRYLICBLURBEHIND

        r, g, b = tint_rgb
        policy = ACCENT_POLICY()
        policy.AccentState = accent_state
        policy.AccentFlags = 2
        policy.GradientColor = _abgr_hex(r, g, b, alpha)
        policy.AnimationId = 0

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attrib = WCA_ACCENT_POLICY
        data.pvData = ctypes.cast(ctypes.byref(policy), ctypes.c_void_p)
        data.cbData = ctypes.sizeof(policy)

        set_wca = getattr(user32, "SetWindowCompositionAttribute", None)
        if set_wca is not None:
            set_wca(ctypes.c_void_p(hwnd), ctypes.byref(data))
        return True
    except Exception as exc:
        logger.debug("DWM glass attribute call skipped for HWND %s: %s", hwnd, exc)
        return False


def refresh_rainmeter_glass_windows(blur_mode: str = "Acrylic", alpha: int = 95) -> int:
    """
    Enumerate top-level Rainmeter meter windows (`RainmeterMeterWindow`) on Windows 11
    and apply DWM rounded corners + Acrylic backdrop blur.
    """
    if platform.system() != "Windows":
        return 0

    applied_count = 0
    try:
        user32 = ctypes.windll.user32
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        matched_hwnds: List[int] = []

        def _enum_cb(hwnd: int, _lparam: int) -> bool:
            if user32.IsWindowVisible(hwnd):
                buf = ctypes.create_unicode_buffer(128)
                user32.GetClassNameW(hwnd, buf, 128)
                if buf.value == "RainmeterMeterWindow":
                    matched_hwnds.append(hwnd)
            return True

        cb_func = WNDENUMPROC(_enum_cb)
        user32.EnumWindows(cb_func, 0)

        # RainmeterMeterWindow handles its own vector rounded corners via [MeterShape].
        # Applying rectangular DWM acrylic blur to RainmeterMeterWindow causes dark rectangular
        # corner bleeding outside the rounded 18px corners. We set ACCENT_DISABLED on Rainmeter.
        for hwnd in matched_hwnds:
            if apply_win11_glass_to_hwnd(hwnd, blur_mode="none", alpha=0):
                applied_count += 1
    except Exception as exc:
        logger.debug("Rainmeter window enumeration skipped: %s", exc)
    return applied_count
