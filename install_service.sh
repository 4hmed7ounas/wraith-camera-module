#!/bin/bash
# Install systemd service for auto-start on boot

set -e

echo "=========================================="
echo "Installing systemd service"
echo "=========================================="
echo ""

# Get current directory
INSTALL_DIR=$(pwd)
USER=$(whoami)

echo "Installation directory: $INSTALL_DIR"
echo "Running as user: $USER"
echo ""

# Create systemd service file
SERVICE_FILE="/etc/systemd/system/wraith-camera.service"

echo "Creating service file at $SERVICE_FILE..."

sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Wraith Camera Detection System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/$USER/.Xauthority"
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/main_raspberry_pi.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable service
echo "Enabling service..."
sudo systemctl enable wraith-camera.service

echo ""
echo "=========================================="
echo "Service installed successfully!"
echo "=========================================="
echo ""
echo "Available commands:"
echo "  Start service:   sudo systemctl start wraith-camera"
echo "  Stop service:    sudo systemctl stop wraith-camera"
echo "  Check status:    sudo systemctl status wraith-camera"
echo "  View logs:       sudo journalctl -u wraith-camera -f"
echo "  Disable service: sudo systemctl disable wraith-camera"
echo ""
echo "The service will now start automatically on boot."
echo ""
