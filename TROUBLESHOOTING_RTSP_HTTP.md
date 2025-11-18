# Troubleshooting RTSP/HTTP Streaming Issues

## Overview

The phone camera integration now includes **automatic fallback** from RTSP to HTTP if it detects issues. This guide helps you understand and resolve streaming problems.

## Quick Diagnostics

### 1. Check if Your Phone Camera is Running

First, verify your IP Webcam or DroidCam is actually streaming:

```powershell
# Open web browser and visit:
http://192.168.0.107:8080/
```

You should see the IP Webcam web interface showing video feed or options.

### 2. Test Connectivity

```powershell
# Ping your phone to verify network connection
ping 192.168.0.107

# Or use the built-in URL tester
python test_phone_camera.py 192.168.0.107
```

## RTSP H264 Black Screen Issue

### Problem
- Application connects to RTSP stream successfully
- Frame reading works
- **BUT**: Display shows all black frames
- Error messages show: `[h264 @ ...] error while decoding MB 53 1`

### Root Cause
H264 codec requires FFmpeg for proper decoding. Without it, OpenCV cannot decode the H264 stream.

### Solutions

#### Solution 1: Use HTTP/MJPEG Instead (Recommended - Immediate)

HTTP streams use MJPEG format which doesn't require special codecs.

```powershell
python src/main.py

# When prompted for camera source, select: 2
# When prompted for URL, enter:
http://192.168.0.107:8080/video
# OR
http://192.168.0.107:8080/mjpegfeed
```

**Advantages:**
- ✅ Works immediately without FFmpeg
- ✅ No codec dependency
- ✅ More stable connection
- ❌ Slightly lower quality than H264
- ❌ Uses more bandwidth

#### Solution 2: Install FFmpeg (Enables H264)

If you want to keep using RTSP H264:

**Option A: Using Chocolatey (if installed)**
```powershell
choco install ffmpeg
```

**Option B: Using Windows Package Manager**
```powershell
winget install FFmpeg
```

**Option C: Manual Download**
1. Download from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to Windows PATH
4. Restart your PC

**Verify installation:**
```powershell
ffmpeg -version
```

Once FFmpeg is installed, restart the application - OpenCV will automatically use it.

#### Solution 3: Try Alternative RTSP Format

Some IP Webcam versions support MPEG4 which is easier to decode:

```powershell
python src/main.py

# Select: 2
# Enter: rtsp://192.168.0.107:8080/mpeg4
# OR: rtsp://192.168.0.107:554/stream
```

#### Solution 4: Upgrade OpenCV with Codec Support

```powershell
pip uninstall opencv-python -y
pip install opencv-contrib-python
```

This version includes more codecs and might resolve H264 issues.

## Automatic Fallback Behavior (New)

The application now automatically tries to detect RTSP issues and offers fallback:

### How It Works

1. **RTSP Connection Attempt**
   - Tries UDP transport first
   - Falls back to TCP transport if UDP fails
   - Tests for valid frames

2. **Black Frame Detection**
   - Monitors frame brightness
   - If >30 consecutive frames are mostly black
   - Warns user about codec issue
   - Suggests HTTP stream alternative

3. **HTTP Fallback** (Automatic)
   - If RTSP completely fails
   - Automatically extracts IP and port from RTSP URL
   - Tries: `/video`, `/mjpegfeed`, `/stream` endpoints
   - Connects to first working URL

### Example Output

```
[RTSP] Attempting connection to: rtsp://192.168.0.107:8080/h264_ulaw.sdp
[RTSP] Trying UDP transport...
[RTSP] ✓ Connected via UDP!

[WAIT] Waiting for valid frames from stream...
[WARNING] Receiving mostly black frames - possible codec issue
[HINT] Try using HTTP stream instead:
  http://192.168.0.107:8080/video
```

## Manual URL Testing

Use the built-in URL tester to find working URLs:

```powershell
python test_phone_camera.py 192.168.0.107
```

This will:
- Test all common IP Webcam URLs
- Test all common DroidCam URLs
- Test all common generic RTSP URLs
- Report which ones work
- Show frame sizes for working URLs

## IP Webcam Specific URLs

### By Priority (Recommended Order)

1. **HTTP (Most Stable)**
   ```
   http://192.168.0.107:8080/video
   http://192.168.0.107:8080/mjpegfeed
   ```

2. **RTSP H264 (with FFmpeg)**
   ```
   rtsp://192.168.0.107:8080/h264_ulaw.sdp      # RECOMMENDED with FFmpeg
   rtsp://192.168.0.107:8080/h264_pcm.sdp       # Alternative
   ```

3. **RTSP MPEG4 (no codec needed)**
   ```
   rtsp://192.168.0.107:8080/mpeg4
   rtsp://192.168.0.107:554/stream
   ```

## DroidCam URLs

```powershell
# Main stream
rtsp://192.168.1.50:4747/mjpegfeed

# Alternative formats
http://192.168.1.50:4747/mjpegfeed
rtsp://192.168.1.50:4747/video
rtsp://192.168.1.50:4747/h264
```

## Common Issues and Fixes

### Issue: "Failed to open camera"

**Cause:** URL is incorrect or app not running on phone

**Fix:**
1. Verify IP Webcam "Start server" is running
2. Test URL in browser: `http://192.168.0.107:8080/`
3. Run: `python test_phone_camera.py 192.168.0.107`
4. Check firewall isn't blocking port 8080

### Issue: "Timeout waiting for frames"

**Cause:** Network latency or stream buffering

**Fix:**
1. Ensure phone is on same WiFi network
2. Reduce phone camera resolution in IP Webcam settings
3. Move phone and PC closer together (WiFi strength)
4. Try HTTP instead of RTSP (less buffering)

### Issue: "Connection Refused"

**Cause:** Port blocked or app not listening

**Fix:**
1. Verify correct IP: `ipconfig` on phone (Settings → WiFi)
2. Verify correct port (usually 8080 for IP Webcam)
3. Check Windows Firewall: Allow port 8080
4. Restart IP Webcam app

### Issue: "URL Failed" from test script

**Cause:** URL format incorrect for your app/setup

**Fix:**
1. Check IP Webcam version (different versions use different URLs)
2. Try all 6 suggested URLs in order
3. Check IP Webcam settings for exact URL format
4. Use web browser to verify URL works first

## Performance Tips

### For Better Video Quality
- Use RTSP H264 if you have FFmpeg installed
- Ensure good WiFi signal (5GHz preferred)
- Close other bandwidth-heavy apps

### For Lower Latency
- Use HTTP/MJPEG (less buffering)
- Reduce phone camera resolution
- Use 5GHz WiFi if available
- Disable unnecessary detection modules (OCR, face recognition)

### For Stability
- Use HTTP/MJPEG over RTSP
- Ensure phone has good WiFi connection
- Keep phone away from microwave/interference
- Monitor logs for repeated errors

## Advanced: Network Diagnostics

### Check WiFi Signal Strength

**Windows PowerShell:**
```powershell
netsh wlan show interfaces
# Look for "Signal" percentage
```

### Check Network Latency

```powershell
ping -n 10 192.168.0.107
# Average RTT should be <50ms
```

### Check Firewall

```powershell
# Allow port 8080 through Windows Defender Firewall
netsh advfirewall firewall add rule name="IP Webcam" dir=in action=allow protocol=tcp localport=8080
```

## Checking FFmpeg Installation

### Verify FFmpeg is Available to OpenCV

```python
import cv2
info = cv2.getBuildInformation()
print(info)

# Look for "Video I/O" section
# Should show: YES (ffmpeg)
# If shows: NO or N/A - FFmpeg not detected
```

## Emergency: Manual RTSP URL Discovery

If auto-test doesn't work, IP Webcam shows these in the app:

1. Open **IP Webcam** on phone
2. Note the IP and port at top of screen
3. Scroll to find format options:
   - **H.264/uLaw over RTSP**: Shows exact URL
   - **H.264/HQ PCM over RTSP**: Shows exact URL
   - **H.264/baseline over RTSP**: Alternative format
   - **MJPEG over HTTP**: Shows HTTP URL

4. Copy exact URL and use in application

## Logs and Debugging

### Check Application Logs

The application prints detailed logs. Look for:

- `[RTSP]` messages: Show connection attempts and transports
- `[HTTP]` messages: Show HTTP fallback attempts
- `[WARNING]` messages: Show detected issues
- `[HINT]` messages: Show suggested fixes

### Save Frames for Analysis

```powershell
# During application run, press 's' to save current frame
# Frames saved to: logs/frame_<timestamp>.jpg
```

### Check Frame Directory

```powershell
dir logs/
# Shows all saved frames and system state when saved
```

## Still Having Issues?

Try this checklist in order:

- [ ] Phone is connected to same WiFi as PC
- [ ] IP Webcam app is running and showing "Server started"
- [ ] Can access `http://192.168.0.107:8080/` in web browser
- [ ] Run `python test_phone_camera.py 192.168.0.107` - at least one URL works
- [ ] Copy working URL from test script into application
- [ ] Try HTTP URL first if any RTSP URL fails
- [ ] Check WiFi signal strength (should be >50%)
- [ ] Restart IP Webcam app
- [ ] Restart PC
- [ ] Install FFmpeg if you want H264 support
- [ ] Update OpenCV: `pip install --upgrade opencv-python`

## Performance Comparison

| Method | Quality | Latency | Compatibility | FFmpeg Needed |
|--------|---------|---------|---------------|----|
| HTTP/MJPEG | Medium | Low | Excellent | No |
| RTSP H264 | High | Medium | Good* | **Yes** |
| RTSP MPEG4 | Good | Medium | Fair | No |

*Good with FFmpeg, poor without (causes black screen)

---

## Next Steps

1. **If RTSP works**: Enjoy RTSP H264 quality
2. **If RTSP black screen**: Try HTTP URL
3. **If HTTP works**: You're good! (slightly lower quality but stable)
4. **If both fail**: Check network connectivity and firewall

---

**Updated:** November 2024
**Status:** With automatic fallback support
