@echo off
REM Setup script for Multi-Detection System (Windows)
REM This script sets up the virtual environment and installs dependencies

echo.
echo ============================================================
echo Multi-Detection System - Windows Setup Script
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [INFO] Python found:
python --version
echo.

REM Check if venv exists
if exist "venv" (
    echo [INFO] Virtual environment already exists
) else (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created
)
echo.

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment activated
echo.

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, continuing anyway...
)
echo.

REM Install requirements
echo [INFO] Installing dependencies from requirements.txt...
echo This may take 10-15 minutes on first run...
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies!
    echo Please check your internet connection and try again
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed
echo.

REM Create directories if they don't exist
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "models" mkdir models

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Activate virtual environment each time you work:
echo    venv\Scripts\activate
echo 2. Run the application:
echo    python src\main.py
echo.
echo For detailed instructions, see README.md
echo.
pause
