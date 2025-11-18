# Fixing Black Screen Issue with IP Webcam

If you're seeing a black screen but the app is connected, it's likely a codec issue with RTSP H264 streaming.

## Quick Fix: Use HTTP Stream Instead

The easiest solution is to use IP Webcam's HTTP stream instead of RTSP:

```powershell
python src/main.py
# Select: 2
# Enter: http://192.168.0.107:8080/video
```

**This should work immediately without codec issues!**

## Why HTTP Works Better

- ✅ Motion JPEG (MJPEG) format - easy to decode
- ✅ No codec dependencies
- ✅ Works with any OpenCV version
- ✅ More stable than RTSP
- ✗ Slightly lower quality than H264
- ✗ Uses more bandwidth

## If You Want to Use RTSP H264

The H264 codec issues occur because OpenCV needs proper FFmpeg support. To fix:

### Option 1: Install FFmpeg (Recommended)

1. **Download FFmpeg:**
   - Go to https://ffmpeg.org/download.html
   - Download Windows build (or use chocolatey)

2. **Using Chocolatey (if installed):**
   ```powershell
   choco install ffmpeg
   ```

3. **Using Direct Download:**
   - Download from ffmpeg.org
   - Extract to `C:\ffmpeg`
   - Add to PATH: `C:\ffmpeg\bin`

4. **Verify installation:**
   ```powershell
   ffmpeg -version
   ```

5. **Restart your application** - OpenCV will now use FFmpeg for H264 decoding

### Option 2: Rebuild OpenCV with FFmpeg Support

More advanced - use pip to install opencv-contrib-python which includes codec support:

```powershell
pip uninstall opencv-python -y
pip install opencv-contrib-python
```

This version includes all codecs and might resolve H264 issues.

### Option 3: Use Different RTSP Format

Some IP Webcam versions support MPEG4 which is easier to decode:

```powershell
python src/main.py
# Select: 2
# Enter: rtsp://192.168.0.107:8080/mpeg4
```

## Troubleshooting Checklist

- [ ] Try HTTP stream first: `http://192.168.0.107:8080/video`
- [ ] If that works, you're good! No need for RTSP
- [ ] If HTTP doesn't work, check Phone Link connection
- [ ] Make sure IP Webcam "Start server" is pressed
- [ ] Verify phone and PC are on same WiFi
- [ ] Try lowering phone camera resolution in IP Webcam settings
- [ ] Restart IP Webcam app
- [ ] Restart your PC

## Testing Codec Support

Check if your OpenCV has H264 support:

```python
import cv2
print(cv2.getBuildInformation())
# Look for "Video I/O" section
# If FFmpeg is enabled, it will show: YES (ffmpeg)
# If not, it will show: NO or N/A
```

## Performance Comparison

| Format | Speed | Quality | Bandwidth |
|--------|-------|---------|-----------|
| MJPEG (HTTP) | ⚡⚡⚡ | ⭐⭐ | High |
| H264 (RTSP) | ⚡⚡ | ⭐⭐⭐⭐ | Low |
| MPEG4 (RTSP) | ⚡⚡ | ⭐⭐⭐ | Medium |

**Recommendation:** Use HTTP/MJPEG for best compatibility, RTSP H264 if you have FFmpeg installed.

## Still Having Issues?

1. Run the URL tester:
   ```powershell
   python test_phone_camera.py 192.168.0.107
   ```

2. Test URL in VLC:
   - Open VLC Media Player
   - Media → Open Network Stream
   - Paste your URL
   - If it plays in VLC, it should work in our app (with proper codec support)

3. Check IP Webcam logs:
   - IP Webcam shows connection info at the top
   - Verify it says "Connected"
   - Check the bitrate/resolution

## Summary

**For immediate working solution:** Use `http://192.168.0.107:8080/video`

**For better quality:** Install FFmpeg and use RTSP H264

**For troubleshooting:** Run `python test_phone_camera.py 192.168.0.107`
