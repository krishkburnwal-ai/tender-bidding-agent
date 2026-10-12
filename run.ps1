Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   TenderAI - Sarvam Bidding Agent Prototype Launcher   " -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan

$venvPython = ".\sarvam-starter\.venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    Write-Host "Using virtual environment Python ($venvPython)..." -ForegroundColor Green
    & $venvPython -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
} else {
    Write-Host "Starting with system python..." -ForegroundColor Yellow
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
}
