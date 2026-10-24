<#
.SYNOPSIS
    Runs the automated pytest test suite and generates a coverage summary.
#>

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

$env:PYTHONPATH = "."
$env:DISABLE_SQLALCHEMY_C_EXTENSIONS = "1"

$VenvPytest = Join-Path $ProjectRoot ".venv\Scripts\pytest.exe"
$VenvCoverage = Join-Path $ProjectRoot ".venv\Scripts\coverage.exe"

Write-Host "Running MathQuest Test Suite..." -ForegroundColor Cyan
& $VenvCoverage run -m pytest -v backend\tests

Write-Host "`nTest Coverage Summary:" -ForegroundColor Green
& $VenvCoverage report --include="backend/app/*"
