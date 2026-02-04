@echo off
REM Quick run script for Windows

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment and run the tool
call venv\Scripts\activate.bat
python hydro_calc.py
