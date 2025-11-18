"""
Face Recognition Module (Ultra-Lightweight Version)
Fast face detection using OpenCV Haar Cascades.
Optimized for real-time webcam processing on CPU.
"""

import os
import pickle
import numpy as np
import cv2
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class FaceRecognitionSystem:
    """
    Ultra-lightweight face detection and recognition using OpenCV Haar Cascades.
    No neural networks - pure classical computer vision.
    """

    def __init__(self, data_dir: str = "data", encodings_file: str = "face_encodings.pkl"):
        """
        Initialize the face recognition system.

        Args:
            data_dir: Directory to store face encodings
            encodings_file: File to store face encodings and names
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.encodings_file = self.data_dir / encodings_file
        self.known_face_encodings: List[np.ndarray] = []
        self.known_face_names: List[str] = []

        # Load Haar Cascade for face detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        # Load existing encodings
        self.load_encodings()

        # Performance optimization
        self.frame_skip = 2
        self.process_frame_count = 0
        self.last_detected_faces = []
        self.cache_frames = 0

    def load_encodings(self):
        """Load face encodings and names from file."""
        if self.encodings_file.exists():
            try:
                with open(self.encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data.get('encodings', [])
                    self.known_face_names = data.get('names', [])
                print(f"[FACE] Loaded {len(self.known_face_names)} known faces")
            except Exception as e:
                print(f"[FACE ERROR] Failed to load: {e}")
        else:
            print("[FACE] No existing faces. Starting fresh.")

    def save_encodings(self):
        """Save face encodings and names to file."""
        try:
            with open(self.encodings_file, 'wb') as f:
                data = {
                    'encodings': self.known_face_encodings,
                    'names': self.known_face_names,
                    'timestamp': datetime.now().isoformat()
                }
                pickle.dump(data, f)
            print(f"[FACE] Saved {len(self.known_face_names)} faces")
        except Exception as e:
            print(f"[FACE ERROR] Save failed: {e}")

    def get_face_encoding(self, face_crop: np.ndarray) -> np.ndarray:
        """
        Generate encoding from face using histogram + edge features.
        Very fast, no ML models needed.

        Args:
            face_crop: Cropped face region

        Returns:
            Face encoding vector
        """
        try:
            # Resize to standard 64x64
            face_resized = cv2.resize(face_crop, (64, 64))
            gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)

            # Histogram features (256 values)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist = cv2.normalize(hist, hist).flatten()

            # Edge features (256 values)
            edges = cv2.Canny(gray, 50, 150)
            edge_hist = cv2.calcHist([edges], [0], None, [256], [0, 256])
            edge_hist = cv2.normalize(edge_hist, edge_hist).flatten()

            # Combine (512 total features)
            encoding = np.concatenate([hist, edge_hist])
            return encoding

        except Exception:
            return np.zeros(512)

    def detect_faces(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect faces using Haar Cascade - very fast!

        Args:
            frame: Input video frame

        Returns:
            List of detected faces
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.3,
                minNeighbors=5,
                minSize=(30, 30)
            )

            detections = []
            for (x, y, w, h) in faces:
                detections.append({
                    'x1': x,
                    'y1': y,
                    'x2': x + w,
                    'y2': y + h,
                    'confidence': 0.8
                })

            return detections

        except Exception:
            return []

    def recognize_faces(self, face_encodings: List[np.ndarray]) -> List[str]:
        """Recognize faces by comparing encodings."""
        if len(self.known_face_encodings) == 0:
            return ["UNKNOWN"] * len(face_encodings)

        face_names = []

        for encoding in face_encodings:
            if encoding.sum() == 0:
                face_names.append("UNKNOWN")
                continue

            # Calculate distances to all known faces
            distances = []
            for known_encoding in self.known_face_encodings:
                distance = np.linalg.norm(encoding - known_encoding)
                distances.append(distance)

            min_distance = min(distances)
            best_match_idx = distances.index(min_distance)

            # Threshold for matching
            if min_distance < 100:
                name = self.known_face_names[best_match_idx]
            else:
                name = "UNKNOWN"

            face_names.append(name)

        return face_names

    def add_face(self, face_encoding: np.ndarray, name: str):
        """Add a new face to the system."""
        self.known_face_encodings.append(face_encoding)
        self.known_face_names.append(name)
        self.save_encodings()
        print(f"[FACE] Registered: {name}")

    def process_frame(self, frame: np.ndarray,
                     callback_unknown_face=None) -> Tuple[List[Dict], List[str]]:
        """
        Process frame for face detection and recognition.

        Args:
            frame: Input video frame
            callback_unknown_face: Callback for unknown faces

        Returns:
            Tuple of (face_locations, face_names)
        """
        self.process_frame_count += 1

        # Use cached results for skipped frames
        if self.process_frame_count % self.frame_skip != 0:
            if self.cache_frames > 0:
                self.cache_frames -= 1
                return self.last_detected_faces[0], self.last_detected_faces[1]
            return [], []

        # Detect faces
        face_locations = self.detect_faces(frame)

        if len(face_locations) == 0:
            self.last_detected_faces = ([], [])
            self.cache_frames = 0
            return [], []

        # Get encodings
        face_encodings = []
        for loc in face_locations:
            face_crop = frame[loc['y1']:loc['y2'], loc['x1']:loc['x2']]
            if face_crop.size > 0:
                encoding = self.get_face_encoding(face_crop)
                face_encodings.append(encoding)
            else:
                face_encodings.append(np.zeros(512))

        # Recognize faces
        face_names = self.recognize_faces(face_encodings)

        # Handle unknown faces
        if callback_unknown_face:
            for i, name in enumerate(face_names):
                if name == "UNKNOWN":
                    user_input = callback_unknown_face()
                    if user_input and user_input.strip():
                        face_names[i] = user_input.strip()
                        self.add_face(face_encodings[i], user_input.strip())

        # Cache results
        self.last_detected_faces = (face_locations, face_names)
        self.cache_frames = self.frame_skip - 1

        return face_locations, face_names

    def draw_faces(self, frame: np.ndarray,
                   face_locations: List[Dict],
                   face_names: List[str]) -> np.ndarray:
        """Draw faces on frame."""
        for loc, name in zip(face_locations, face_names):
            x1, y1, x2, y2 = loc['x1'], loc['y1'], loc['x2'], loc['y2']

            # Color: green for known, red for unknown
            color = (0, 255, 0) if name != "UNKNOWN" else (0, 0, 255)

            # Draw rectangle
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Draw label
            label_y = y1 - 10 if y1 > 30 else y2 + 25
            cv2.rectangle(frame, (x1, label_y - 25), (x2, label_y), color, -1)
            cv2.putText(frame, name, (x1 + 5, label_y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        return frame

    def get_statistics(self) -> Dict:
        """Get system statistics."""
        return {
            'known_faces': len(self.known_face_names),
            'face_names': self.known_face_names.copy()
        }
