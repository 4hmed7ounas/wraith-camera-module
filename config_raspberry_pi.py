"""
Raspberry Pi 5 Optimized Configuration
Use this configuration for running on Raspberry Pi with limited resources
"""

# ==================== FACE RECOGNITION ====================
FACE_RECOGNITION = {
    'enabled': True,
    'tolerance': 0.6,
    'frame_skip': 10,           # Process every 10th frame (higher for Pi)
    'model': 'hog',             # HOG is much faster than CNN on Pi
    'encodings_file': 'data/face_encodings.pkl',
    'confidence_display': False,
}

# ==================== OBJECT DETECTION ====================
OBJECT_DETECTION = {
    'enabled': True,
    'model': 'yolov8n.pt',      # Nano model only - smallest and fastest
    'confidence_threshold': 0.6, # Higher threshold = fewer detections = faster
    'iou_threshold': 0.45,
}

# ==================== OCR (TEXT RECOGNITION) ====================
OCR = {
    'enabled': False,            # Disable OCR by default - very resource intensive
    'languages': ['en'],
    'confidence_threshold': 0.4,
    'filter_by_size': True,
    'min_text_width': 30,
    'min_text_height': 20,
    'gpu_acceleration': False,   # Pi doesn't have CUDA
}

# ==================== CAMERA SETTINGS ====================
CAMERA = {
    'device_id': 0,              # 0 = Pi Camera or USB camera
    'frame_width': 640,          # Lower resolution for Pi (was 1280)
    'frame_height': 480,         # Lower resolution for Pi (was 720)
    'fps_limit': 15,             # Lower FPS target (was 30)
}

# ==================== DISPLAY SETTINGS ====================
DISPLAY = {
    'window_title': 'Multi-Detection System - Raspberry Pi',
    'show_fps': True,
    'show_module_info': True,
    'show_instructions': False,  # Reduce overlay for performance
    'thickness_face': 1,         # Thinner lines = faster drawing
    'thickness_object': 1,
    'thickness_text': 1,
}

# ==================== PERFORMANCE TUNING ====================
PERFORMANCE = {
    'skip_frame_processing': True,      # Skip processing on alternate frames
    'reduce_resolution': True,          # Process at lower res, upscale display
    'max_faces_per_frame': 5,          # Limit to 5 faces max
    'max_objects_per_frame': 20,       # Limit to 20 objects max
    'max_ocr_detections': 10,          # Limit OCR detections
    'use_threading': False,             # Single-threaded for stability
}

# ==================== LOGGING ====================
LOGGING = {
    'save_frames': False,        # Disable to save SD card writes
    'save_detections': False,    # Disable to save SD card writes
    'log_directory': 'logs',
    'verbose': False,            # Less console output
}

# ==================== RASPBERRY PI SPECIFIC ====================
RASPBERRY_PI = {
    'use_picamera2': True,       # Use new Pi Camera library if available
    'enable_hardware_accel': True, # Use Pi's GPU for video decode
    'reduce_cpu_usage': True,    # Additional CPU optimizations
    'thermal_throttle_temp': 70, # Throttle if temp exceeds 70°C
}

# ==================== QUICK PRESETS ====================

def get_preset(preset_name):
    """
    Get a predefined configuration preset for Raspberry Pi
    """
    presets = {
        'pi_performance': {  # Maximum performance, minimal features
            'FACE_RECOGNITION': {'enabled': False},
            'OBJECT_DETECTION': {'enabled': True, 'model': 'yolov8n.pt', 'confidence_threshold': 0.7},
            'OCR': {'enabled': False},
            'CAMERA': {'frame_width': 320, 'frame_height': 240, 'fps_limit': 20},
        },
        'pi_balanced': {  # Balanced performance and features (RECOMMENDED)
            'FACE_RECOGNITION': {'enabled': True, 'frame_skip': 15},
            'OBJECT_DETECTION': {'enabled': True, 'model': 'yolov8n.pt', 'confidence_threshold': 0.6},
            'OCR': {'enabled': False},
            'CAMERA': {'frame_width': 640, 'frame_height': 480, 'fps_limit': 15},
        },
        'pi_faces_only': {  # Only face recognition
            'FACE_RECOGNITION': {'enabled': True, 'frame_skip': 8},
            'OBJECT_DETECTION': {'enabled': False},
            'OCR': {'enabled': False},
            'CAMERA': {'frame_width': 640, 'frame_height': 480, 'fps_limit': 20},
        },
        'pi_objects_only': {  # Only object detection
            'FACE_RECOGNITION': {'enabled': False},
            'OBJECT_DETECTION': {'enabled': True, 'model': 'yolov8n.pt'},
            'OCR': {'enabled': False},
            'CAMERA': {'frame_width': 640, 'frame_height': 480, 'fps_limit': 20},
        },
        'pi_minimal': {  # Absolute minimum for testing
            'FACE_RECOGNITION': {'enabled': False},
            'OBJECT_DETECTION': {'enabled': True, 'model': 'yolov8n.pt', 'confidence_threshold': 0.8},
            'OCR': {'enabled': False},
            'CAMERA': {'frame_width': 320, 'frame_height': 240, 'fps_limit': 30},
        },
    }
    return presets.get(preset_name, presets['pi_balanced'])


if __name__ == '__main__':
    print("Raspberry Pi 5 Configuration")
    print(f"Face Recognition: {FACE_RECOGNITION['enabled']}")
    print(f"Object Detection: {OBJECT_DETECTION['enabled']}")
    print(f"OCR: {OCR['enabled']}")
    print(f"Camera: {CAMERA['frame_width']}x{CAMERA['frame_height']} @ {CAMERA['fps_limit']} FPS")
    print()
    print("Available Pi presets:")
    print("  - pi_performance: Max speed, minimal features")
    print("  - pi_balanced: Recommended for Pi 5 (default)")
    print("  - pi_faces_only: Face detection only")
    print("  - pi_objects_only: Object detection only")
    print("  - pi_minimal: Absolute minimal config for testing")
