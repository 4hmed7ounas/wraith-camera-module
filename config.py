"""
Configuration file for Multi-Detection System
Edit this file to customize the application behavior
"""

# ==================== FACE RECOGNITION ====================
FACE_RECOGNITION = {
    'enabled': True,
    'tolerance': 0.6,           # Lower = stricter matching (0.3-0.6 recommended)
    'frame_skip': 2,            # Process every Nth frame (higher = faster but less responsive)
    'model': 'hog',             # 'hog' (faster) or 'cnn' (more accurate but slower)
    'encodings_file': 'data/face_encodings.pkl',
    'confidence_display': True, # Show confidence scores
}

# ==================== OBJECT DETECTION ====================
OBJECT_DETECTION = {
    'enabled': True,
    'model': 'yolov8n.pt',      # yolov8n (fast), yolov8s, yolov8m, yolov8l, yolov8x (accurate)
    'confidence_threshold': 0.5, # Only show detections with confidence >= this
    'iou_threshold': 0.45,      # Intersection over Union threshold
}

# ==================== OCR (TEXT RECOGNITION) ====================
OCR = {
    'enabled': True,
    'languages': ['en'],        # ['en', 'es', 'fr', 'de'] for multiple languages
    'confidence_threshold': 0.3, # Only show text with confidence >= this
    'filter_by_size': True,     # Remove small text (noise reduction)
    'min_text_width': 20,       # Minimum text width in pixels
    'min_text_height': 15,      # Minimum text height in pixels
    'gpu_acceleration': False,  # Use GPU if available (requires CUDA)
}

# ==================== CAMERA SETTINGS ====================
CAMERA = {
    'device_id': 0,             # 0 = default/built-in, 1, 2... = USB cameras
    'frame_width': 1280,        # Width in pixels
    'frame_height': 720,        # Height in pixels
    'fps_limit': 30,            # Target frames per second
}

# ==================== DISPLAY SETTINGS ====================
DISPLAY = {
    'window_title': 'Multi-Detection System',
    'show_fps': True,           # Display FPS counter
    'show_module_info': True,   # Show which modules are active
    'show_instructions': True,  # Show keyboard controls
    'thickness_face': 2,        # Face rectangle thickness
    'thickness_object': 2,      # Object rectangle thickness
    'thickness_text': 2,        # Text rectangle thickness
}

# ==================== PERFORMANCE TUNING ====================
PERFORMANCE = {
    'skip_frame_processing': False,     # Skip every other frame
    'reduce_resolution': False,         # Process at lower resolution, upscale for display
    'max_faces_per_frame': 10,         # Maximum faces to process per frame
    'max_objects_per_frame': 100,      # Maximum objects to process per frame
    'max_ocr_detections': 50,          # Maximum OCR regions to process
}

# ==================== LOGGING ====================
LOGGING = {
    'save_frames': True,        # Save detected frames to logs/
    'save_detections': True,    # Save detection statistics
    'log_directory': 'logs',
    'verbose': True,            # Print detailed information
}

# ==================== ADVANCED ====================
ADVANCED = {
    'face_recognition_model': 'hog',     # 'hog' or 'cnn'
    'face_detection_upsampling': 1,      # Increase for smaller faces (slower)
    'face_encoding_jitter': 1,           # Accuracy vs speed tradeoff
    'yolo_device': '0',                  # GPU device ID (0 = first GPU, -1 = CPU)
}

# ==================== QUICK PRESETS ====================

def get_preset(preset_name):
    """
    Get a predefined configuration preset
    Usage: config = get_preset('performance')
    """
    presets = {
        'default': {
            'FACE_RECOGNITION': {'enabled': True, 'frame_skip': 2, 'model': 'hog'},
            'OBJECT_DETECTION': {'enabled': True, 'model': 'yolov8n.pt'},
            'OCR': {'enabled': True},
            'CAMERA': {'frame_width': 1280, 'frame_height': 720, 'fps_limit': 30},
        },
        'performance': {  # Fastest - sacrifices some accuracy
            'FACE_RECOGNITION': {'enabled': True, 'frame_skip': 4, 'model': 'hog'},
            'OBJECT_DETECTION': {'enabled': True, 'model': 'yolov8n.pt', 'confidence_threshold': 0.6},
            'OCR': {'enabled': False},
            'CAMERA': {'frame_width': 640, 'frame_height': 480, 'fps_limit': 30},
        },
        'accuracy': {  # Most accurate - slower processing
            'FACE_RECOGNITION': {'enabled': True, 'frame_skip': 1, 'model': 'cnn'},
            'OBJECT_DETECTION': {'enabled': True, 'model': 'yolov8m.pt', 'confidence_threshold': 0.4},
            'OCR': {'enabled': True},
            'CAMERA': {'frame_width': 1920, 'frame_height': 1080, 'fps_limit': 30},
        },
        'faces_only': {  # Only face recognition
            'FACE_RECOGNITION': {'enabled': True, 'frame_skip': 2},
            'OBJECT_DETECTION': {'enabled': False},
            'OCR': {'enabled': False},
            'CAMERA': {'frame_width': 1280, 'frame_height': 720, 'fps_limit': 30},
        },
        'objects_only': {  # Only object detection
            'FACE_RECOGNITION': {'enabled': False},
            'OBJECT_DETECTION': {'enabled': True, 'model': 'yolov8n.pt'},
            'OCR': {'enabled': False},
            'CAMERA': {'frame_width': 1280, 'frame_height': 720, 'fps_limit': 30},
        },
        'ocr_only': {  # Only text recognition
            'FACE_RECOGNITION': {'enabled': False},
            'OBJECT_DETECTION': {'enabled': False},
            'OCR': {'enabled': True},
            'CAMERA': {'frame_width': 1280, 'frame_height': 720, 'fps_limit': 30},
        },
    }
    return presets.get(preset_name, presets['default'])


if __name__ == '__main__':
    # Example: Print current configuration
    print("Current Configuration:")
    print(f"Face Recognition: {FACE_RECOGNITION['enabled']}")
    print(f"Object Detection: {OBJECT_DETECTION['enabled']}")
    print(f"OCR: {OCR['enabled']}")
    print(f"Camera: {CAMERA['frame_width']}x{CAMERA['frame_height']} @ {CAMERA['fps_limit']} FPS")
    print()
    print("Available presets: default, performance, accuracy, faces_only, objects_only, ocr_only")
    print("Example: config = get_preset('performance')")
