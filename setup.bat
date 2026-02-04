@echo off
echo ============================================================
echo Hydraulic Piping Calculation Tool - Setup
echo ============================================================
echo.

REM Check if virtual environment already exists
if exist venv (
    echo Virtual environment already exists.
    echo To recreate it, delete the 'venv' folder first.
    echo.
) else (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment.
        echo Make sure Python is installed and in your PATH.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
    echo.
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment.
    pause
    exit /b 1
)

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo Installing hydraulics package in development mode...
pip install -e .
if errorlevel 1 (
    echo Error: Failed to install hydraulics package.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Setup complete!
echo ============================================================
echo.
echo To use the tool:
echo 1. Run: run.bat
echo.
echo Or manually:
echo 1. Activate the virtual environment: venv\Scripts\activate
echo 2. Run the tool: python hydro_calc.py
echo.
pause
