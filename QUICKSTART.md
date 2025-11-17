# Quick Start Guide

Get the Multi-Detection System running in 5 minutes!

## Step 1: Run Setup Script (One-time only)

### Windows
```bash
setup.bat
```

### macOS/Linux
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- ✅ Create and activate virtual environment
- ✅ Install all dependencies
- ✅ Create required directories

**Note:** First-time installation takes 10-15 minutes (downloading models).

## Step 2: Activate Virtual Environment

Every time you use the project:

### Windows
```bash
venv\Scripts\activate
```

### macOS/Linux
```bash
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

## Step 3: Run the Application

```bash
python src/main.py
```

## Step 4: Use the Application

A webcam window will open showing:
- 🟩 **Green boxes** = Recognized faces
- 🟥 **Red boxes** = Unknown faces
- 🟩 **Green boxes** = Detected objects
- 🟦 **Blue boxes** = Detected text (OCR)

### When you see an unknown face:
```
[FACE] Unknown face detected!
Enter name (or press Enter to skip):
```

Type a name and press Enter. That face will be remembered next time!

### Keyboard Controls

| Key | What it does |
|-----|--------------|
| `q` | Quit the app |
| `s` | Save current frame |
| `t` | Toggle OCR on/off |

## That's it! 🎉

Your multi-detection system is running with:
- ✅ Face recognition with dynamic labeling
- ✅ Real-time object detection (80+ objects)
- ✅ Text/sign recognition (OCR)

## Troubleshooting

### "No camera found"
- Make sure your webcam is connected
- Try changing `camera_id: 0` to `camera_id: 1` in `src/main.py`

### "Very slow FPS"
- Press `t` to disable OCR (speeds up significantly)
- Or edit `src/main.py` and change `'yolov8n.pt'` to reduce model size

### "Python not found"
- Install Python 3.8+ from https://www.python.org/
- Make sure to check "Add Python to PATH" during installation

## Next Steps

For more detailed information, see [README.md](README.md):
- Configuration options
- Performance optimization
- Advanced usage
- Customization

## File Structure

```
camera-module/
├── venv/              ← Virtual environment (created by setup)
├── src/               ← All Python code
│   ├── main.py        ← Run this file
│   ├── face_recognition_module.py
│   ├── object_detection_module.py
│   └── ocr_module.py
├── data/              ← Your saved faces go here
├── logs/              ← Saved screenshots go here
├── requirements.txt   ← Dependencies
├── README.md          ← Full documentation
└── QUICKSTART.md      ← This file
```

## Common Questions

**Q: What happens to the faces I recognize?**
A: They're saved in `data/face_encodings.pkl` for future use.

**Q: Can I recognize faces from images instead of webcam?**
A: Yes! You can modify `src/main.py` to load images instead of webcam input.

**Q: Can I use a USB camera instead of built-in webcam?**
A: Yes! Change `camera_id: 0` to `camera_id: 1` or higher in `src/main.py`.

**Q: Does it work on Mac/Linux?**
A: Yes! The setup script works on all platforms.

**Q: Can I improve recognition accuracy?**
A: Yes! Make sure faces are clear, well-lit, and frontal. Delete `data/face_encodings.pkl` and re-register faces for best results.

---

Enjoy using the Multi-Detection System! 🚀
