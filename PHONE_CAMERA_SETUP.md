# Using Phone Camera with Multi-Detection System

This guide explains how to use your mobile phone camera with the application via Phone Link or RTSP streaming.

## Option 1: Phone Link (Microsoft)

Phone Link is built into Windows 11 and can access your phone camera.

### Setup Steps:

1. **Connect Phone to PC:**
   - On your PC: Settings → Bluetooth & devices → Phone Link
   - On your phone: Open Phone Link app
   - Follow pairing instructions

2. **Get Camera Access:**
   - Phone Link provides access to phone's camera
   - The camera will appear as a standard device

3. **Get the RTSP URL:**
   - Open Settings on your phone
   - Find Phone Link camera stream details
   - Note the RTSP URL (usually format: `rtsp://192.168.x.x:port/stream`)

4. **Run the Application:**
   ```powershell
   python src/main.py
   ```

5. **When prompted:**
   - Select option `2` for Phone Camera
   - Enter your phone's RTSP URL
   - Press Enter to start

## Option 2: IP Webcam App (Android) - RECOMMENDED

Best method for Android phones. Supports both HTTP and RTSP streaming.

### Setup Steps:

1. **Install IP Webcam:**
   - Download from Google Play Store
   - Open the app

2. **Start Streaming:**
   - Tap "Start server"
   - Note the IP address and port (e.g., `192.168.0.107:8080`)

3. **Get the RTSP URL:**
   - **H264/uLaw (RECOMMENDED):** `rtsp://192.168.0.107:8080/h264_ulaw.sdp`
   - **H264/HQ PCM:** `rtsp://192.168.0.107:8080/h264_pcm.sdp`
   - Replace IP and port with your values

4. **Connect PC and Phone:**
   - Both must be on the same WiFi network
   - Or connect via Phone Link

5. **Run the Application:**
   ```powershell
   python src/main.py
   ```

6. **When prompted:**
   - Select option `2` for Phone Camera
   - Enter: `rtsp://192.168.0.107:8080/h264_ulaw.sdp`
   - Press Enter to start

### Alternative URLs (if above doesn't work):
   - HTTP streaming: `http://192.168.0.107:8080/video`
   - MJPEG HTTP: `http://192.168.0.107:8080/mjpegfeed`

## Option 3: DroidCam (Android)

Another popular streaming app.

### Setup Steps:

1. **Install DroidCam:**
   - Download from Google Play Store
   - Install DroidCam client on PC (optional but recommended)

2. **Get the RTSP URL:**
   - Launch app on phone
   - IP Webcam mode will show: `rtsp://phone_ip:port/video`
   - Example: `rtsp://192.168.1.50:4747/mjpegfeed`

3. **Run the Application:**
   ```powershell
   python src/main.py
   ```

4. **When prompted:**
   - Select option `2` for Phone Camera
   - Enter the RTSP URL from DroidCam
   - Press Enter to start

## Option 4: iPhone/iPad via HTTP Live Streaming

For Apple devices.

### Setup Steps:

1. **Install Streaming App:**
   - Recommended: Live Studio, Manycam, or similar
   - Apps provide HLS/RTSP streaming URLs

2. **Get the Stream URL:**
   - App will provide a URL like: `rtsp://ip:port/stream`

3. **Run the Application:**
   ```powershell
   python src/main.py
   ```

4. **When prompted:**
   - Select option `2` for Phone Camera
   - Enter the provided URL
   - Press Enter to start

## Troubleshooting

### "Camera not found" Error:
- Check Phone Link connection is active
- Verify streaming app is running on phone
- Confirm both devices are on same network
- Try different RTSP URLs
- Check firewall isn't blocking the connection

### Poor Video Quality/Lag:
- Reduce phone camera resolution in app settings
- Ensure good WiFi signal
- Close other bandwidth-heavy apps
- Use 5GHz WiFi if available
- Lower frame rate in application (edit main.py)

### Connection Drops:
- Check WiFi connection stability
- Ensure Phone Link stays active
- Streaming app may have timeout - restart it
- Reconnect phone to PC

### Wrong RTSP URL:
Common formats:
- `rtsp://192.168.x.x:554/stream` (standard)
- `rtsp://192.168.x.x:8080/video` (IP Webcam)
- `rtsp://192.168.x.x:4747/mjpegfeed` (DroidCam)
- Check streaming app for exact URL

## Performance Tips

1. **Phone Camera is slower than local webcam:**
   - OCR is disabled by default (too slow for network)
   - Face recognition: every 2 frames (optimized)
   - Object detection: every 3 frames (optimized)

2. **To improve performance:**
   - Lower phone resolution
   - Reduce FPS in settings
   - Disable unnecessary modules
   - Use 5GHz WiFi
   - Place phone near PC (WiFi strength)

3. **For better recognition:**
   - Ensure good lighting
   - Position phone steady
   - Face should be 30-50cm from camera
   - Clear, unobstructed view

## Keyboard Shortcuts (During Operation)

| Key | Action |
|-----|--------|
| `q` | Quit application |
| `s` | Save current frame to logs/ |
| `t` | Toggle OCR on/off |
| `f` | Toggle face recognition on/off (if implemented) |

## Advanced: Custom RTSP Streaming

If you have your own streaming solution:

1. Get your RTSP URL
2. Test with VLC Media Player first:
   - Open VLC
   - Media → Open Network Stream
   - Paste your RTSP URL
   - If it plays, it will work with this app

3. Use the URL in the application:
   ```powershell
   python src/main.py
   # Select option 2
   # Paste your RTSP URL
   # Press Enter
   ```

## Bandwidth Requirements

- **1080p @ 30fps**: ~5-8 Mbps
- **720p @ 30fps**: ~2-4 Mbps
- **480p @ 30fps**: ~1-2 Mbps

Recommended: 5GHz WiFi with 5+ Mbps dedicated bandwidth

## Security Notes

- Phone camera access is only during application runtime
- No recording occurs unless explicitly saved with 's' key
- Saved frames are stored in `logs/` directory locally
- Face encodings stored in `data/face_encodings.pkl`

## Example Usage Session

```powershell
PS D:\FYP\camera-module> python src/main.py
============================================================
Multi-Detection System - Face Recognition, Objects & OCR
============================================================

Camera Source Selection:
  1. Built-in Webcam (default)
  2. Phone Camera via Phone Link (RTSP)

Select camera source (1 or 2, press Enter for 1): 2

[PHONE CAMERA] Phone Link Setup Instructions:
  1. Make sure Phone Link is connected on your PC and phone
  2. Use a camera streaming app on your phone (e.g., IP Webcam, DroidCam)
  3. Get the RTSP URL from the app (format: rtsp://phone_ip:port/stream)

Enter Phone Camera RTSP URL: rtsp://192.168.1.100:8080/video

[INFO] Using phone camera: rtsp://192.168.1.100:8080/video

[INFO] Connecting to phone camera: rtsp://192.168.1.100:8080/video
[INFO] Camera opened successfully
[INFO] Resolution: 1280x720
[INFO] Starting video processing...
[INFO] Press 'q' to quit, 's' to save frame, 't' to toggle OCR

[FACE] Loaded 0 known faces
[OBJECT] Model loaded. 80 classes available
```

Enjoy using your phone camera! 📱

---

**Last Updated:** November 2024
**Status:** Working with Phone Link and RTSP streams
