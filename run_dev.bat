@echo off
echo ===================================================
echo Starting RecipeAI Development Environment...
echo ===================================================

:: Start FastAPI Backend in a new window
echo Starting FastAPI Backend on port 8000...
start cmd /k "echo Starting Backend... && cd backend && python main.py"

:: Start React Vite Frontend in current window
echo Starting React Frontend on port 5173...
cd frontend && npm run dev
