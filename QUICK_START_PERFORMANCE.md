# Quick Start - Performance & Resolution Guide

## TL;DR - How to Make It Faster

1. **Run the app:**
   ```powershell
   python src/main.py
   ```

2. **When asked for camera source:**
   ```
   Select camera source (1 or 2, press Enter for 1): 2
   ```

3. **When asked for performance mode:**
   ```
   Performance Mode Selection:
     1. High Quality (1280x720) - For good hardware
     2. Balanced (640x480) - Recommended for phone camera
     3. Fast (480x360) - For slower systems
     4. Ultra Fast (320x240) - Minimum, extremely fast

   Select performance mode (1-4, press Enter for 2): 2
   ```
   **← Press Enter (default is 2 - RECOMMENDED)**

4. **Enter your phone camera URL:**
   ```
   Enter Phone Camera URL: http://192.168.0.107:8080/video
   ```

5. **Done!** App starts with 640x480 resolution = **SMOOTH & FAST** ✓

---

## Why 640x480?

| Resolution | Speed | Quality | Stutter? |
|-----------|-------|---------|----------|
| 1280x720 | 5-8 FPS | Excellent | ✗ YES |
| **640x480** | **15-20 FPS** | **Good** | **✓ NO** |
| 480x360 | 20-30 FPS | Okay | ✓ NO |
| 320x240 | 30 FPS | Poor | ✓ NO |

---

## If It's Still Slow

### Step 1: Check You Selected Mode 2
- Default is "2" - just press Enter
- If you see "640x480" in the output, you're good

### Step 2: Try Mode 3 (480x360)
- Run app again
- When asked for mode, enter: `3`

### Step 3: Try Mode 4 (320x240)
- Run app again
- When asked for mode, enter: `4`

### Step 4: Disable OCR
- Press 't' while app is running
- Disables text recognition (saves 10-20ms per frame)

---

## During Operation

```
Keyboard controls:
q = Quit
s = Save current frame
t = Toggle OCR on/off (improves speed if disabled)
```

---

## Performance Tips

### ✅ DO:
- Use Mode 2 (640x480) as default
- Use HTTP URL instead of RTSP
- Ensure good WiFi signal
- Close other apps

### ✗ DON'T:
- Use 1280x720 (too slow for phone camera)
- Use RTSP H264 without FFmpeg
- Have lots of other apps running
- Disable resolution selection (stick with the mode choice)

---

## What Happens

```
Before (1280x720):
├─ Video stutters constantly
├─ Faces detected with delay
└─ Overall FPS: 5-8

After (640x480):
├─ Smooth video playback
├─ Real-time face detection
└─ Overall FPS: 15-20 ✓
```

---

## One More Thing

**Webapp would be SLOWER!**

Local processing >> Network streaming

---

## Quick Settings Summary

```powershell
# Run app
python src/main.py

# Camera: 2 (phone)
# Performance: 2 (Balanced - 640x480) ← DEFAULT
# URL: http://192.168.0.107:8080/video

# Result: Smooth operation! 🎉
```

That's it! Enjoy fast, smooth face detection!
