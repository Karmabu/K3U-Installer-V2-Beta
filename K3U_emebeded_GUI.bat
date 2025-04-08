@echo off
setlocal

REM --- Path Configuration ---
REM Determine the current directory of the batch script
set "SCRIPT_DIR=%~dp0"
REM Remove trailing backslash (\) if present for consistency
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Define the embedded Python directory and executable
set "EMBEDDED_PYTHON_DIR=%SCRIPT_DIR%\python_embeded"
set "EMBEDDED_PYTHON=%EMBEDDED_PYTHON_DIR%\python.exe"

REM Define the path to the get-pip.py script
set "GET_PIP_SCRIPT=%EMBEDDED_PYTHON_DIR%\get-pip.py"

REM Define the name of the GUI Python script
set "GUI_SCRIPT=%SCRIPT_DIR%\k3u_installer_gui.py"

REM --- Check for Embedded Python ---
echo Checking for Python executable: %EMBEDDED_PYTHON%
if not exist "%EMBEDDED_PYTHON%" (
    echo ERROR: Python executable not found in %EMBEDDED_PYTHON_DIR%
    echo Make sure the 'python_embeded' folder exists here and contains python.exe
    pause
    exit /b 1
)

REM --- Install/Update Python Dependencies ---
echo.
echo Starting installation/update of dependencies for embedded Python...
echo Target folder: %EMBEDDED_PYTHON_DIR%
echo.

REM 1. Install/Update pip using get-pip.py
echo Checking for get-pip.py: %GET_PIP_SCRIPT%
if not exist "%GET_PIP_SCRIPT%" (
    echo ERROR: Script 'get-pip.py' not found in %EMBEDDED_PYTHON_DIR%
    echo Download it from https://bootstrap.pypa.io/get-pip.py and place it in that folder.
    pause
    exit /b 1
)
echo Running get-pip.py to install/update pip...
"%EMBEDDED_PYTHON%" "%GET_PIP_SCRIPT%" --target "%EMBEDDED_PYTHON_DIR%" --no-warn-script-location
if errorlevel 1 (
    echo ERROR: Failed during get-pip.py execution.
    pause
    exit /b 1
)

REM 2. Install/Update setuptools
echo Installing/Updating setuptools...
"%EMBEDDED_PYTHON%" -m pip install --upgrade setuptools --target "%EMBEDDED_PYTHON_DIR%" --no-warn-script-location
if errorlevel 1 (
    echo ERROR: Failed during setuptools installation.
    pause
    exit /b 1
)

REM 3. Install/Update tkinter-embed
echo Installing/Updating tkinter-embed...
"%EMBEDDED_PYTHON%" -m pip install --upgrade tkinter-embed --target "%EMBEDDED_PYTHON_DIR%" --no-warn-script-location
if errorlevel 1 (
    echo ERROR: Failed during tkinter-embed installation.
    pause
    exit /b 1
)

echo.
echo Dependency installation completed successfully.
echo.

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
