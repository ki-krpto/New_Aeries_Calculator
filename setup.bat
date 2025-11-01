@echo off
echo Aeries Grade Calculator - Setup
echo ================================
echo.

REM Find Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python not found! Please install Python from python.org
    pause
    exit /b
)

echo Step 1: Creating virtual environment...
python -m venv .venv
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create virtual environment!
    pause
    exit /b
)
echo Virtual environment created!
echo.

echo Step 2: Activating virtual environment...
call .venv\Scripts\activate.bat
echo.

echo Step 3: Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies!
    pause
    exit /b
)
echo Dependencies installed!
echo.

echo Step 4: Initializing database...
python database.py
if %ERRORLEVEL% NEQ 0 (
    echo Failed to initialize database!
    pause
    exit /b
)
echo Database initialized!
echo.

echo ================================
echo Setup complete!
echo.
echo To run the app, use: run.bat
echo Or manually: .venv\Scripts\activate.bat then python app.py
echo.
pause
