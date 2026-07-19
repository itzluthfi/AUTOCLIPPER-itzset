@echo off
echo ===================================================
echo   AutoClipper Local Dev Server Launcher
echo ===================================================

echo Starting FastAPI Backend...
start cmd /k "cd backend && .venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

echo Starting Expo Frontend Web App...
start cmd /k "cd frontend && npm run web"

echo Both servers are starting up!
echo - Backend API: http://localhost:8000/docs
echo - Frontend Web: Check browser window opened by Expo
echo - API Key for Login: autoclipper_local_dev_key_123
echo ===================================================
pause
