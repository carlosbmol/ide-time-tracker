@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   IDE Time Tracker - Installer
echo ============================================
echo.

:: ── Locate Python ────────────────────────────────────────────────────────────
set PYTHON_EXE=

:: First, check if pythonw.exe is available on PATH
for %%p in (pythonw.exe) do (
    where %%p >nul 2>&1
    if !errorlevel! == 0 (
        set PYTHON_EXE=%%p
    )
)

:: If not found on PATH, try common installation directories
if "%PYTHON_EXE%"=="" (
    for %%d in (
        "%LOCALAPPDATA%\Programs\Python\Python313\pythonw.exe"
        "%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe"
        "%LOCALAPPDATA%\Programs\Python\Python311\pythonw.exe"
        "%LOCALAPPDATA%\Programs\Python\Python310\pythonw.exe"
        "C:\Python313\pythonw.exe"
        "C:\Python312\pythonw.exe"
    ) do (
        if exist %%d set PYTHON_EXE=%%~d
    )
)

if "%PYTHON_EXE%"=="" (
    echo ERROR: Python not found. Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Python found: %PYTHON_EXE%
echo.

:: ── Install psutil if missing ─────────────────────────────────────────────────
echo Checking dependencies...
"%PYTHON_EXE%" -c "import psutil" >nul 2>&1
if errorlevel 1 (
    echo Installing psutil...
    pip install psutil
    if errorlevel 1 (
        echo ERROR: Could not install psutil. Run manually: pip install psutil
        pause
        exit /b 1
    )
)
echo psutil OK
echo.

:: ── Copy script to AppData ────────────────────────────────────────────────────
:: We copy the script out of its original folder so it works even if you
:: move or delete the source directory later.
set SCRIPT_SRC=%~dp0ide_tracker.pyw
set INSTALL_DIR=%APPDATA%\IdeTimeTracker
set SCRIPT_DEST=%INSTALL_DIR%\ide_tracker.pyw

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

if not exist "%SCRIPT_SRC%" (
    echo ERROR: ide_tracker.pyw not found next to this installer.
    echo Make sure both files are in the same folder.
    pause
    exit /b 1
)

copy /Y "%SCRIPT_SRC%" "%SCRIPT_DEST%" >nul
echo Script installed to: %SCRIPT_DEST%

:: ── Create Startup shortcut ───────────────────────────────────────────────────
:: This makes the tracker launch automatically every time Windows starts.
:: The shortcut is placed in the user's Startup folder (no admin rights needed).
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SHORTCUT=%STARTUP_DIR%\IdeTimeTracker.lnk
set VBS_TMP=%TEMP%\create_shortcut.vbs

:: Build a temporary VBScript to create the shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell")  > "%VBS_TMP%"
echo sLinkFile = "%SHORTCUT%"                         >> "%VBS_TMP%"
echo Set oLink = oWS.CreateShortcut(sLinkFile)        >> "%VBS_TMP%"
echo oLink.TargetPath = "%PYTHON_EXE%"                >> "%VBS_TMP%"
echo oLink.Arguments = """%SCRIPT_DEST%"""            >> "%VBS_TMP%"
echo oLink.WorkingDirectory = "%INSTALL_DIR%"         >> "%VBS_TMP%"
echo oLink.Description = "IDE Time Tracker"           >> "%VBS_TMP%"
echo oLink.WindowStyle = 7                            >> "%VBS_TMP%"
echo oLink.Save                                       >> "%VBS_TMP%"

cscript //nologo "%VBS_TMP%"
del "%VBS_TMP%" >nul 2>&1

if exist "%SHORTCUT%" (
    echo Startup shortcut created: OK
) else (
    echo ERROR: Could not create Startup shortcut.
    pause
    exit /b 1
)

:: ── Done ─────────────────────────────────────────────────────────────────────
echo.
echo ============================================
echo   Installation complete!
echo ============================================
echo.
echo  - IDE Time Tracker will start automatically
echo    every time Windows boots.
echo  - To uninstall, delete the shortcut at:
echo    %SHORTCUT%
echo    and the folder: %INSTALL_DIR%
echo.
echo Launching now...
start "" "%PYTHON_EXE%" "%SCRIPT_DEST%"

timeout /t 3 >nul
