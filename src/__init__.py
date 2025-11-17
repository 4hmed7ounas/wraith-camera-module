"""
Multi-Detection System Package
Comprehensive real-time system for face recognition, object detection, and OCR.
"""

from .face_recognition_module import FaceRecognitionSystem
from .object_detection_module import ObjectDetectionSystem
from .ocr_module import OCRSystem
from .main import MultiDetectionSystem

__all__ = [
    'FaceRecognitionSystem',
    'ObjectDetectionSystem',
    'OCRSystem',
    'MultiDetectionSystem'
]
