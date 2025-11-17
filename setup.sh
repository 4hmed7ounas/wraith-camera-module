#!/bin/bash

# Setup script for Multi-Detection System (macOS/Linux)
# This script sets up the virtual environment and installs dependencies

echo ""
echo "============================================================"
echo "Multi-Detection System - macOS/Linux Setup Script"
echo "============================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed!"
    echo "Please install Python 3.8+ using:"
    echo "  macOS: brew install python3"
    echo "  Linux: sudo apt-get install python3 python3-venv"
    exit 1
fi

echo "[INFO] Python found:"
python3 --version
echo ""

# Check if venv exists
if [ -d "venv" ]; then
    echo "[INFO] Virtual environment already exists"
else
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment!"
        exit 1
    fi
    echo "[SUCCESS] Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment!"
    exit 1
fi
echo "[SUCCESS] Virtual environment activated"
echo ""

# Upgrade pip
echo "[INFO] Upgrading pip..."
python -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "[WARNING] Failed to upgrade pip, continuing anyway..."
fi
echo ""

# Install requirements
echo "[INFO] Installing dependencies from requirements.txt..."
echo "This may take 10-15 minutes on first run..."
echo ""
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies!"
    echo "Please check your internet connection and try again"
    exit 1
fi
echo "[SUCCESS] Dependencies installed"
echo ""

# Create directories if they don't exist
mkdir -p data logs models

echo ""
echo "============================================================"
echo "Setup Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment each time you work:"
echo "   source venv/bin/activate"
echo "2. Run the application:"
echo "   python src/main.py"
echo ""
echo "For detailed instructions, see README.md"
echo ""
