# Face Recognition Naming - Fixed!

## What Was Wrong

Face detection was working, but **the app was NOT asking for person's name** when an unknown face was detected.

## Why It Happened

The face naming callback was **disabled for performance reasons** in the original code:

```python
# OLD CODE (disabled)
callback_unknown_face=None  # Disable unknown face prompt for performance
```

## What Changed

✅ **Face naming is now ENABLED** with smart rate limiting:

```python
# NEW CODE (enabled with cooldown)
callback_unknown_face=self._get_face_name_with_cooldown
```

## What Was Added

✅ **Terminal Logging** - Detection messages now display to console
✅ **Rate Limited Logging** - Prevents spam (logs max once per 2 seconds per face)
✅ **Visual Feedback** - Shows ✓ for known faces, ❓ for unknown faces

## How It Works Now

1. **Face detected** → Logged to terminal (e.g., `[FACE] ✓ Detected: Alice`)
2. **Unknown face detected** → App prompts you for name
3. **You enter name** → Face is stored and recognized next time
4. **Rate limiting** → Only prompts once every 3 seconds (prevents spam)
5. **Stored persistently** → Face encodings saved to `data/face_encodings.pkl`

## Usage

### Example Terminal Output - Unknown Face:

```
[INFO] Starting video processing...
[FACE] ❓ Detected: UNKNOWN face (1 face)
[FACE] Unknown face detected!
Enter name (or press Enter to skip): Alice
[FACE] Registered: Alice
```

### Example Terminal Output - Known Face:

```
[INFO] Starting video processing...
[FACE] ✓ Detected: Alice
[FACE] ✓ Detected: Alice
```

### Visual Display:

```
Video window shows:
- Green box around face
- Name label: "Alice" (for known faces)
- Name label: "UNKNOWN" (for unknown faces)
```

## Rate Limiting Explanation

### Face Naming Prompt (3-second cooldown)

**Why the 3-second cooldown?**
- Without it: App would spam prompts if multiple unknown faces appear
- With it: Only prompts once every 3 seconds maximum
- Still responsive enough for real use

### Terminal Logging (2-second cooldown)

**Why the 2-second cooldown for logs?**
- Avoids terminal spam if face stays in view continuously
- Still shows every time a NEW face is detected
- Shows every 2 seconds if same face stays visible

**Example:**
```
Time 0s: [FACE] ✓ Detected: Alice    ← First detection
Time 1s: (same face, no log)
Time 2s: [FACE] ✓ Detected: Alice    ← Logs again (2s passed)
```

## Customization

**Change face prompt cooldown:** Edit `src/main.py` line ~99:

```python
self.face_prompt_cooldown = 3  # Change 3 to whatever you want (in seconds)
```

Options:
- `1` = prompt every 1 second (very frequent)
- `5` = prompt every 5 seconds (less frequent)
- `10` = prompt every 10 seconds (rarely)

**Change terminal logging cooldown:** Edit `src/main.py` line ~104:

```python
self.face_log_cooldown = 2  # Change 2 to whatever you want (in seconds)
```

Options:
- `0.5` = log every 0.5 seconds (very frequent)
- `5` = log every 5 seconds (less frequent)

## Files Modified

- [src/main.py](src/main.py) - Enabled face naming with rate limiting

## Testing It

```powershell
python src/main.py

# Use your webcam (option 1) or phone camera (option 2)
# When unknown face appears:
# Enter name and press Enter
# Next time same face appears: It should show the name in green box
```

## How Face Recognition Works

1. **Detection**: Finds faces in frame (every 2nd frame for performance)
2. **Encoding**: Creates unique fingerprint for each face
3. **Comparison**: Compares new faces to stored faces
4. **Naming**: Assigns known names or asks for new names
5. **Storage**: Saves face encodings to file for next time

## Face Encoding Storage

Face data is stored in: `data/face_encodings.pkl`

**To reset and start fresh:**
```powershell
# Delete the file
del data/face_encodings.pkl

# Restart app - all faces become "unknown" again
python src/main.py
```

## Troubleshooting

### Issue: "App still not asking for names"

**Solution:**
1. Make sure face detection is enabled (it is by default)
2. Check that face is clearly visible and frontal
3. Ensure good lighting
4. Check console output for `[FACE]` messages

### Issue: "Asked for name but then still shows unknown"

**Possible causes:**
- Different lighting/angle changes appearance
- Face encoding wasn't stored properly
- Check `data/face_encodings.pkl` exists

**Fix:**
- Register same face multiple times from different angles
- Or delete encodings and retrain

### Issue: "Prompts too frequently / not frequently enough"

**Solution:** Adjust cooldown in `src/main.py`:

```python
self.face_prompt_cooldown = 5  # Change to desired seconds
```

## Performance Notes

- Face detection: Every 2 frames (optimized)
- Face encoding: Only for detected faces
- Naming prompt: Only for unknown faces, max once per 3 seconds
- **Total overhead: Minimal** - works smoothly with phone camera

## Summary

✅ Face naming is now enabled - **App asks for unknown face names**
✅ Terminal logging enabled - **Detections displayed in console**
✅ Smart rate limiting prevents spam - **No console flooding**
✅ Faces stored and recognized persistently - **Remembers across sessions**
✅ Works with both local webcam and phone camera - **Phone camera ready**
✅ Customizable cooldowns - **Adjust to your preference**

## What You'll See Now

**In Terminal (Console):**
```
[FACE] ❓ Detected: UNKNOWN face (1 face)
[FACE] Unknown face detected!
Enter name (or press Enter to skip): Alice
[FACE] Registered: Alice
[FACE] ✓ Detected: Alice
```

**In Video Window:**
- Green box around detected face
- Name label showing "Alice" or "UNKNOWN"

Enjoy using face recognition! 🎉
