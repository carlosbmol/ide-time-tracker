# IDE Time Tracker

A lightweight Windows background tool that detects when you open or close your IDE and reminds you to log your hours in your time-tracking tool.

Built with Python — no GUI, no tray icon, no setup beyond a double-click installer.

---

## How it works

The tracker runs silently on startup and polls your running processes every 5 seconds using `psutil`.

**When you open a watched IDE** → a green popup appears and auto-dismisses after 8 seconds.

**When you close a watched IDE** → a red popup appears showing the exact session duration. It stays visible until you manually confirm it.

```
🔴 Visual Studio closed

Session time: 2h 34min
From 09:15 to 11:49

Don't forget to log your hours →
```

---

## Features

- Monitors Visual Studio and Android Studio out of the box (fully configurable)
- Calculates and displays session duration on close
- Handles edge cases: processes already open at startup, multiple IDEs running simultaneously
- Runs headlessly via `.pyw` (no console window)
- Auto-starts with Windows via Startup folder shortcut
- Single-file installer — no admin rights required

---

## Requirements

- Windows 10 / 11
- Python 3.10 or higher — [download](https://python.org)
- `psutil` (installed automatically by the installer)

---

## Installation

1. Download `ide_tracker.pyw` and `install_ide_tracker.bat` into the same folder
2. Double-click `install_ide_tracker.bat`
3. Done — the tracker starts immediately and will auto-launch on every reboot

The installer will:
- Detect your Python installation
- Install `psutil` if not already present
- Copy the script to `%APPDATA%\IdeTimeTracker\`
- Register a Startup shortcut in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`

---

## Configuration

Open `ide_tracker.pyw` and edit the two sections at the top of the file.

**Add or remove IDEs to monitor:**

```python
WATCHED_PROCESSES = {
    "devenv.exe":           "Visual Studio",
    "studio64.exe":         "Android Studio",
    "androidstudio64.exe":  "Android Studio",
    # "code.exe":           "VS Code",
    # "idea64.exe":         "IntelliJ IDEA",
    # "pycharm64.exe":      "PyCharm",
}
```

**Customize the notification messages:**

```python
OPEN_MESSAGE  = "Remember to start tracking your time\nwhen you begin working.\n\n⏱ Timer started!"
CLOSE_MESSAGE = "Don't forget to log your hours in\nyour time-tracking tool →"
```

After editing, re-run the installer to update the installed copy.

---

## Uninstall

Delete the Startup shortcut and the installed script:

```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\IdeTimeTracker.lnk
%APPDATA%\IdeTimeTracker\
```

---

## Finding your process name

If your IDE isn't listed above, find its process name via Task Manager → Details tab while the app is open.

---

## Tech stack

| | |
|---|---|
| Language | Python 3.10+ |
| Process monitoring | `psutil` |
| Notifications | `tkinter` |
| Installer | Windows Batch (`.bat`) + VBScript |

---

## License

MIT — free to use, modify, and distribute.
