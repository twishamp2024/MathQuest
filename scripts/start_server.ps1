<#
.SYNOPSIS
    Starts the MathQuest FastAPI backend server and serves the web game & simulator.
.DESCRIPTION
    Initializes environment variables, ensures pure-Python compatibility, and starts Uvicorn.
#>

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  MathQuest: Adaptive AI-Based Educational Toy Server   " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# Set Python Path and Environment
$env:PYTHONPATH = "."
$env:DISABLE_SQLALCHEMY_C_EXTENSIONS = "1"

# Check Virtual Environment
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "Creating Python virtual environment in .venv..." -ForegroundColor Yellow
    python -m venv .venv
    & ".\.venv\Scripts\pip.exe" install -r backend\requirements-dev.txt
}

# Run pure-python compatibility check
& $VenvPython "scripts\ensure_pure_python.py"

Write-Host "Starting server on http://localhost:8000" -ForegroundColor Green
Write-Host "  - Web Adventure Game:       http://localhost:8000" -ForegroundColor White
Write-Host "  - Virtual ESP32 Simulator:  http://localhost:8000 (Click Simulator tab)" -ForegroundColor White
Write-Host "  - Interactive API Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host "Press Ctrl+C to stop the server.`n" -ForegroundColor DarkGray

& $VenvPython -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
