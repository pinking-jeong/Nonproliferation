# Launch helper — runs FastAPI backend and Streamlit frontend together.
#
# Usage (from ospm/ directory):
#   powershell -ExecutionPolicy Bypass -File scripts/launch_demo.ps1
#
# Stops both with Ctrl+C.

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "[OS-PM] Starting FastAPI backend on :8000 ..."
$backend = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"
) -PassThru -WindowStyle Minimized

Start-Sleep -Seconds 3

Write-Host "[OS-PM] Starting Streamlit on :8501 ..."
$env:OSPM_API = "http://127.0.0.1:8000"
$frontend = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "streamlit run frontend/app.py"
) -PassThru -WindowStyle Minimized

Write-Host ""
Write-Host "[OS-PM] Both services launched."
Write-Host "  Backend  : http://127.0.0.1:8000  (docs: /docs)"
Write-Host "  Frontend : http://127.0.0.1:8501"
Write-Host ""
Write-Host "Press Enter to stop both."
Read-Host

Write-Host "[OS-PM] Stopping ..."
Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue
Write-Host "[OS-PM] Done."
