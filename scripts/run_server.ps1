# Run the FastAPI server (Windows). Run from project root: .\scripts\run_server.ps1

Set-Location $PSScriptRoot\..

if (Test-Path .\venv\Scripts\Activate.ps1) {
    .\venv\Scripts\Activate.ps1
}

$hostName = if ($env:HOST) { $env:HOST } else { "0.0.0.0" }
$port = if ($env:PORT) { $env:PORT } else { "8000" }
Write-Host "Starting server at http://${hostName}:${port}"
uvicorn app.main:app --host $hostName --port $port
