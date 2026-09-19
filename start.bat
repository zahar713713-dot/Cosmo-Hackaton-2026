@echo off
title CosmoContour 2035 - Space Logistics Operator Workplace

:: Switch to script directory regardless of launch method or spaces in path
cd /d "%~dp0"

echo ===================================================================
echo   COSMOCONTOUR 2035 // CISLUNAR HUB OPERATOR WORKPLACE
echo   CosmoHackathon 2026
echo ===================================================================
echo.

:: Detect Python executable (py launcher or python)
set "PYTHON_EXE=py"
where py >nul 2>nul
if %errorlevel% equ 0 goto CHECK_NODE

set "PYTHON_EXE=python"
where python >nul 2>nul
if %errorlevel% equ 0 goto CHECK_NODE

echo [ERROR] Python was not found in PATH!
echo Please install Python 3.12+ and ensure it is added to PATH.
echo.
pause
exit /b 1

:CHECK_NODE
where npm >nul 2>nul
if %errorlevel% equ 0 goto ALL_OK

echo [ERROR] Node.js / npm was not found in PATH!
echo Please install Node.js 18 or newer to run the web UI.
echo.
pause
exit /b 1

:ALL_OK
echo [OK] Python detected: %PYTHON_EXE%
echo [OK] Node / npm detected
echo [OK] Workspace: %~dp0
echo.

echo [1/2] Starting Backend API on http://127.0.0.1:8000 ...
start "CosmoContour - Backend API" /D "%~dp0" cmd /k "%PYTHON_EXE% -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Starting Frontend UI on http://localhost:3000 ...
start "CosmoContour - Frontend UI" /D "%~dp0frontend" cmd /k "npm run dev"

echo.
echo ===================================================================
echo   Services successfully started in separate windows:
echo   - Web Dashboard:     http://localhost:3000
echo   - API Swagger Docs:  http://127.0.0.1:8000/docs
echo ===================================================================
echo.
echo Opening web dashboard in default browser in 3 seconds...
ping 127.0.0.1 -n 4 >nul

start http://localhost:3000

echo.
echo You may close this launcher window.
echo (The Backend and Frontend windows will keep running in background).
echo.
echo Press any key to exit this launcher...
pause >nul
