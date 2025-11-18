"""
Object Detection Module (Lightweight Version)
Fast YOLOv8 nano model for real-time detection.
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple, Dict
import warnings

warnings.filterwarnings('ignore')

class ObjectDetectionSystem:
    """
    Lightweight object detection using YOLOv8 nano model.
    """

    def __init__(self, model_name: str = "yolov8n.pt", confidence_threshold: float = 0.5):
        """
        Initialize object detection.

        Args:
            model_name: YOLOv8 model (nano by default for speed)
            confidence_threshold: Minimum confidence for detections
        """
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.class_names = {}
        self.frame_skip = 3
        self.frame_count = 0
        self.process_frame_count = 0
        self.cached_detections = []
        self.cached_frame = None

        try:
            # Load YOLOv8 model (downloads if not present)
            print(f"[INFO] Loading YOLOv8 model: {model_name}")
            self.model = YOLO(model_name)
            self.class_names = self.model.names
            print(f"[INFO] Model loaded successfully with {len(self.class_names)} classes")
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            raise

    def detect_objects(self, frame: np.ndarray) -> Tuple[List[Dict], np.ndarray]:
        """
        Detect objects in the frame using YOLOv8.

        Args:
            frame: Input video frame

        Returns:
            Tuple of (detections list, annotated frame)
        """
        if self.model is None:
            return [], frame

        self.process_frame_count += 1

        # Use cached results for skipped frames
        if self.process_frame_count % self.frame_skip != 0:
            if self.cached_frame is not None:
                annotated_frame = self.draw_detections(frame, self.cached_detections)
                return self.cached_detections, annotated_frame
            return [], frame

        try:
            # Run inference with optimizations
            results = self.model(
                frame,
                verbose=False,
                conf=self.confidence_threshold,
                half=True,  # Use FP16 for faster inference
                device='cpu'  # Explicitly set device
            )

            detections = []

            # Process results
            if results and len(results) > 0:
                result = results[0]

                # Extract bounding boxes and confidence scores
                for box in result.boxes:
                    # Get box coordinates
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = self.class_names.get(class_id, "Unknown")

                    detection = {
                        'x1': x1,
                        'y1': y1,
                        'x2': x2,
                        'y2': y2,
                        'confidence': confidence,
                        'class_id': class_id,
                        'class_name': class_name,
                        'width': x2 - x1,
                        'height': y2 - y1
                    }
                    detections.append(detection)

            # Cache results
            self.cached_detections = detections
            self.cached_frame = frame.copy()

            # Annotate frame
            annotated_frame = self.draw_detections(frame, detections)

            return detections, annotated_frame

        except Exception as e:
            print(f"[ERROR] Object detection failed: {e}")
            return [], frame

    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw bounding boxes and labels for detected objects.

        Args:
            frame: Input video frame
            detections: List of detection dictionaries

        Returns:
            Frame with drawn detections
        """
        for detection in detections:
            x1, y1 = detection['x1'], detection['y1']
            x2, y2 = detection['x2'], detection['y2']
            class_name = detection['class_name']
            confidence = detection['confidence']

            # Draw bounding box
            color = (0, 255, 0)  # Green for objects
            thickness = 2
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

            # Prepare label
            label = f"{class_name}: {confidence:.2f}"

            # Get text size for background
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            thickness_text = 1
            text_size = cv2.getTextSize(label, font, font_scale, thickness_text)[0]

            # Draw label background
            label_y = y1 - 10 if y1 > 30 else y2 + 25
            cv2.rectangle(frame,
                         (x1, label_y - text_size[1] - 4),
                         (x1 + text_size[0] + 4, label_y + 2),
                         color, cv2.FILLED)

            # Put text
            cv2.putText(frame, label, (x1 + 2, label_y - 2),
                       font, font_scale, (255, 255, 255), thickness_text)

        return frame

    def filter_detections(self, detections: List[Dict], class_names: List[str]) -> List[Dict]:
        """
        Filter detections by specific class names.

        Args:
            detections: List of detection dictionaries
            class_names: List of class names to keep

        Returns:
            Filtered list of detections
        """
        return [d for d in detections if d['class_name'] in class_names]

    def get_class_statistics(self, detections: List[Dict]) -> Dict[str, int]:
        """
        Get statistics about detected classes.

        Args:
            detections: List of detection dictionaries

        Returns:
            Dictionary with class counts
        """
        stats = {}
        for detection in detections:
            class_name = detection['class_name']
            stats[class_name] = stats.get(class_name, 0) + 1
        return stats

    def get_available_models(self) -> List[str]:
        """
        Get list of available YOLOv8 models.

        Returns:
            List of model names
        """
        return [
            "yolov8n.pt",   # Nano (fastest, least accurate)
            "yolov8s.pt",   # Small
            "yolov8m.pt",   # Medium
            "yolov8l.pt",   # Large
            "yolov8x.pt",   # Extra Large (slowest, most accurate)
        ]

    def get_available_classes(self) -> List[str]:
        """
        Get list of available object classes.

        Returns:
            List of class names the model can detect
        """
        return list(self.class_names.values()) if self.class_names else []

    def process_frame(self, frame: np.ndarray) -> Tuple[List[Dict], np.ndarray]:
        """
        Main frame processing function for object detection.

        Args:
            frame: Input video frame

        Returns:
            Tuple of (detections, annotated_frame)
        """
        detections, annotated_frame = self.detect_objects(frame)
        return detections, annotated_frame
