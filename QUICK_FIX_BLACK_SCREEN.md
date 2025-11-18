# Quick Fix: RTSP H264 Black Screen

## TL;DR - Immediate Solution

You have a black screen? **Try this RIGHT NOW:**

```powershell
python src/main.py

# When asked for camera source, select: 2
# When asked for URL, enter:
http://192.168.0.107:8080/video

# Should work immediately!
```

If that works, you're done! 🎉

---

## If HTTP Doesn't Work

### Step 1: Find Working URL
```powershell
python test_phone_camera.py 192.168.0.107
```

This will test 15+ different URL patterns and tell you which ones work.

### Step 2: Use the Working URL
Copy the URL from test results and use it in the application.

---

## Why RTSP Shows Black Screen

Your RTSP URL uses **H264 codec**, which requires **FFmpeg** to decode.

Without FFmpeg:
- ❌ Connection succeeds
- ❌ Frames are received
- ✅ But frames are all black (decode errors)

With FFmpeg:
- ✅ Everything works perfectly

---

## Option A: Keep Using HTTP (Simplest)

HTTP uses MJPEG format - **no special codec needed!**

**Pros:**
- ✅ Works immediately
- ✅ No FFmpeg install needed
- ✅ Stable connection

**Cons:**
- ❌ Slightly lower quality than H264
- ❌ Uses more bandwidth

**Use URL:** `http://192.168.0.107:8080/video`

---

## Option B: Install FFmpeg (Better Quality)

If you want H264 quality, install FFmpeg:

### Windows 10/11 (Easy Way):

```powershell
# If you have Chocolatey
choco install ffmpeg

# Or if you have Windows Package Manager
winget install FFmpeg

# Or manual: Download and extract to C:\ffmpeg
# Add C:\ffmpeg\bin to Windows PATH
```

### Then:

1. **Restart your PC** (important!)
2. Verify: `ffmpeg -version` in PowerShell
3. Run app again with RTSP URL

---

## Option C: Change RTSP Format

Try MPEG4 instead of H264 (might work without FFmpeg):

```powershell
python src/main.py

# Select: 2
# Enter: rtsp://192.168.0.107:8080/mpeg4
```

---

## What Changed in Your App

The app now:
1. **Detects** if you're getting all black frames
2. **Warns** you about the issue
3. **Suggests** using HTTP instead
4. **Automatically tries** HTTP if RTSP completely fails

So you should see helpful messages now instead of just black screen!

---

## Testing Your Fix

After installing FFmpeg or switching to HTTP:

```powershell
python src/main.py
# Select: 2
# Enter your URL

# You should see:
# [OK] Connected! Receiving frames...
# [INFO] Resolution: 1280x720
```

If you see video appearing - **it worked!**

---

## Still Showing Black Screen?

1. ✅ Try HTTP URL: `http://192.168.0.107:8080/video`
2. ✅ Run test script: `python test_phone_camera.py 192.168.0.107`
3. ✅ Check IP Webcam is actually running and "Start server" is pressed
4. ✅ Try different URL from test results
5. ✅ Reinstall FFmpeg if using RTSP

---

## Performance Notes

| Method | Quality | Latency | Best For |
|--------|---------|---------|----------|
| HTTP/MJPEG | Good | Low | **Most people** |
| RTSP H264 + FFmpeg | Excellent | Medium | High quality needed |
| RTSP MPEG4 | Very Good | Medium | Fallback option |

**Recommendation:** Use HTTP for stability, switch to RTSP H264 + FFmpeg only if you need higher quality.

---

## Still Having Issues?

See full guide: [TROUBLESHOOTING_RTSP_HTTP.md](TROUBLESHOOTING_RTSP_HTTP.md)

That guide has:
- Advanced diagnostics
- Network troubleshooting
- FFmpeg detailed installation
- All possible URL patterns
- Debugging tips

---

## Summary

| Problem | Solution | Time |
|---------|----------|------|
| Black screen | Try HTTP instead of RTSP | 30 sec |
| Want H264 quality | Install FFmpeg | 5 min |
| Don't know URL | Run `test_phone_camera.py` | 1 min |
| Still not working | See full troubleshooting guide | 10 min |
