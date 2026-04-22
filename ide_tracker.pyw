"""
IDE Time Tracker
Detects when you open/close your IDE(s) and shows popup reminders
to log your hours in your time-tracking tool.

Requirements:
    pip install psutil

Usage:
    python ide_time_tracker.pyw

To run automatically on Windows startup:
    Add a shortcut to this script in:
    C:\\Users\\<YourUser>\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup
    (the installer script handles this automatically)
"""

import psutil
import time
import tkinter as tk
from tkinter import font as tkfont
from datetime import datetime
import threading
import sys

# ── Processes to monitor ────────────────────────────────────────────────────
# Add or remove entries as needed.
# Key   → executable name (lowercase)
# Value → display name shown in the popup
WATCHED_PROCESSES = {
    "devenv.exe":           "Visual Studio",
    "studio64.exe":         "Android Studio",
    "androidstudio64.exe":  "Android Studio",
    # "code.exe":           "VS Code",       # uncomment to add VS Code
    # "idea64.exe":         "IntelliJ IDEA", # uncomment to add IntelliJ
    # "pycharm64.exe":      "PyCharm",        # uncomment to add PyCharm
}

# ── Notification text ────────────────────────────────────────────────────────
# Customize these messages to match your time-tracking tool or workflow.
OPEN_MESSAGE  = "Remember to start tracking your time\nwhen you begin working.\n\n⏱ Timer started!"
CLOSE_MESSAGE = "Don't forget to log your hours in\nyour time-tracking tool →"

# ── Internal state ───────────────────────────────────────────────────────────
active_sessions: dict[str, datetime] = {}  # process name → session start time
_lock = threading.Lock()


# ── Popups ───────────────────────────────────────────────────────────────────

def show_popup(title: str, message: str, color: str = "#2563EB", auto_close: int = 0):
    """
    Display a centered popup window.
    auto_close: seconds before auto-dismiss (0 = manual close required).
    """

    def _run():
        root = tk.Tk()
        root.withdraw()

        win = tk.Toplevel(root)
        win.title(title)
        win.configure(bg="#1E1E2E")
        win.resizable(False, False)
        win.attributes("-topmost", True)

        # Position: bottom-right corner
        win.update_idletasks()
        w, h = 420, 220
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        win.geometry(f"{w}x{h}+{(sw - w) // 2}+{sh - h - 60}")

        # Colored top bar
        tk.Frame(win, bg=color, height=6).pack(fill="x")

        # Title label
        title_font = tkfont.Font(family="Segoe UI", size=13, weight="bold")
        tk.Label(win, text=title, font=title_font,
                 bg="#1E1E2E", fg="white").pack(pady=(18, 4))

        # Message label
        msg_font = tkfont.Font(family="Segoe UI", size=10)
        tk.Label(win, text=message, font=msg_font,
                 bg="#1E1E2E", fg="#CBD5E1",
                 wraplength=360, justify="center").pack(pady=(0, 16))

        # Dismiss button
        btn_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        tk.Button(
            win, text="Got it ✓",
            font=btn_font,
            bg=color, fg="white",
            relief="flat", padx=20, pady=6,
            cursor="hand2",
            command=lambda: (win.destroy(), root.destroy())
        ).pack()

        if auto_close > 0:
            win.after(auto_close * 1000, lambda: (win.destroy(), root.destroy()))

        root.mainloop()

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join()


def notify_open(app_name: str):
    """Green popup shown when a watched process starts."""
    show_popup(
        title=f"🟢 {app_name} opened",
        message=OPEN_MESSAGE,
        color="#16A34A",
        auto_close=8  # auto-dismisses after 8 seconds
    )


def notify_close(app_name: str, start_time: datetime):
    """
    Red popup shown when a watched process exits.
    Displays total session duration and stays visible until manually dismissed.
    """
    elapsed       = datetime.now() - start_time
    total_minutes = int(elapsed.total_seconds() / 60)
    hours, minutes = divmod(total_minutes, 60)

    duration_str = f"{hours}h {minutes:02d}min" if hours > 0 else f"{minutes} minutes"
    start_str    = start_time.strftime("%H:%M")
    end_str      = datetime.now().strftime("%H:%M")

    show_popup(
        title=f"🔴 {app_name} closed",
        message=(
            f"Session time: {duration_str}\n"
            f"From {start_str} to {end_str}\n\n"
            f"{CLOSE_MESSAGE}"
        ),
        color="#DC2626",
        auto_close=0  # stays open until user clicks "Got it"
    )


# ── Process monitor ──────────────────────────────────────────────────────────

def get_running_watched() -> set[str]:
    """Return the set of watched process names currently running."""
    running = set()
    try:
        for proc in psutil.process_iter(["name"]):
            name = (proc.info["name"] or "").lower()
            if name in WATCHED_PROCESSES:
                running.add(name)
    except Exception:
        pass
    return running


def monitor_loop():
    print("IDE Time Tracker running... (Ctrl+C to stop)")
    print(f"Watching: {', '.join(WATCHED_PROCESSES.values())}\n")

    # Handle processes that were already open when the tracker started
    previously_running: set[str] = get_running_watched()
    for proc in previously_running:
        with _lock:
            active_sessions[proc] = datetime.now()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ALREADY OPEN: {WATCHED_PROCESSES[proc]}")

    while True:
        currently_running = get_running_watched()

        # Newly opened processes
        for proc in (currently_running - previously_running):
            with _lock:
                active_sessions[proc] = datetime.now()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] OPENED: {WATCHED_PROCESSES[proc]}")
            threading.Thread(target=notify_open,
                             args=(WATCHED_PROCESSES[proc],), daemon=True).start()

        # Newly closed processes
        for proc in (previously_running - currently_running):
            with _lock:
                start_time = active_sessions.pop(proc, None)
            if start_time:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] CLOSED: {WATCHED_PROCESSES[proc]}")
                threading.Thread(target=notify_close,
                                 args=(WATCHED_PROCESSES[proc], start_time), daemon=True).start()

        previously_running = currently_running
        time.sleep(5)  # poll interval in seconds


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        monitor_loop()
    except KeyboardInterrupt:
        print("\nIDE Time Tracker stopped.")
        sys.exit(0)
