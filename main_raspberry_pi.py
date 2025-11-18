"""
Raspberry Pi Optimized Main Application
Runs the multi-detection system with Pi-specific optimizations
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from main import MultiDetectionSystem
import config_raspberry_pi as config


def main():
    """
    Main entry point for Raspberry Pi deployment.
    """
    print("=" * 60)
    print("Multi-Detection System - Raspberry Pi 5 Edition")
    print("=" * 60)
    print()

    # Use Pi-optimized configuration (fast preset - objects only)
    pi_config = {
        'enable_face_recognition': False,  # Disabled - too slow for real-time
        'enable_object_detection': True,
        'enable_ocr': False,  # Disabled by default on Pi
        'yolo_model': 'yolov8n.pt',  # Nano model only
        'camera_id': 0,
        'frame_width': 640,    # Reduced from 1280
        'frame_height': 480,   # Reduced from 720
        'fps_limit': 30        # Increased from 15
    }

    print("[INFO] Configuration:")
    print(f"  - Resolution: {pi_config['frame_width']}x{pi_config['frame_height']}")
    print(f"  - Target FPS: {pi_config['fps_limit']}")
    print(f"  - Face Recognition: {pi_config['enable_face_recognition']}")
    print(f"  - Object Detection: {pi_config['enable_object_detection']}")
    print(f"  - OCR: {pi_config['enable_ocr']}")
    print()
    print("[INFO] Performance Tips for Raspberry Pi:")
    print("  - Press 't' to toggle OCR (disabled by default)")
    print("  - Lower resolution = better performance")
    print("  - Consider disabling face recognition if only detecting objects")
    print("  - Monitor CPU temperature with: vcgencmd measure_temp")
    print()

    try:
        # Create and run system
        system = MultiDetectionSystem(**pi_config)
        system.run()
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Application failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
