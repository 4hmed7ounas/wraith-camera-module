#!/usr/bin/env python3
"""
PC Testing Wrapper for Raspberry Pi 5 Nameplate Reader
Allows you to test the system on Windows/Linux/Mac before deploying to Pi

Usage:
    python test_on_pc.py          # Use default camera (0)
    python test_on_pc.py --camera 1   # Use camera 1
    python test_on_pc.py --help   # Show all options
"""

import cv2
import sys
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def detect_cameras():
    """Detect available cameras on the system."""
    cameras = []
    for i in range(5):  # Check cameras 0-4
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                cameras.append(i)
                logger.info(f"✓ Camera {i} detected: {frame.shape}")
            cap.release()
    return cameras


def list_available_cameras():
    """List all available cameras and let user choose."""
    logger.info("\n" + "="*60)
    logger.info("DETECTING AVAILABLE CAMERAS...")
    logger.info("="*60)

    cameras = detect_cameras()

    if not cameras:
        logger.error("✗ No cameras detected!")
        logger.info("\nTroubleshooting:")
        logger.info("1. Check if camera is connected")
        logger.info("2. Try different camera indices: 0, 1, 2, etc.")
        logger.info("3. Restart your PC")
        return None

    logger.info(f"\n✓ Found {len(cameras)} camera(s): {cameras}")

    if len(cameras) == 1:
        return cameras[0]

    # Let user choose
    logger.info("\nSelect camera:")
    for i, cam in enumerate(cameras):
        logger.info(f"  {i}: Camera {cam}")

    try:
        choice = int(input(f"Enter choice (0-{len(cameras)-1}): "))
        if 0 <= choice < len(cameras):
            return cameras[choice]
    except (ValueError, IndexError):
        pass

    logger.warning("Invalid choice, using camera 0")
    return cameras[0]


def test_camera(camera_id=0):
    """Test camera capture and basic video display."""
    logger.info("\n" + "="*60)
    logger.info(f"TESTING CAMERA {camera_id}...")
    logger.info("="*60)

    cap = cv2.VideoCapture(camera_id)

    if not cap.isOpened():
        logger.error(f"✗ Failed to open camera {camera_id}")
        return False

    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    logger.info(f"Resolution: {cap.get(cv2.CAP_PROP_FRAME_WIDTH):.0f}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT):.0f}")
    logger.info(f"FPS: {cap.get(cv2.CAP_PROP_FPS):.0f}")

    # Test frame capture
    logger.info("\nCapturing test frames...")
    for i in range(5):
        ret, frame = cap.read()
        if not ret:
            logger.error(f"✗ Failed to read frame {i}")
            cap.release()
            return False
        logger.info(f"  Frame {i+1}: {frame.shape}, dtype={frame.dtype}")

    cap.release()
    logger.info("✓ Camera test successful!")
    return True


def check_dependencies():
    """Check if all required packages are installed."""
    logger.info("\n" + "="*60)
    logger.info("CHECKING DEPENDENCIES...")
    logger.info("="*60)

    dependencies = {
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'ultralytics': 'ultralytics',
        'paddleocr': 'paddleocr',
        'paddlepaddle': 'paddlepaddle'
    }

    missing = []

    for module, package in dependencies.items():
        try:
            __import__(module)
            logger.info(f"✓ {module}")
        except ImportError:
            logger.error(f"✗ {module} (install: pip install {package})")
            missing.append(package)

    if missing:
        logger.error(f"\n✗ Missing packages: {', '.join(missing)}")
        logger.info("\nInstall with:")
        logger.info(f"  pip install {' '.join(missing)}")
        return False

    logger.info("\n✓ All dependencies installed!")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='PC Testing Wrapper for Raspberry Pi 5 Plate Reader'
    )
    parser.add_argument('--camera', type=int, default=None,
                        help='Camera index (0, 1, etc.)')
    parser.add_argument('--no-detect', action='store_true',
                        help='Skip camera detection, use camera 0')
    parser.add_argument('--skip-plate-reader', action='store_true',
                        help='Only test dependencies and camera, skip plate reader')

    args = parser.parse_args()

    # Step 1: Check dependencies
    if not check_dependencies():
        logger.error("\n⚠ Please install missing dependencies and try again")
        return

    # Step 2: Find camera
    if args.no_detect:
        camera_id = args.camera or 0
    elif args.camera is not None:
        camera_id = args.camera
    else:
        camera_id = list_available_cameras()
        if camera_id is None:
            return

    # Step 3: Test camera
    if not test_camera(camera_id):
        logger.error("\n⚠ Camera test failed. Check your setup.")
        return

    # Step 4: Run full plate reader
    if not args.skip_plate_reader:
        logger.info("\n" + "="*60)
        logger.info("RUNNING FULL PLATE READER...")
        logger.info("="*60)
        logger.info("Importing rpi5_plate_reader module...")

        try:
            from rpi5_plate_reader import PlateReaderPipeline

            logger.info("\n✓ PlateReaderPipeline imported successfully")
            logger.info("\nInitializing pipeline...")

            pipeline = PlateReaderPipeline(
                camera_id=camera_id,
                model_path="yolov8n.pt",
                conf_threshold=0.5,
                target_fps=15
            )

            logger.info("✓ Pipeline initialized!")
            logger.info("\nStarting real-time plate reader...")
            logger.info("Press 'q' in the window to quit\n")

            pipeline.run()

        except ImportError as e:
            logger.error(f"✗ Failed to import rpi5_plate_reader: {e}")
            logger.info("\nMake sure rpi5_plate_reader.py is in the same directory")
            return
        except Exception as e:
            logger.error(f"✗ Plate reader error: {e}")
            return

    logger.info("\n" + "="*60)
    logger.info("✓ PC TEST COMPLETE")
    logger.info("="*60)
    logger.info("\nPC Test Results:")
    logger.info("  ✓ Dependencies installed")
    logger.info(f"  ✓ Camera {camera_id} working")
    if not args.skip_plate_reader:
        logger.info("  ✓ Plate reader running")

    logger.info("\nYou can now deploy to Raspberry Pi 5!")


if __name__ == "__main__":
    main()
