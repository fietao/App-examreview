@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo   Java Study App - Setup and Run
echo ==========================================
echo.

set "VENV_DIR=.venv"
set "MODEL=llama3:latest"
set "RUN_APP=1"
if /I "%~1"=="--setup-only" set "RUN_APP=0"

where py >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_BOOT=py -3"
) else (
    where python >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python was not found in PATH.
        echo Install Python 3.8+ and re-run this script.
        pause
        exit /b 1
    )
    set "PY_BOOT=python"
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [1/5] Creating virtual environment in %VENV_DIR%...
    %PY_BOOT% -m venv "%VENV_DIR%"
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [1/5] Virtual environment already exists.
)

echo [2/5] Installing Python dependencies...
call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b 1
)

echo [3/5] Checking Ollama installation...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Ollama is not installed.
    echo Download from: https://ollama.com/download
    pause
    exit /b 1
)

echo [4/5] Ensuring Ollama is running and model is available (%MODEL%)...
powershell -NoProfile -Command "try { Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -TimeoutSec 3 | Out-Null; exit 0 } catch { exit 1 }"
if %errorlevel% neq 0 (
    echo Starting Ollama service in background...
    start "" /B ollama serve
)
ollama pull %MODEL%
if %errorlevel% neq 0 (
    echo [ERROR] Failed to pull model %MODEL%.
    echo Check internet and run: ollama pull %MODEL%
    pause
    exit /b 1
)

echo [5/5] Verifying app health endpoint logic dependencies...
powershell -NoProfile -Command "try { Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -TimeoutSec 10 | Out-Null; Write-Host 'Ollama API: OK' } catch { Write-Host 'Ollama API: NOT REACHABLE'; exit 1 }"
if %errorlevel% neq 0 (
    echo [ERROR] Ollama API is still unreachable at http://localhost:11434.
    pause
    exit /b 1
)

if "%RUN_APP%"=="0" (
    echo.
    echo Setup complete. Run this to start app:
    echo   call %VENV_DIR%\Scripts\activate.bat ^&^& python study_app.py
    exit /b 0
)

echo.
echo Setup complete. Launching app...
echo URL: http://localhost:5000
echo Press Ctrl+C to stop.
echo.
python study_app.py
