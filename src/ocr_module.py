"""
OCR (Optical Character Recognition) Module
Handles text detection and recognition from images/video frames.
"""

import cv2
import numpy as np
import easyocr
from typing import List, Tuple, Dict
import threading

class OCRSystem:
    """
    Manages text detection and recognition using EasyOCR.
    """

    def __init__(self, languages: List[str] = ['en'], gpu: bool = False):
        """
        Initialize the OCR system.

        Args:
            languages: List of languages to recognize (e.g., ['en', 'es', 'fr'])
            gpu: Whether to use GPU acceleration (requires CUDA)
        """
        self.languages = languages
        self.gpu = gpu
        self.reader = None
        self.lock = threading.Lock()

        try:
            print(f"[INFO] Loading EasyOCR reader for languages: {languages}")
            self.reader = easyocr.Reader(languages, gpu=gpu)
            print("[INFO] OCR reader loaded successfully")
        except Exception as e:
            print(f"[ERROR] Failed to load OCR reader: {e}")
            raise

    def detect_text(self, frame: np.ndarray,
                   confidence_threshold: float = 0.3) -> List[Dict]:
        """
        Detect and recognize text in the frame.

        Args:
            frame: Input video frame
            confidence_threshold: Minimum confidence for text detection

        Returns:
            List of detected text with bounding boxes
        """
        if self.reader is None:
            return []

        detections = []

        try:
            with self.lock:
                # Run OCR
                results = self.reader.readtext(frame)

            # Process results
            for (bbox, text, confidence) in results:
                if confidence >= confidence_threshold:
                    # Convert bbox format (list of tuples to coordinates)
                    bbox = np.array(bbox, dtype=np.int32)
                    x_coords = bbox[:, 0]
                    y_coords = bbox[:, 1]

                    x1, y1 = int(np.min(x_coords)), int(np.min(y_coords))
                    x2, y2 = int(np.max(x_coords)), int(np.max(y_coords))

                    detection = {
                        'text': text.strip(),
                        'confidence': confidence,
                        'x1': x1,
                        'y1': y1,
                        'x2': x2,
                        'y2': y2,
                        'bbox': bbox,
                        'width': x2 - x1,
                        'height': y2 - y1
                    }
                    detections.append(detection)

        except Exception as e:
            print(f"[ERROR] OCR detection failed: {e}")

        return detections

    def draw_text_detections(self, frame: np.ndarray,
                            detections: List[Dict],
                            show_confidence: bool = True) -> np.ndarray:
        """
        Draw bounding boxes and text labels on the frame.

        Args:
            frame: Input video frame
            detections: List of text detections
            show_confidence: Whether to show confidence scores

        Returns:
            Frame with drawn text detections
        """
        for detection in detections:
            bbox = detection['bbox']
            text = detection['text']
            confidence = detection['confidence']

            # Draw polygon around text
            color = (0, 255, 255)  # Cyan for text
            cv2.polylines(frame, [bbox], True, color, 2)

            # Prepare label
            label = f"{text}" if not show_confidence else f"{text} ({confidence:.2f})"

            # Get position for label
            x1, y1 = detection['x1'], detection['y1']
            label_y = y1 - 10 if y1 > 30 else detection['y2'] + 25

            # Get text size for background
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness_text = 1
            text_size = cv2.getTextSize(label, font, font_scale, thickness_text)[0]

            # Draw label background
            cv2.rectangle(frame,
                         (x1, label_y - text_size[1] - 4),
                         (x1 + text_size[0] + 4, label_y + 2),
                         color, cv2.FILLED)

            # Put text
            cv2.putText(frame, label, (x1 + 2, label_y - 2),
                       font, font_scale, (0, 0, 0), thickness_text)

        return frame

    def extract_text(self, detections: List[Dict]) -> str:
        """
        Extract all recognized text from detections.

        Args:
            detections: List of text detections

        Returns:
            Combined text string
        """
        if not detections:
            return ""
        return " ".join([d['text'] for d in detections])

    def filter_by_size(self, detections: List[Dict],
                      min_width: int = 20, min_height: int = 15) -> List[Dict]:
        """
        Filter text detections by minimum size to reduce noise.

        Args:
            detections: List of text detections
            min_width: Minimum text width
            min_height: Minimum text height

        Returns:
            Filtered list of detections
        """
        return [d for d in detections
                if d['width'] >= min_width and d['height'] >= min_height]

    def group_nearby_text(self, detections: List[Dict],
                         distance_threshold: int = 50) -> List[Dict]:
        """
        Group nearby text detections into lines/regions.

        Args:
            detections: List of text detections
            distance_threshold: Maximum distance between texts to group

        Returns:
            Grouped text detections
        """
        if not detections:
            return []

        # Sort by Y coordinate (top to bottom)
        sorted_detections = sorted(detections, key=lambda d: d['y1'])

        groups = []
        current_group = [sorted_detections[0]]

        for detection in sorted_detections[1:]:
            # Check if within distance threshold
            last_detection = current_group[-1]
            y_distance = abs(detection['y1'] - last_detection['y1'])

            if y_distance <= distance_threshold:
                current_group.append(detection)
            else:
                groups.append(current_group)
                current_group = [detection]

        if current_group:
            groups.append(current_group)

        # Merge groups
        merged = []
        for group in groups:
            combined_text = " ".join([d['text'] for d in group])
            y_positions = [d['y1'] for d in group]
            x_positions = [d['x1'] for d in group]

            merged_detection = {
                'text': combined_text,
                'x1': min(x_positions),
                'y1': min(y_positions),
                'x2': max([d['x2'] for d in group]),
                'y2': max([d['y2'] for d in group]),
                'confidence': np.mean([d['confidence'] for d in group])
            }
            merged.append(merged_detection)

        return merged

    def process_frame(self, frame: np.ndarray,
                     confidence_threshold: float = 0.3,
                     filter_size: bool = True,
                     show_confidence: bool = True) -> Tuple[List[Dict], np.ndarray]:
        """
        Main frame processing function for OCR.

        Args:
            frame: Input video frame
            confidence_threshold: Minimum confidence for text detection
            filter_size: Whether to filter by text size
            show_confidence: Whether to show confidence scores

        Returns:
            Tuple of (detections, annotated_frame)
        """
        detections = self.detect_text(frame, confidence_threshold)

        if filter_size:
            detections = self.filter_by_size(detections)

        annotated_frame = self.draw_text_detections(frame, detections, show_confidence)

        return detections, annotated_frame

    def get_statistics(self, detections: List[Dict]) -> Dict:
        """
        Get statistics about detected text.

        Args:
            detections: List of text detections

        Returns:
            Dictionary with statistics
        """
        if not detections:
            return {
                'total_detections': 0,
                'average_confidence': 0,
                'total_text': ""
            }

        return {
            'total_detections': len(detections),
            'average_confidence': np.mean([d['confidence'] for d in detections]),
            'total_text': self.extract_text(detections)
        }
