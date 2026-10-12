@echo off
echo ========================================================
echo    TenderAI - Sarvam Bidding Agent Prototype Launcher
echo ========================================================
echo.
echo Activating virtual environment...
if exist "sarvam-starter\.venv\Scripts\activate.bat" (
    call sarvam-starter\.venv\Scripts\activate.bat
) else (
    echo [!] Virtual environment not found at sarvam-starter\.venv
    echo Running with default python...
)

echo Starting TenderAI Server at http://127.0.0.1:8000 ...
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
