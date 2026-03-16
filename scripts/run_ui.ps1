# Run Streamlit UI. Ensure FastAPI backend is running first (scripts/run_server.ps1)
Set-Location $PSScriptRoot\..

if (Test-Path ..\venv\Scripts\Activate.ps1) {
    ..\venv\Scripts\Activate.ps1
} elseif (Test-Path .\venv\Scripts\Activate.ps1) {
    .\venv\Scripts\Activate.ps1
}

Write-Host "Starting Streamlit UI at http://localhost:8501"
Write-Host "Ensure FastAPI backend is running: uvicorn app.main:app --host 0.0.0.0 --port 8000"
streamlit run ui_app.py
