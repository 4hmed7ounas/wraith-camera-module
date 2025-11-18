================================================================================
WRAITH CAMERA MODULE - RASPBERRY PI 5 DEPLOYMENT GUIDE
================================================================================

HARDWARE REQUIREMENTS:
- Raspberry Pi 5 (4GB RAM minimum)
- USB Webcam or Raspberry Pi Camera Module
- MicroSD Card (32GB+ recommended)
- Power Supply (official Pi 5 power supply recommended)
- Optional: Heatsink/fan for cooling

SOFTWARE REQUIREMENTS:
- Raspberry Pi OS (64-bit recommended)
- Python 3.9+

================================================================================
QUICK START
================================================================================

1. Transfer files to Raspberry Pi:
   scp -r wraith-camera-module pi@raspberrypi.local:~/

2. SSH into Raspberry Pi:
   ssh pi@raspberrypi.local

3. Navigate to project:
   cd ~/wraith-camera-module

4. Make scripts executable:
   chmod +x setup_raspberry_pi.sh
   chmod +x install_service.sh

5. Run setup script:
   ./setup_raspberry_pi.sh

6. Activate virtual environment:
   source venv/bin/activate

7. Run the application:
   python main_raspberry_pi.py

================================================================================
CONFIGURATION OPTIONS
================================================================================

The default configuration is optimized for Pi 5:
- Resolution: 640x480 (lower than desktop version)
- FPS: 15 (lower than desktop version)
- Face Detection: Every 10 frames (was 5)
- Object Detection: Every 2 frames
- OCR: Disabled by default (too slow)

To modify settings, edit: config_raspberry_pi.py

Available presets in config_raspberry_pi.py:
- pi_balanced (default): Face + Object detection
- pi_performance: Object detection only, max speed
- pi_faces_only: Face detection only
- pi_objects_only: Object detection only
- pi_minimal: Minimal config for testing

================================================================================
PERFORMANCE OPTIMIZATION TIPS
================================================================================

1. REDUCE RESOLUTION:
   Lower frame_width and frame_height in config_raspberry_pi.py
   Example: 320x240 for maximum speed

2. DISABLE FEATURES:
   Set enable_face_recognition or enable_object_detection to False
   Disable OCR (already disabled by default)

3. INCREASE FRAME SKIPPING:
   Higher frame_skip values = faster processing but less responsive
   Face: frame_skip = 10-15
   Object: frame_skip = 2-3

4. MONITOR TEMPERATURE:
   vcgencmd measure_temp
   If temp > 70°C, consider adding cooling

5. OVERCLOCK (Advanced):
   Edit /boot/config.txt (be careful!)
   Add heatsink/fan before overclocking

6. USE LITE OS:
   Install Raspberry Pi OS Lite (no desktop) for better performance
   Run in headless mode, stream results over network

================================================================================
AUTO-START ON BOOT
================================================================================

To run the detection system automatically on boot:

1. Install as systemd service:
   sudo ./install_service.sh

2. Start the service:
   sudo systemctl start wraith-camera

3. Check status:
   sudo systemctl status wraith-camera

4. View live logs:
   sudo journalctl -u wraith-camera -f

5. Stop the service:
   sudo systemctl stop wraith-camera

6. Disable auto-start:
   sudo systemctl disable wraith-camera

================================================================================
TROUBLESHOOTING
================================================================================

ISSUE: Camera not detected
FIX: - Check camera connection
     - Run: v4l2-ctl --list-devices
     - For Pi Camera: Enable camera in raspi-config
     - Try changing camera_id in config

ISSUE: Low FPS / Laggy performance
FIX: - Lower resolution to 320x240
     - Disable face recognition
     - Increase frame_skip values
     - Close other applications
     - Check CPU temperature

ISSUE: "Out of memory" errors
FIX: - Increase swap size: sudo dphys-swapfile swapoff
       Edit /etc/dphys-swapfile, set CONF_SWAPSIZE=2048
       sudo dphys-swapfile setup && sudo dphys-swapfile swapon
     - Disable OCR
     - Use only object detection

ISSUE: TensorFlow/DeepFace installation fails
FIX: - Face recognition is heavy on Pi
     - Consider disabling face recognition
     - Install dependencies one by one
     - Use pip install --no-cache-dir

ISSUE: YOLO model download fails
FIX: - Pre-download model on PC
     - Copy yolov8n.pt to Pi
     - Place in project root or models/ folder

ISSUE: OpenCV window not displaying
FIX: - Make sure you have desktop environment
     - Run: export DISPLAY=:0
     - Or use VNC/X11 forwarding

================================================================================
CAMERA OPTIONS
================================================================================

USB WEBCAM:
- Set camera_id = 0 in config
- Most USB webcams work out of the box

RASPBERRY PI CAMERA MODULE:
- Enable camera in raspi-config
- Install picamera2: pip install picamera2
- May need to modify code to use picamera2 API

MULTIPLE CAMERAS:
- camera_id = 0 (first camera)
- camera_id = 1 (second camera)
- Check with: v4l2-ctl --list-devices

================================================================================
EXPECTED PERFORMANCE
================================================================================

Raspberry Pi 5 (4GB) with recommended settings:
- Object Detection Only: 15-20 FPS @ 640x480
- Object + Face Detection: 10-15 FPS @ 640x480
- All Features (with OCR): 3-5 FPS @ 640x480

For better performance:
- Lower resolution to 320x240: 20-25 FPS
- Disable face recognition: 18-22 FPS
- Use minimal config: 25-30 FPS

================================================================================
NETWORKING / REMOTE ACCESS
================================================================================

VIEW OUTPUT REMOTELY:
1. SSH with X11 forwarding:
   ssh -X pi@raspberrypi.local
   python main_raspberry_pi.py

2. VNC (Recommended):
   Enable VNC in raspi-config
   Connect with VNC Viewer

3. Stream over HTTP (Advanced):
   Modify code to stream frames via Flask
   Access via web browser

================================================================================
FILES CREATED FOR RASPBERRY PI
================================================================================

config_raspberry_pi.py         - Pi-optimized configuration
main_raspberry_pi.py           - Pi-optimized main script
requirements_raspberry_pi.txt  - ARM-compatible dependencies
setup_raspberry_pi.sh          - Automated setup script
install_service.sh             - Auto-start service installer
README_RASPBERRY_PI.txt        - This file

================================================================================
NEXT STEPS
================================================================================

1. Test the basic setup:
   python main_raspberry_pi.py

2. Optimize settings for your use case

3. Set up auto-start if needed

4. Consider building a case with cooling

5. Optionally add cloud logging to send results to a server

================================================================================
SUPPORT & ISSUES
================================================================================

For performance issues:
- Check CPU temperature
- Monitor with: htop, vcgencmd measure_temp
- Review config_raspberry_pi.py settings

For bugs or questions:
- Check the main README.md
- Review error logs
- Test with minimal configuration first

================================================================================
