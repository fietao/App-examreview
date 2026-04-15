@echo off
title Java Study App
cd /d "%~dp0"

echo ==========================================
echo       Java Study App - Starter
echo ==========================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/
    pause
    exit /b
)

:: Check for Ollama and pull model
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Ollama not found. AI grading will not work.
    echo Please install it from https://ollama.com/
    echo.
) else (
    echo Checking if Ollama model is available...
    ollama list 2>nul | findstr /i "qwen2.5:1.5b" >nul 2>&1
    if %errorlevel% neq 0 (
        echo Pulling model qwen2.5:1.5b — this may take a minute on first run...
        ollama pull qwen2.5:1.5b
        if %errorlevel% neq 0 (
            echo [WARNING] Failed to pull model. Make sure Ollama is running: ollama serve
        ) else (
            echo Model ready!
        )
    ) else (
        echo Model qwen2.5:1.5b is ready.
    )
    echo.
)

:: Check for requirements
echo Checking dependencies...
python -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [WARNING] Failed to install requirements. Trying to run anyway...
)

echo.
echo Starting the app...
echo The app will open in your browser automatically.
echo Press Ctrl+C in this window to stop the server.
echo.

python study_app.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The app crashed or was interrupted.
    pause
)
