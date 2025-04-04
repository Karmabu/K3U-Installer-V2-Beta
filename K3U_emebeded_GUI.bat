@echo off
setlocal

REM Determine the current directory of the batch script
set "SCRIPT_DIR=%~dp0"

REM Define the relative path to the embedded Python
set "EMBEDDED_PYTHON=%SCRIPT_DIR%python_embeded\python.exe"

REM Define the name of the GUI Python script
set "GUI_SCRIPT=%SCRIPT_DIR%k3u_installer_gui.py"

echo Checking for Embedded Python executable: %EMBEDDED_PYTHON%
if not exist "%EMBEDDED_PYTHON%" (
    echo ERROR: Embedded Python executable not found.
    echo Make sure the 'python_embeded' folder exists here and contains python.exe
    pause
    exit /b 1
)

echo Checking for GUI script: %GUI_SCRIPT%
if not exist "%GUI_SCRIPT%" (
    echo ERROR: GUI script '%GUI_SCRIPT%' not found.
    echo Make sure the Python script is in this same folder.
    pause
    exit /b 1
)

echo Launching K3U Installer GUI using Embedded Python...
echo.

REM Run the GUI script using embedded Python
"%EMBEDDED_PYTHON%" "%GUI_SCRIPT%"

echo.
echo GUI script has finished.
pause

endlocal
