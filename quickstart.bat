@echo off
REM Quick start script for HealthClaim Analytics Hub (Windows)

setlocal enabledelayedexpansion

echo 🏥 HealthClaim Analytics Hub - Quick Start (Windows)
echo =====================================================
echo.

REM Step 1: Check Python version
echo [Step 1] Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python %PYTHON_VERSION% found
echo.

REM Step 2: Create virtual environment
echo [Step 2] Setting up virtual environment...
if not exist "venv\" (
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)
echo.

REM Step 3: Activate virtual environment
echo [Step 3] Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.

REM Step 4: Install dependencies
echo [Step 4] Installing dependencies...
pip install --upgrade pip setuptools wheel >nul 2>&1
pip install -r requirements.txt >nul 2>&1
echo ✓ Dependencies installed
echo.

REM Step 5: Configure secrets
echo [Step 5] Checking Streamlit secrets...
if not exist ".streamlit\secrets.toml" (
    if exist ".streamlit\secrets.toml.example" (
        copy .streamlit\secrets.toml.example .streamlit\secrets.toml
        echo ⚠ Created .streamlit\secrets.toml from template
        echo ⚠ Please edit .streamlit\secrets.toml and add your OpenAI API key
        echo.
        echo To get your OpenAI API key:
        echo   1. Visit https://platform.openai.com/api-keys
        echo   2. Create a new API key
        echo   3. Copy the key to .streamlit\secrets.toml
        echo.
        pause
    )
)
echo.

REM Step 6: Start application
echo [Step 6] Starting HealthClaim Analytics Hub...
echo ✓ Application starting at http://localhost:8501
echo ⚠ Press Ctrl+C to stop
echo.

streamlit run app.py --logger.level=warning

pause
