@echo off
echo Starting Aeries Grade Calculator...
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Please run setup.bat first!
    pause
    exit /b
)

REM Activate virtual environment and run app
call .venv\Scripts\activate.bat
python app.py
pause
