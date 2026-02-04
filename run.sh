#!/bin/bash
# Quick run script for Linux/Mac

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found!"
    echo "Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment and run the tool
source venv/bin/activate
python hydro_calc.py
