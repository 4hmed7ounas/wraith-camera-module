"""
ULTRA FAST VERSION - Object Detection Only
For maximum performance on any hardware
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from main import MultiDetectionSystem


def main():
    """
    Ultra-fast configuration - object detection only.
    """
    print("=" * 60)
    print("Multi-Detection System - FAST MODE")
    print("=" * 60)
    print()

    # Minimal configuration for maximum speed
    fast_config = {
        'enable_face_recognition': False,  # DISABLED
        'enable_object_detection': True,   # ONLY THIS
        'enable_ocr': False,               # DISABLED
        'yolo_model': 'yolov8n.pt',
        'camera_id': 0,
        'frame_width': 640,
        'frame_height': 480,
        'fps_limit': 30
    }

    print("[INFO] FAST MODE Configuration:")
    print("  - Face Recognition: DISABLED")
    print("  - Object Detection: ENABLED (YOLOv8-nano)")
    print("  - OCR: DISABLED")
    print(f"  - Resolution: {fast_config['frame_width']}x{fast_config['frame_height']}")
    print(f"  - Target FPS: {fast_config['fps_limit']}")
    print()
    print("[INFO] This should run smoothly on any hardware!")
    print()

    try:
        # Create and run system
        system = MultiDetectionSystem(**fast_config)
        system.run()
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Application failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
