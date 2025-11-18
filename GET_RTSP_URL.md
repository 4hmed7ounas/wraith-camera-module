# Getting Your Phone's RTSP URL for Camera Streaming

## Quick Methods to Get RTSP URL

### Method 1: Check Phone Link App (Windows 11)

1. Open **Phone Link** app on your PC
2. Go to **Camera** section
3. Look for **camera stream details** or **settings**
4. Copy the RTSP URL shown
5. Format: Usually `rtsp://your.phone.ip:port/stream`

### Method 2: Find Phone's IP Address

1. On your phone, go to **Settings → WiFi**
2. Tap on your current network
3. Look for **IP address** (e.g., `192.168.1.50`)
4. Use a camera app with typical ports:
   - IP Webcam: `rtsp://192.168.1.50:8080/video`
   - DroidCam: `rtsp://192.168.1.50:4747/mjpegfeed`

### Method 3: Using ADB (Advanced)

If you have Android SDK installed:

```bash
adb shell getprop dhcp.wlan0.ipaddress
```

This gives you the phone's IP, then add port and path.

### Method 4: Check Router

1. Open your router's admin interface
2. Go to **Connected Devices**
3. Find your phone's name and IP
4. Use that IP with streaming app port

### Method 5: Try These Common Combinations

If you're using a streaming app, try these URL patterns:

**IP Webcam:**
```
rtsp://192.168.1.x:8080/video
rtsp://192.168.1.x:554/stream
```

**DroidCam:**
```
rtsp://192.168.1.x:4747/mjpegfeed
rtsp://192.168.1.x:4747/video
```

**Generic RTSP:**
```
rtsp://192.168.1.x:554/stream
rtsp://192.168.1.x:8554/stream
```

## Testing Your RTSP URL

### Using VLC Media Player:

1. Open **VLC Media Player**
2. Click **Media** → **Open Network Stream**
3. Paste your RTSP URL
4. Click **Play**

If video appears, your URL is correct!

### Using Command Line (PowerShell):

```powershell
# Test with ffmpeg (if installed)
ffmpeg -rtsp_transport tcp -i "rtsp://192.168.1.100:8080/video" -t 5 -f null -

# Or test with ffprobe
ffprobe "rtsp://192.168.1.100:8080/video"
```

### Using Python:

```python
import cv2

url = "rtsp://192.168.1.100:8080/video"
cap = cv2.VideoCapture(url)

if cap.isOpened():
    print("URL works!")
    ret, frame = cap.read()
    cap.release()
else:
    print("URL failed")
```

## Default Ports by Streaming App

| App | Port | Path | Full URL Example |
|-----|------|------|------------------|
| IP Webcam (H264/uLaw) | 8080 | /h264_ulaw.sdp | **rtsp://192.168.0.107:8080/h264_ulaw.sdp** |
| IP Webcam (H264/PCM) | 8080 | /h264_pcm.sdp | rtsp://192.168.0.107:8080/h264_pcm.sdp |
| IP Webcam (HTTP) | 8080 | /video | http://192.168.0.107:8080/video |
| DroidCam | 4747 | /mjpegfeed | rtsp://192.168.1.50:4747/mjpegfeed |
| Manycam | 554 | /stream | rtsp://192.168.1.50:554/stream |
| Phone Link | varies | varies | Check Phone Link settings |
| Generic RTSP | 554 | /stream | rtsp://192.168.1.50:554/stream |

## Troubleshooting

### "Connection Refused"
- Streaming app not running on phone
- Wrong port number
- Firewall blocking connection
- Phone IP changed

### "Timeout"
- Phone WiFi disconnected
- Network latency too high
- Wrong IP address
- RTSP server not responding

### "Invalid URL Format"
- Missing `rtsp://` prefix
- Check spelling of IP and port
- Use colons `:` not periods between port
- Example: `192.168.1.50:8080` NOT `192.168.1.50.8080`

## Where to Find Streaming Apps

### Android:
- **IP Webcam**: Google Play Store (free)
- **DroidCam**: Google Play Store (free)
- **Manycam**: Google Play Store (freemium)

### iPhone/iPad:
- **Live Studio**: App Store
- **Manycam**: App Store
- Check App Store for "IP camera" or "webcam"

## Using in Multi-Detection System

Once you have your RTSP URL:

```powershell
python src/main.py

# When prompted:
# Select option: 2
# Enter URL: rtsp://192.168.1.50:8080/video
# Press Enter to start
```

## Common URLs to Try (by Priority)

If you're using **IP Webcam**, try in this order:

```
rtsp://192.168.0.107:8080/h264_ulaw.sdp      # RECOMMENDED for IP Webcam
rtsp://192.168.0.107:8080/h264_pcm.sdp       # Alternative for IP Webcam
http://192.168.0.107:8080/video              # HTTP streaming
rtsp://192.168.0.107:554/stream               # Generic RTSP
rtsp://192.168.0.107:8554/stream              # Alternative RTSP
```

For **other apps**, try:

```
rtsp://192.168.1.50:4747/mjpegfeed            # DroidCam
rtsp://192.168.1.50:554/stream                # Generic
rtsp://192.168.1.50:1935/live/stream          # RTMP
```

Replace `192.168.0.107` with your actual phone IP address.

---

**Need Help?** Check the streaming app's documentation or settings for exact URL format.
