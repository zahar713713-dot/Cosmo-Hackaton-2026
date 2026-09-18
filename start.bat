@echo off
chcp 65001 > nul
title Топливный космоконтур 2035
echo ===================================================================
echo   ТОПЛИВНЫЙ КОСМОКОНТУР 2035 // Рабочее место оператора ОТУ
echo   КосмоХакатон 2026 // Проект "Кадры для космоса"
echo ===================================================================
echo.
echo [1/2] Запуск Backend API (FastAPI) на порту 8000...
start "Космоконтур - Backend API" py -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload

echo [2/2] Запуск Frontend (React/Vite) на порту 3000...
start "Космоконтур - Frontend UI" cmd /c "cd frontend && npm run dev"

echo.
echo Сервисы успешно запущены в фоновых окнах:
echo   - Дашборд оператора: http://localhost:3000
echo   - Документация API (Swagger): http://127.0.0.1:8000/docs
echo.
echo Нажмите любую клавишу для закрытия этого стартового окна.
pause > nul
