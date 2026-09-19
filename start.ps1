# PowerShell launcher for CosmoContour 2035
$PSScriptRoot = Split-Path -Parent -MyInvocation.MyCommand.Definition
Set-Location $PSScriptRoot

Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "  ТОПЛИВНЫЙ КОСМОКОНТУР 2035 // СИТУАЦИОННЫЙ ЦЕНТР ОТУ" -ForegroundColor Yellow
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
$pyCmd = if (Get-Command py -ErrorAction SilentlyContinue) { "py" } elseif (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { $null }
if (-not $pyCmd) {
    Write-Error "Python не найден в системе!"
    exit 1
}

# Check Node / npm
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Error "Node.js / npm не найден в системе!"
    exit 1
}

Write-Host "[1/2] Запуск Backend API (FastAPI) на http://127.0.0.1:8000 ..." -ForegroundColor Green
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "$pyCmd -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload" -WorkingDirectory $PSScriptRoot

Write-Host "[2/2] Запуск Frontend UI (React/Vite) на http://localhost:3000 ..." -ForegroundColor Green
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "npm.cmd run dev" -WorkingDirectory "$PSScriptRoot\frontend"

Start-Sleep -Seconds 3
Start-Process "http://localhost:3000"

Write-Host "Система успешно запущена!" -ForegroundColor Yellow
