# Setup script (Windows PowerShell): create venv and install dependencies.
# Run from project root: .\scripts\setup_env.ps1

Set-Location $PSScriptRoot\..
$ErrorActionPreference = "Stop"

Write-Host "Creating virtual environment..."
python -m venv venv

Write-Host "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

Write-Host "Installing dependencies..."
pip install -r requirements.txt

if (-not (Test-Path .env)) {
    Write-Host "Copying .env.example to .env..."
    Copy-Item .env.example .env
    Write-Host "Edit .env and set SECRET_KEY, MONGODB_URI, etc."
} else {
    Write-Host ".env already exists; skipping."
}

Write-Host "Setup complete. Activate with: .\venv\Scripts\Activate.ps1"
