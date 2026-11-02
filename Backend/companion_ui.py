"""
SpaceGlass — Companion Settings Interface & Task Action Dialogs (Backend/companion_ui.py).
Provides:
1. Full 4-tab Settings Window matching the SpaceGlass aesthetic:
   - GENERAL: Enable/disable individual widgets, right/top margins, startup with Windows,
              12/24-hour clock, Sunday/Monday week start, city & weather configuration.
   - APPEARANCE: Glass transparency slider, Blur intensity/mode (Acrylic/Blur/Mica/None),
                 corner radius, widget width, widget spacing, font size, and
                 Orange (#FF7A18) / Violet (#A66CDB) / Blue (#58A6FF) accent selector.
   - GOOGLE: Connect/Disconnect Google Account, connected status, Google Calendar ID,
             Google Tasks list selector, and Manual Sync button.
   - ADVANCED: Backend status, last sync time, Open Logs, and Reset Settings.
2. Quick Add-Task modal (`--action add-task`) for creating a real Google Task with title & due date.
3. Delete Task confirmation modal (`--action delete-task`) before calling `DELETE /api/tasks/{id}`.
4. Toggle Task completion helper (`--action toggle-task`) invoked by Rainmeter checkboxes.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Backend.config import ConfigManager, SpaceGlassSettings
from Backend.glass_effect import apply_win11_glass_to_hwnd

# SpaceGlass Palette for Tkinter UI
BG_DARK = "#1E1926"
BG_CARD = "#2A2334"
FG_PRIMARY = "#F5F3F7"
FG_MUTED = "#C5BECF"
ACCENT_ORANGE = "#FF7A18"
ACCENT_VIOLET = "#A66CDB"
ACCENT_BLUE = "#58A6FF"
DANGER_RED = "#FF6B6B"


def api_request(
    base_url: str,
    method: str,
    path: str,
    payload: Optional[Dict[str, Any]] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """Perform an HTTP request against the local SpaceGlass FastAPI backend."""
    url = f"{base_url.rstrip('/')}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as http_err:
        err_body = http_err.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(err_body)
            detail = parsed.get("detail", err_body)
            if isinstance(detail, dict):
                detail = detail.get("message", str(detail))
        except Exception:
            detail = err_body
        raise RuntimeError(f"HTTP {http_err.code}: {detail}") from http_err
    except Exception as exc:
        raise RuntimeError(f"Backend unreachable ({exc}). Ensure SpaceGlass backend is running.") from exc


def refresh_rainmeter_skins() -> None:
    """Ask Rainmeter to refresh active SpaceGlass skins if Rainmeter.exe is present."""
    if platform.system() != "Windows":
        return
    candidates = [
        Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "Rainmeter" / "Rainmeter.exe",
        Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "Rainmeter" / "Rainmeter.exe",
    ]
    for exe in candidates:
        if exe.exists():
            try:
                subprocess.Popen([str(exe), "!RefreshApp"], creationflags=0x08000000)
            except Exception:
                pass
            break


def run_cli_action(args: argparse.Namespace, cfg_mgr: ConfigManager) -> int:
    """Handle headless/dialog actions triggered directly from Rainmeter widget clicks."""
    base_url = f"http://{cfg_mgr.settings.host}:{cfg_mgr.settings.port}"

    if args.action == "sync":
        try:
            api_request(base_url, "POST", "/api/sync", timeout=30)
            refresh_rainmeter_skins()
            return 0
        except Exception as exc:
            _show_error_popup("SpaceGlass Sync Error", str(exc))
            return 1

    if args.action == "toggle-task":
        if not args.task_id:
            return 1
        encoded_id = urllib.parse.quote(args.task_id, safe="")
        try:
            api_request(
                base_url,
                "PATCH",
                f"/api/tasks/{encoded_id}",
                payload={"list_id": args.list_id or "@default", "status": args.status or "completed"},
            )
            refresh_rainmeter_skins()
            return 0
        except Exception as exc:
            _show_error_popup("Google Tasks Sync Failed", str(exc))
            return 1

    if args.action == "delete-task":
        if not args.task_id:
            return 1
        return _run_delete_confirmation_dialog(base_url, args.list_id or "@default", args.task_id, args.title or "this task")

    if args.action == "add-task":
        return _run_add_task_dialog(base_url, cfg_mgr.settings.selected_task_list_id)

    return 0


def _show_error_popup(title: str, message: str) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except Exception:
        sys.stderr.write(f"[{title}] {message}\n")


def _run_delete_confirmation_dialog(base_url: str, list_id: str, task_id: str, title: str) -> int:
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.withdraw()
    confirmed = messagebox.askyesno(
        "Delete Google Task",
        f"Are you sure you want to permanently delete '{title}' from Google Tasks?",
    )
    if confirmed:
        try:
            encoded_id = urllib.parse.quote(task_id, safe="")
            encoded_list = urllib.parse.quote(list_id, safe="")
            api_request(base_url, "DELETE", f"/api/tasks/{encoded_id}?list_id={encoded_list}")
            refresh_rainmeter_skins()
        except Exception as exc:
            messagebox.showerror("Delete Task Failed", str(exc))
            root.destroy()
            return 1
    root.destroy()
    return 0


def _run_add_task_dialog(base_url: str, default_list_id: str) -> int:
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.title("SpaceGlass — New Google Task")
    root.geometry("380x230")
    root.configure(bg=BG_DARK)
    root.resizable(False, False)

    root.update_idletasks()
    apply_win11_glass_to_hwnd(root.winfo_id(), blur_mode="Acrylic", alpha=180)

    tk.Label(
        root,
        text="Add New Task to Google Tasks",
        bg=BG_DARK,
        fg=FG_PRIMARY,
        font=("Segoe UI", 12, "bold"),
    ).pack(anchor="w", padx=20, pady=(16, 8))

    tk.Label(root, text="Task Title:", bg=BG_DARK, fg=FG_MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=20)
    title_var = tk.StringVar()
    title_entry = tk.Entry(
        root,
        textvariable=title_var,
        bg=BG_CARD,
        fg=FG_PRIMARY,
        insertbackground=FG_PRIMARY,
        relief="flat",
        font=("Segoe UI", 10),
    )
    title_entry.pack(fill="x", padx=20, pady=(2, 10), ipady=5)
    title_entry.focus_set()

    tk.Label(
        root,
        text="Due Date (Optional, YYYY-MM-DD):",
        bg=BG_DARK,
        fg=FG_MUTED,
        font=("Segoe UI", 9),
    ).pack(anchor="w", padx=20)
    due_var = tk.StringVar()
    due_entry = tk.Entry(
        root,
        textvariable=due_var,
        bg=BG_CARD,
        fg=FG_PRIMARY,
        insertbackground=FG_PRIMARY,
        relief="flat",
        font=("Segoe UI", 10),
    )
    due_entry.pack(fill="x", padx=20, pady=(2, 14), ipady=4)

    def on_submit(_event=None) -> None:
        t_val = title_var.get().strip()
        d_val = due_var.get().strip() or None
        if not t_val:
            messagebox.showwarning("Validation", "Please enter a task title.", parent=root)
            return
        try:
            api_request(
                base_url,
                "POST",
                "/api/tasks",
                payload={"title": t_val, "list_id": default_list_id, "due_date": d_val},
            )
            refresh_rainmeter_skins()
            root.destroy()
        except Exception as exc:
            messagebox.showerror("Unable to Add Task", str(exc), parent=root)

    btn_frame = tk.Frame(root, bg=BG_DARK)
    btn_frame.pack(fill="x", padx=20)

    tk.Button(
        btn_frame,
        text="Cancel",
        command=root.destroy,
        bg=BG_CARD,
        fg=FG_MUTED,
        relief="flat",
        padx=14,
        pady=5,
    ).pack(side="right", padx=(8, 0))

    tk.Button(
        btn_frame,
        text="Add Task",
        command=on_submit,
        bg=ACCENT_ORANGE,
        fg=FG_PRIMARY,
        activebackground="#E0650E",
        relief="flat",
        padx=16,
        pady=5,
    ).pack(side="right")

    root.bind("<Return>", on_submit)
    root.bind("<Escape>", lambda _e: root.destroy())
    root.mainloop()
    return 0


def launch_settings_window(cfg_mgr: ConfigManager, initial_tab: str = "general") -> None:
    """Launch the 4-tab SpaceGlass Settings GUI (General, Appearance, Google, Advanced)."""
    import tkinter as tk
    from tkinter import messagebox, ttk

    s = cfg_mgr.load()
    base_url = f"http://{s.host}:{s.port}"

    root = tk.Tk()
    root.title("SpaceGlass Settings — Your Universe. Your Schedule.")
    root.geometry("540x520")
    root.configure(bg=BG_DARK)
    root.resizable(False, False)

    root.update_idletasks()
    apply_win11_glass_to_hwnd(root.winfo_id(), blur_mode=s.blur_type, alpha=190)

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TNotebook", background=BG_DARK, borderwidth=0)
    style.configure(
        "TNotebook.Tab",
        background=BG_CARD,
        foreground=FG_MUTED,
        padding=(14, 7),
        font=("Segoe UI", 9, "bold"),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", ACCENT_ORANGE)],
        foreground=[("selected", FG_PRIMARY)],
    )

    header = tk.Frame(root, bg=BG_DARK)
    header.pack(fill="x", padx=20, pady=(14, 6))
    tk.Label(
        header,
        text="SPACEGLASS",
        bg=BG_DARK,
        fg=FG_PRIMARY,
        font=("Segoe UI", 14, "bold"),
    ).pack(side="left")
    tk.Label(
        header,
        text="  Your Universe. Your Schedule.",
        bg=BG_DARK,
        fg=FG_MUTED,
        font=("Segoe UI", 9),
    ).pack(side="left", pady=(4, 0))

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=20, pady=8)

    tab_general = tk.Frame(notebook, bg=BG_DARK, padx=16, pady=12)
    tab_appearance = tk.Frame(notebook, bg=BG_DARK, padx=16, pady=12)
    tab_google = tk.Frame(notebook, bg=BG_DARK, padx=16, pady=12)
    tab_advanced = tk.Frame(notebook, bg=BG_DARK, padx=16, pady=12)

    notebook.add(tab_general, text="GENERAL")
    notebook.add(tab_appearance, text="APPEARANCE")
    notebook.add(tab_google, text="GOOGLE")
    notebook.add(tab_advanced, text="ADVANCED")

    # --- TAB 1: GENERAL ---
    enable_clock_var = tk.BooleanVar(value=s.enable_clock)
    enable_cal_var = tk.BooleanVar(value=s.enable_calendar)
    enable_ev_var = tk.BooleanVar(value=s.enable_events)
    enable_tsk_var = tk.BooleanVar(value=s.enable_tasks)
    startup_var = tk.BooleanVar(value=s.start_with_windows)
    use24_var = tk.BooleanVar(value=s.use_24_hour)
    monday_var = tk.BooleanVar(value=s.week_start_monday)
    weather_var = tk.BooleanVar(value=s.weather_enabled)
    city_var = tk.StringVar(value=s.city_name)
    right_margin_var = tk.IntVar(value=s.right_margin)
    top_margin_var = tk.IntVar(value=s.top_margin)

    for text_lbl, var_obj in [
        ("Enable Clock & Weather Widget", enable_clock_var),
        ("Enable Monthly Calendar Widget", enable_cal_var),
        ("Enable Upcoming Events Widget", enable_ev_var),
        ("Enable Google Tasks Widget", enable_tsk_var),
        ("Start SpaceGlass automatically with Windows", startup_var),
        ("Use 24-hour clock format (19:30)", use24_var),
        ("Start calendar week on Monday (instead of Sunday)", monday_var),
        ("Enable live Weather display", weather_var),
    ]:
        tk.Checkbutton(
            tab_general,
            text=text_lbl,
            variable=var_obj,
            bg=BG_DARK,
            fg=FG_PRIMARY,
            selectcolor=BG_CARD,
            activebackground=BG_DARK,
            activeforeground=FG_PRIMARY,
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=2)

    row_city = tk.Frame(tab_general, bg=BG_DARK)
    row_city.pack(fill="x", pady=(8, 4))
    tk.Label(row_city, text="Weather City:", bg=BG_DARK, fg=FG_MUTED, width=18, anchor="w").pack(side="left")
    tk.Entry(row_city, textvariable=city_var, bg=BG_CARD, fg=FG_PRIMARY, relief="flat").pack(side="left", fill="x", expand=True)

    row_pos = tk.Frame(tab_general, bg=BG_DARK)
    row_pos.pack(fill="x", pady=4)
    tk.Label(row_pos, text="Right Margin (px):", bg=BG_DARK, fg=FG_MUTED, width=18, anchor="w").pack(side="left")
    tk.Spinbox(row_pos, from_=0, to=300, textvariable=right_margin_var, bg=BG_CARD, fg=FG_PRIMARY, width=8).pack(side="left")
    tk.Label(row_pos, text="  Top Margin (px):", bg=BG_DARK, fg=FG_MUTED).pack(side="left")
    tk.Spinbox(row_pos, from_=0, to=300, textvariable=top_margin_var, bg=BG_CARD, fg=FG_PRIMARY, width=8).pack(side="left")

    # --- TAB 2: APPEARANCE ---
    alpha_var = tk.IntVar(value=s.glass_alpha)
    blur_var = tk.StringVar(value=s.blur_type)
    radius_var = tk.IntVar(value=s.corner_radius)
    width_var = tk.IntVar(value=s.widget_width)
    gap_var = tk.IntVar(value=s.widget_gap)
    font_var = tk.IntVar(value=s.font_size_body)
    accent_var = tk.StringVar(value=s.accent_color)

    tk.Label(tab_appearance, text="Glass Transparency (Alpha 20–240):", bg=BG_DARK, fg=FG_MUTED).pack(anchor="w")
    tk.Scale(
        tab_appearance,
        from_=20,
        to=240,
        orient="horizontal",
        variable=alpha_var,
        bg=BG_DARK,
        fg=FG_PRIMARY,
        highlightthickness=0,
        troughcolor=BG_CARD,
    ).pack(fill="x", pady=(0, 8))

    row_blur = tk.Frame(tab_appearance, bg=BG_DARK)
    row_blur.pack(fill="x", pady=4)
    tk.Label(row_blur, text="Windows 11 Blur Mode:", bg=BG_DARK, fg=FG_MUTED, width=22, anchor="w").pack(side="left")
    ttk.Combobox(row_blur, textvariable=blur_var, values=["Acrylic", "Blur", "Mica", "None"], state="readonly").pack(side="left")

    for lbl_txt, spin_var, lo, hi in [
        ("Corner Radius (px):", radius_var, 8, 40),
        ("Widget Width (px):", width_var, 260, 480),
        ("Vertical Widget Spacing (px):", gap_var, 4, 48),
        ("Body Font Size (pt):", font_var, 8, 14),
    ]:
        r_frame = tk.Frame(tab_appearance, bg=BG_DARK)
        r_frame.pack(fill="x", pady=4)
        tk.Label(r_frame, text=lbl_txt, bg=BG_DARK, fg=FG_MUTED, width=22, anchor="w").pack(side="left")
        tk.Spinbox(r_frame, from_=lo, to=hi, textvariable=spin_var, bg=BG_CARD, fg=FG_PRIMARY, width=10).pack(side="left")

    row_acc = tk.Frame(tab_appearance, bg=BG_DARK)
    row_acc.pack(fill="x", pady=8)
    tk.Label(row_acc, text="Cosmic Accent Color:", bg=BG_DARK, fg=FG_MUTED, width=22, anchor="w").pack(side="left")
    for acc_name, acc_hex in [("orange", ACCENT_ORANGE), ("violet", ACCENT_VIOLET), ("blue", ACCENT_BLUE)]:
        tk.Radiobutton(
            row_acc,
            text=acc_name.capitalize(),
            value=acc_name,
            variable=accent_var,
            bg=BG_DARK,
            fg=acc_hex,
            selectcolor=BG_CARD,
            activebackground=BG_DARK,
        ).pack(side="left", padx=6)

    # --- TAB 3: GOOGLE ---
    google_status_lbl = tk.Label(
        tab_google,
        text="Checking Google connection status...",
        bg=BG_DARK,
        fg=FG_PRIMARY,
        font=("Segoe UI", 10, "bold"),
    )
    google_status_lbl.pack(anchor="w", pady=(4, 10))

    cal_id_var = tk.StringVar(value=s.selected_calendar_id)
    task_list_id_var = tk.StringVar(value=s.selected_task_list_id)

    def refresh_google_tab() -> None:
        try:
            st = api_request(base_url, "GET", "/api/status", timeout=5)
            is_auth = st.get("google_authenticated", False)
            has_creds = st.get("credentials_configured", False)
            if is_auth:
                google_status_lbl.config(text="● Connected to Google Calendar & Google Tasks", fg="#58D68D")
            elif has_creds:
                google_status_lbl.config(text="○ Disconnected (credentials.json ready)", fg=ACCENT_ORANGE)
            else:
                google_status_lbl.config(
                    text="○ Waiting for credentials.json in %LOCALAPPDATA%\\SpaceGlass",
                    fg=DANGER_RED,
                )
        except Exception as exc:
            google_status_lbl.config(text=f"○ Backend offline: {exc}", fg=DANGER_RED)

    def on_connect_google() -> None:
        try:
            api_request(base_url, "POST", "/api/google/connect", timeout=190)
            refresh_google_tab()
            refresh_rainmeter_skins()
            messagebox.showinfo("Connected", "Google Calendar and Google Tasks are now linked!", parent=root)
        except Exception as exc:
            messagebox.showerror("Google OAuth Error", str(exc), parent=root)

    def on_disconnect_google() -> None:
        try:
            api_request(base_url, "POST", "/api/google/disconnect", timeout=10)
            refresh_google_tab()
            refresh_rainmeter_skins()
        except Exception as exc:
            messagebox.showerror("Disconnect Error", str(exc), parent=root)

    def on_manual_sync() -> None:
        try:
            res = api_request(base_url, "POST", "/api/sync", timeout=30)
            refresh_rainmeter_skins()
            messagebox.showinfo(
                "Synchronization Complete",
                f"Synced {res.get('upcoming_events_count', 0)} upcoming events and "
                f"{res.get('active_tasks_count', 0)} active tasks.",
                parent=root,
            )
        except Exception as exc:
            messagebox.showerror("Sync Failed", str(exc), parent=root)

    btn_row_g = tk.Frame(tab_google, bg=BG_DARK)
    btn_row_g.pack(fill="x", pady=6)
    tk.Button(
        btn_row_g,
        text="Connect Google Account",
        command=on_connect_google,
        bg=ACCENT_ORANGE,
        fg=FG_PRIMARY,
        relief="flat",
        padx=12,
        pady=6,
    ).pack(side="left", padx=(0, 8))
    tk.Button(
        btn_row_g,
        text="Disconnect",
        command=on_disconnect_google,
        bg=BG_CARD,
        fg=FG_MUTED,
        relief="flat",
        padx=12,
        pady=6,
    ).pack(side="left", padx=(0, 8))
    tk.Button(
        btn_row_g,
        text="Sync Now",
        command=on_manual_sync,
        bg=ACCENT_BLUE,
        fg=FG_PRIMARY,
        relief="flat",
        padx=12,
        pady=6,
    ).pack(side="left")

    row_cal = tk.Frame(tab_google, bg=BG_DARK)
    row_cal.pack(fill="x", pady=(14, 4))
    tk.Label(row_cal, text="Google Calendar ID:", bg=BG_DARK, fg=FG_MUTED, width=20, anchor="w").pack(side="left")
    tk.Entry(row_cal, textvariable=cal_id_var, bg=BG_CARD, fg=FG_PRIMARY, relief="flat").pack(side="left", fill="x", expand=True)

    row_tl = tk.Frame(tab_google, bg=BG_DARK)
    row_tl.pack(fill="x", pady=4)
    tk.Label(row_tl, text="Google Tasks List ID:", bg=BG_DARK, fg=FG_MUTED, width=20, anchor="w").pack(side="left")
    tk.Entry(row_tl, textvariable=task_list_id_var, bg=BG_CARD, fg=FG_PRIMARY, relief="flat").pack(side="left", fill="x", expand=True)

    # --- TAB 4: ADVANCED ---
    adv_info_var = tk.StringVar(value="Querying backend health...")
    tk.Label(
        tab_advanced,
        textvariable=adv_info_var,
        bg=BG_DARK,
        fg=FG_PRIMARY,
        justify="left",
        font=("Consolas", 9),
    ).pack(anchor="w", pady=8)

    def refresh_advanced_tab() -> None:
        try:
            st = api_request(base_url, "GET", "/api/status", timeout=5)
            adv_info_var.set(
                f"Backend Status : {st.get('status', 'unknown')}\n"
                f"API Endpoint   : {base_url}\n"
                f"Uptime         : {st.get('uptime_seconds', 0)}s\n"
                f"Last Sync Time : {st.get('last_sync_time') or 'Never'}\n"
                f"Connectivity   : {st.get('api_connectivity')}\n"
                f"Log File       : {cfg_mgr.log_path}"
            )
        except Exception as exc:
            adv_info_var.set(f"Backend Status : Offline\nReason         : {exc}")

    def on_open_logs() -> None:
        if cfg_mgr.log_path.exists():
            if platform.system() == "Windows":
                os.startfile(str(cfg_mgr.log_path))  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["xdg-open", str(cfg_mgr.log_path)])
        else:
            messagebox.showinfo("Logs", f"No log file created yet at {cfg_mgr.log_path}", parent=root)

    def on_reset_defaults() -> None:
        if messagebox.askyesno("Reset Settings", "Restore all SpaceGlass settings to factory defaults?", parent=root):
            cfg_mgr.reset_to_defaults()
            refresh_rainmeter_skins()
            root.destroy()

    adv_btns = tk.Frame(tab_advanced, bg=BG_DARK)
    adv_btns.pack(fill="x", pady=12)
    tk.Button(adv_btns, text="Open Logs", command=on_open_logs, bg=BG_CARD, fg=FG_PRIMARY, relief="flat", padx=12, pady=6).pack(side="left", padx=(0, 8))
    tk.Button(adv_btns, text="Refresh Status", command=refresh_advanced_tab, bg=BG_CARD, fg=FG_PRIMARY, relief="flat", padx=12, pady=6).pack(side="left", padx=(0, 8))
    tk.Button(adv_btns, text="Reset to Defaults", command=on_reset_defaults, bg=DANGER_RED, fg=FG_PRIMARY, relief="flat", padx=12, pady=6).pack(side="left")

    # Save Footer
    footer = tk.Frame(root, bg=BG_DARK)
    footer.pack(fill="x", padx=20, pady=(4, 14))

    def on_save_all() -> None:
        updated = SpaceGlassSettings(
            enable_clock=enable_clock_var.get(),
            enable_calendar=enable_cal_var.get(),
            enable_events=enable_ev_var.get(),
            enable_tasks=enable_tsk_var.get(),
            start_with_windows=startup_var.get(),
            use_24_hour=use24_var.get(),
            week_start_monday=monday_var.get(),
            weather_enabled=weather_var.get(),
            city_name=city_var.get().strip() or "Nagpur",
            right_margin=right_margin_var.get(),
            top_margin=top_margin_var.get(),
            glass_alpha=alpha_var.get(),
            blur_type=blur_var.get(),
            corner_radius=radius_var.get(),
            widget_width=width_var.get(),
            widget_gap=gap_var.get(),
            font_size_body=font_var.get(),
            accent_color=accent_var.get(),
            selected_calendar_id=cal_id_var.get().strip() or "primary",
            selected_task_list_id=task_list_id_var.get().strip() or "@default",
        )
        cfg_mgr.save(updated)
        try:
            api_request(base_url, "PUT", "/api/settings", payload=updated.model_dump(), timeout=5)
        except Exception:
            pass
        refresh_rainmeter_skins()
        messagebox.showinfo("Saved", "SpaceGlass settings saved and applied to widgets.", parent=root)

    tk.Button(
        footer,
        text="Save & Apply",
        command=on_save_all,
        bg=ACCENT_ORANGE,
        fg=FG_PRIMARY,
        relief="flat",
        padx=18,
        pady=6,
        font=("Segoe UI", 9, "bold"),
    ).pack(side="right")

    tab_map = {"general": 0, "appearance": 1, "google": 2, "advanced": 3}
    notebook.select(tab_map.get(initial_tab.lower(), 0))
    refresh_google_tab()
    refresh_advanced_tab()
    root.mainloop()


def main() -> int:
    parser = argparse.ArgumentParser(description="SpaceGlass Settings & Companion UI")
    parser.add_argument("--tab", default="general", choices=["general", "appearance", "google", "advanced"])
    parser.add_argument("--action", default=None, choices=["sync", "add-task", "toggle-task", "delete-task"])
    parser.add_argument("--list-id", default="@default")
    parser.add_argument("--task-id", default=None)
    parser.add_argument("--status", default="completed")
    parser.add_argument("--title", default="")
    args = parser.parse_args()

    cfg_mgr = ConfigManager()
    if args.action:
        return run_cli_action(args, cfg_mgr)
    launch_settings_window(cfg_mgr, initial_tab=args.tab)
    return 0


if __name__ == "__main__":
    sys.exit(main())
