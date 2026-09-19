@echo off
title Stop CosmoContour 2035 Services

echo ===================================================================
echo   STOPPING COSMOCONTOUR 2035 SERVICES
echo ===================================================================
echo.

echo Terminating processes on port 8000 (Backend) and port 3000 (Frontend)...

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo Stopping Backend PID %%a...
    taskkill /F /PID %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    echo Stopping Frontend PID %%a...
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo All services stopped successfully.
ping 127.0.0.1 -n 3 >nul
