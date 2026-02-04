#!/bin/bash

echo "============================================================"
echo "Hydraulic Piping Calculation Tool - Setup"
echo "============================================================"
echo ""

# Check if virtual environment already exists
if [ -d "venv" ]; then
    echo "Virtual environment already exists."
    echo "To recreate it, delete the 'venv' folder first."
    echo ""
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        echo "Make sure Python 3 is installed."
        exit 1
    fi
    echo "Virtual environment created successfully."
    echo ""
fi

echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment."
    exit 1
fi

echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    exit 1
fi

echo ""
echo "============================================================"
echo "Setup complete!"
echo "============================================================"
echo ""
echo "To use the tool:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the tool: python hydro_calc.py"
echo ""
echo "Or simply run: ./run.sh"
echo ""
