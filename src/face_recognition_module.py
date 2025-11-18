"""
Face Recognition Module
Handles face detection, encoding, storage, and recognition with dynamic labeling.
Uses deepface for face detection and embedding generation.
"""

import os
import pickle
import json
import numpy as np
import cv2
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

try:
    from deepface import DeepFace
except ImportError:
    print("[WARNING] deepface not installed. Install with: pip install deepface")
    DeepFace = None

class FaceRecognitionSystem:
    """
    Manages face detection, encoding, storage, and real-time recognition using deepface.
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

        # Load existing encodings if available
        self.load_encodings()

        # Face detection parameters
        self.process_frame_count = 0
        self.frame_skip = 5  # Process every 5th frame for performance
        self.model_name = "VGG-Face"  # Model for face embedding
        self.distance_threshold = 0.5  # Distance threshold for matching

        # Cache last detected faces
        self.cached_face_locations = []
        self.cached_face_names = []
        self.cache_valid_frames = 0

    def load_encodings(self):
        """Load face encodings and names from file."""
        if self.encodings_file.exists():
            try:
                with open(self.encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data.get('encodings', [])
                    self.known_face_names = data.get('names', [])
                print(f"[INFO] Loaded {len(self.known_face_names)} known faces from file")
            except Exception as e:
                print(f"[ERROR] Failed to load encodings: {e}")
        else:
            print("[INFO] No existing face encodings found. Starting fresh.")

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
            print(f"[INFO] Saved {len(self.known_face_names)} face encodings")
        except Exception as e:
            print(f"[ERROR] Failed to save encodings: {e}")

    def detect_faces(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect faces in the frame using deepface.

        Args:
            frame: Input video frame

        Returns:
            List of detected faces with bounding boxes
        """
        if DeepFace is None:
            return []

        try:
            # Detect faces in the frame
            faces = DeepFace.extract_faces(img_path=frame, enforce_detection=False)

            detections = []
            for face in faces:
                facial_area = face['facial_area']
                x = facial_area['x']
                y = facial_area['y']
                w = facial_area['w']
                h = facial_area['h']

                detection = {
                    'x1': x,
                    'y1': y,
                    'x2': x + w,
                    'y2': y + h,
                    'confidence': face.get('confidence', 0.9)
                }
                detections.append(detection)

            return detections
        except Exception as e:
            # Silently fail if no faces detected or error occurs
            return []

    def get_face_encoding(self, frame: np.ndarray, face_location: Dict) -> Optional[np.ndarray]:
        """
        Get face embedding/encoding for a detected face.

        Args:
            frame: Input video frame
            face_location: Face location dictionary

        Returns:
            Face encoding vector or None
        """
        if DeepFace is None:
            return None

        try:
            x1, y1, x2, y2 = face_location['x1'], face_location['y1'], face_location['x2'], face_location['y2']

            # Extract face region
            face_crop = frame[y1:y2, x1:x2]

            if face_crop.size == 0:
                return None

            # Get embedding
            embedding_objs = DeepFace.represent(
                img_path=face_crop,
                model_name=self.model_name,
                enforce_detection=False
            )

            if embedding_objs and len(embedding_objs) > 0:
                return np.array(embedding_objs[0]['embedding'])

            return None
        except Exception as e:
            return None

    def recognize_faces(self, face_encodings: List[np.ndarray],
                       tolerance: float = None) -> List[str]:
        """
        Recognize faces by comparing with known face encodings.

        Args:
            face_encodings: List of face encodings to recognize
            tolerance: Distance threshold (not used, kept for compatibility)

        Returns:
            List of names for each face encoding
        """
        face_names = []

        for face_encoding in face_encodings:
            if len(self.known_face_encodings) == 0:
                face_names.append("UNKNOWN")
                continue

            # Calculate distances
            distances = []
            for known_encoding in self.known_face_encodings:
                # Use Euclidean distance
                distance = np.linalg.norm(face_encoding - known_encoding)
                distances.append(distance)

            min_distance = min(distances)
            best_match_index = distances.index(min_distance)

            # If best match is close enough
            if min_distance < self.distance_threshold:
                name = self.known_face_names[best_match_index]
            else:
                name = "UNKNOWN"

            face_names.append(name)

        return face_names

    def add_face(self, face_encoding: np.ndarray, name: str):
        """
        Add a new known face to the system.

        Args:
            face_encoding: Face encoding vector
            name: Name/label for the face
        """
        self.known_face_encodings.append(face_encoding)
        self.known_face_names.append(name)
        self.save_encodings()
        print(f"[INFO] Added new face: {name}")

    def process_frame(self, frame: np.ndarray,
                     callback_unknown_face=None) -> Tuple[List[Dict], List[str]]:
        """
        Main frame processing function for face detection and recognition.

        Args:
            frame: Input video frame
            callback_unknown_face: Callback function to handle unknown faces

        Returns:
            Tuple of (face_locations, face_names)
        """
        # Skip frames for performance
        self.process_frame_count += 1

        # Use cached results for skipped frames
        if self.process_frame_count % self.frame_skip != 0:
            if self.cache_valid_frames > 0:
                self.cache_valid_frames -= 1
                return self.cached_face_locations, self.cached_face_names
            return [], []

        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

        # Detect faces
        face_locations = self.detect_faces(small_frame)

        if len(face_locations) == 0:
            self.cached_face_locations = []
            self.cached_face_names = []
            self.cache_valid_frames = 0
            return [], []

        # Scale back face locations to original size
        for face_loc in face_locations:
            face_loc['x1'] *= 2
            face_loc['y1'] *= 2
            face_loc['x2'] *= 2
            face_loc['y2'] *= 2

        # Get encodings for detected faces
        face_encodings = []
        for face_location in face_locations:
            encoding = self.get_face_encoding(frame, face_location)
            if encoding is not None:
                face_encodings.append(encoding)
            else:
                face_encodings.append(np.zeros(128))  # Dummy encoding if extraction fails

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
        self.cached_face_locations = face_locations
        self.cached_face_names = face_names
        self.cache_valid_frames = self.frame_skip - 1

        return face_locations, face_names

    def draw_faces(self, frame: np.ndarray,
                   face_locations: List[Dict],
                   face_names: List[str]) -> np.ndarray:
        """
        Draw rectangles and labels for detected faces.

        Args:
            frame: Input video frame
            face_locations: List of face locations
            face_names: List of face names/labels

        Returns:
            Frame with drawn faces
        """
        for face_location, name in zip(face_locations, face_names):
            x1, y1, x2, y2 = face_location['x1'], face_location['y1'], face_location['x2'], face_location['y2']

            # Draw rectangle
            color = (0, 255, 0) if name != "UNKNOWN" else (0, 0, 255)
            thickness = 2
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

            # Draw label background
            label_y = y1 - 10 if y1 > 30 else y2 + 25
            cv2.rectangle(frame, (x1, label_y - 25), (x2, label_y), color, cv2.FILLED)

            # Put text
            cv2.putText(frame, name, (x1 + 6, label_y - 6),
                       cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

        return frame

    def get_statistics(self) -> Dict:
        """Get current system statistics."""
        return {
            'known_faces': len(self.known_face_names),
            'face_names': self.known_face_names.copy()
        }
