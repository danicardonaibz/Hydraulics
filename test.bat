@echo off
REM Quick test script for Windows

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment and run smoke test
call venv\Scripts\activate.bat
python smoke_test.py
pause
