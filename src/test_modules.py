"""
Module Testing Script
Test individual components to debug issues
"""

import sys
import cv2
import numpy as np
from pathlib import Path

def test_opencv():
    """Test OpenCV installation and camera access"""
    print("\n" + "="*60)
    print("Testing OpenCV")
    print("="*60)

    try:
        import cv2
        print(f"✓ OpenCV version: {cv2.__version__}")

        # Try to open camera
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✓ Camera access OK")
                print(f"  Frame size: {frame.shape}")
            else:
                print("✗ Failed to read from camera")
            cap.release()
        else:
            print("✗ Failed to open camera (device may be in use)")

    except Exception as e:
        print(f"✗ OpenCV test failed: {e}")
        return False

    return True


def test_face_recognition():
    """Test face_recognition library"""
    print("\n" + "="*60)
    print("Testing Face Recognition Library")
    print("="*60)

    try:
        import face_recognition
        print(f"✓ face_recognition library loaded")

        # Test on a dummy image
        dummy_img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        locations = face_recognition.face_locations(dummy_img, model="hog")
        print(f"✓ Face detection works (found {len(locations)} faces in dummy image)")

        if len(locations) == 0:
            print("  (This is expected for random noise)")

    except ImportError as e:
        print(f"✗ face_recognition import failed: {e}")
        print("  Try: pip install face-recognition")
        return False
    except Exception as e:
        print(f"✗ face_recognition test failed: {e}")
        return False

    return True


def test_yolo():
    """Test YOLOv8 installation"""
    print("\n" + "="*60)
    print("Testing YOLOv8 Object Detection")
    print("="*60)

    try:
        from ultralytics import YOLO
        print(f"✓ ultralytics library loaded")

        # Load nano model (smallest)
        print("  Loading YOLOv8 nano model (this may take a minute on first run)...")
        model = YOLO('yolov8n.pt')
        print(f"✓ YOLOv8 model loaded successfully")

        # Test on dummy image
        dummy_img = np.random.randint(0, 256, (640, 640, 3), dtype=np.uint8)
        results = model(dummy_img, verbose=False)
        print(f"✓ Object detection works")

    except ImportError as e:
        print(f"✗ ultralytics import failed: {e}")
        print("  Try: pip install ultralytics")
        return False
    except Exception as e:
        print(f"✗ YOLOv8 test failed: {e}")
        return False

    return True


def test_ocr():
    """Test EasyOCR installation"""
    print("\n" + "="*60)
    print("Testing OCR (EasyOCR)")
    print("="*60)

    try:
        import easyocr
        print(f"✓ easyocr library loaded")

        # Load reader (this downloads model on first run)
        print("  Loading OCR reader (this may take a minute on first run)...")
        reader = easyocr.Reader(['en'], gpu=False)
        print(f"✓ OCR reader loaded successfully")

        # Test on dummy image with text
        dummy_img = np.ones((200, 200, 3), dtype=np.uint8) * 255
        cv2.putText(dummy_img, "TEST", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2)
        results = reader.readtext(dummy_img)
        print(f"✓ Text detection works (found {len(results)} text regions)")

    except ImportError as e:
        print(f"✗ easyocr import failed: {e}")
        print("  Try: pip install easyocr")
        return False
    except Exception as e:
        print(f"✗ OCR test failed: {e}")
        return False

    return True


def test_modules():
    """Test custom modules"""
    print("\n" + "="*60)
    print("Testing Custom Modules")
    print("="*60)

    try:
        from face_recognition_module import FaceRecognitionSystem
        print(f"✓ FaceRecognitionSystem imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import FaceRecognitionSystem: {e}")
        return False

    try:
        from object_detection_module import ObjectDetectionSystem
        print(f"✓ ObjectDetectionSystem imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import ObjectDetectionSystem: {e}")
        return False

    try:
        from ocr_module import OCRSystem
        print(f"✓ OCRSystem imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import OCRSystem: {e}")
        return False

    return True


def test_dependencies():
    """Test all dependencies"""
    print("\n" + "="*60)
    print("Testing Dependencies")
    print("="*60)

    dependencies = [
        'cv2',
        'numpy',
        'PIL',
        'face_recognition',
        'ultralytics',
        'torch',
        'torchvision',
        'easyocr',
        'scipy',
    ]

    missing = []

    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✓ {dep}")
        except ImportError:
            print(f"✗ {dep} (missing)")
            missing.append(dep)

    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False

    return True


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  Multi-Detection System - Module Test Suite".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")

    tests = [
        ("Dependencies", test_dependencies),
        ("OpenCV & Camera", test_opencv),
        ("Face Recognition", test_face_recognition),
        ("YOLOv8 Object Detection", test_yolo),
        ("EasyOCR Text Recognition", test_ocr),
        ("Custom Modules", test_modules),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ Unexpected error in {test_name}: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed! Your system is ready.")
        print("\nRun the application with: python src/main.py")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  1. Reinstall dependencies: pip install -r requirements.txt")
        print("  2. Make sure camera is not in use by other applications")
        print("  3. Check internet connection (for model downloads)")
        print("  4. Update pip: python -m pip install --upgrade pip")
        return 1


if __name__ == "__main__":
    sys.exit(main())
