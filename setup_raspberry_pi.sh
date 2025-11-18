#!/bin/bash
# Raspberry Pi 5 Setup Script
# This script installs and configures the wraith-camera-module on Raspberry Pi

set -e  # Exit on error

echo "=========================================="
echo "Wraith Camera Module - Raspberry Pi Setup"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "[WARNING] This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "[1/8] Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo "[2/8] Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-opencv \
    libopencv-dev \
    libatlas-base-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test \
    libhdf5-dev \
    libhdf5-103 \
    git \
    cmake \
    libopenblas-dev

# Install Pi Camera support (optional)
read -p "Install Pi Camera support? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "[3/8] Installing Pi Camera libraries..."
    sudo apt-get install -y python3-picamera2
else
    echo "[3/8] Skipping Pi Camera installation"
fi

# Create virtual environment
echo "[4/8] Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "[5/8] Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "[6/8] Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "[7/8] Installing Python dependencies..."
echo "This may take 10-20 minutes on Raspberry Pi..."

# Install dependencies one by one to avoid memory issues
pip install numpy
pip install opencv-python
pip install Pillow
pip install psutil
pip install pyyaml
pip install scipy
pip install scikit-image

# Install PyTorch (ARM-optimized version)
echo "Installing PyTorch for ARM..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install YOLO
echo "Installing Ultralytics YOLO..."
pip install ultralytics

# Install DeepFace (optional - heavy)
read -p "Install DeepFace for face recognition? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing DeepFace (this will take a while)..."
    pip install deepface tf-keras
else
    echo "Skipping DeepFace installation"
fi

# Create necessary directories
echo "[8/8] Creating directories..."
mkdir -p data
mkdir -p logs
mkdir -p models

# Set permissions
chmod +x main_raspberry_pi.py

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the application:"
echo "   python main_raspberry_pi.py"
echo ""
echo "3. (Optional) Set up auto-start on boot:"
echo "   sudo ./install_service.sh"
echo ""
echo "Performance tips:"
echo "- Monitor temperature: vcgencmd measure_temp"
echo "- Check CPU usage: htop"
echo "- Lower resolution if FPS is too low"
echo "- Disable face recognition if only detecting objects"
echo ""
