@echo off
setlocal

REM Determine the current directory of the batch script
set "SCRIPT_DIR=%~dp0"

REM Define the name of the GUI Python script
set "GUI_SCRIPT=%SCRIPT_DIR%k3u_installer_gui.py"

echo Checking for GUI script: %GUI_SCRIPT%
if not exist "%GUI_SCRIPT%" (
    echo ERROR: GUI script '%GUI_SCRIPT%' not found.
    echo Make sure the Python script is located in this same folder.
    pause
    exit /b 1
)

echo Starting K3U Installer GUI using system Python (from PATH)...
echo Make sure the Python in PATH has Tkinter installed.
echo.

REM Run the GUI script using Python found in the system PATH
python "%GUI_SCRIPT%"

REM Alternative (more explicit on Windows, usually equivalent):
REM python.exe "%GUI_SCRIPT%"

echo.
echo GUI script finished.
pause

endlocal
