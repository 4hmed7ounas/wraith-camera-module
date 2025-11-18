"""
Main Application
Integrates Face Recognition, Object Detection, and OCR modules for real-time processing.
"""

import cv2
import numpy as np
import sys
from pathlib import Path
from typing import Optional, Callable
import time

# Import custom modules
from face_recognition_module import FaceRecognitionSystem
from object_detection_module import ObjectDetectionSystem
from ocr_module import OCRSystem

class MultiDetectionSystem:
    """
    Main system that integrates all detection modules (face, object, OCR).
    """

    def __init__(self,
                 enable_face_recognition: bool = True,
                 enable_object_detection: bool = True,
                 enable_ocr: bool = True,
                 yolo_model: str = "yolov8n.pt",
                 camera_id: int = 0,
                 frame_width: int = 1280,
                 frame_height: int = 720,
                 fps_limit: int = 30):
        """
        Initialize the multi-detection system.

        Args:
            enable_face_recognition: Enable face recognition module
            enable_object_detection: Enable object detection module
            enable_ocr: Enable OCR module
            yolo_model: YOLOv8 model to use
            camera_id: Camera device ID
            frame_width: Frame width
            frame_height: Frame height
            fps_limit: Maximum FPS to process
        """
        self.enable_face_recognition = enable_face_recognition
        self.enable_object_detection = enable_object_detection
        self.enable_ocr = enable_ocr

        self.camera_id = camera_id
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.fps_limit = fps_limit
        self.frame_time = 1 / fps_limit

        # Initialize modules
        self.face_system = None
        self.object_system = None
        self.ocr_system = None

        self._initialize_modules()

        # Statistics
        self.frame_count = 0
        self.fps = 0
        self.last_time = time.time()
        self.fps_update_time = time.time()

    def _initialize_modules(self):
        """Initialize enabled detection modules."""
        print("[INFO] Initializing detection modules...")

        if self.enable_face_recognition:
            try:
                self.face_system = FaceRecognitionSystem()
                print("[INFO] Face recognition module initialized")
            except Exception as e:
                print(f"[WARNING] Failed to initialize face recognition: {e}")
                self.enable_face_recognition = False

        if self.enable_object_detection:
            try:
                self.object_system = ObjectDetectionSystem(model_name="yolov8n.pt")
                print("[INFO] Object detection module initialized")
            except Exception as e:
                print(f"[WARNING] Failed to initialize object detection: {e}")
                self.enable_object_detection = False

        if self.enable_ocr:
            try:
                self.ocr_system = OCRSystem(languages=['en'])
                print("[INFO] OCR module initialized")
            except Exception as e:
                print(f"[WARNING] Failed to initialize OCR: {e}")
                self.enable_ocr = False

    def _ask_for_name(self) -> Optional[str]:
        """
        Ask user to enter name for unknown face.
        Returns the name or None if user cancels.
        """
        print("\n[FACE] Unknown face detected!")
        user_input = input("Enter name (or press Enter to skip): ").strip()
        return user_input if user_input else None

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Process frame through all enabled modules.

        Args:
            frame: Input video frame

        Returns:
            Processed frame with all detections
        """
        # Face Recognition (highest priority - runs every 5 frames)
        if self.enable_face_recognition and self.face_system:
            try:
                face_locations, face_names = self.face_system.process_frame(
                    frame,
                    callback_unknown_face=None  # Disable unknown face prompt for performance
                )
                if face_locations:
                    frame = self.face_system.draw_faces(frame, face_locations, face_names)
            except Exception as e:
                print(f"[ERROR] Face recognition failed: {e}")

        # Object Detection (runs every 2 frames)
        if self.enable_object_detection and self.object_system:
            try:
                detections, frame = self.object_system.process_frame(frame)
            except Exception as e:
                print(f"[ERROR] Object detection failed: {e}")

        # OCR (Text Recognition) (lowest priority - runs every 10 frames)
        if self.enable_ocr and self.ocr_system:
            try:
                ocr_detections, frame = self.ocr_system.process_frame(
                    frame,
                    confidence_threshold=0.3,
                    filter_size=True,
                    show_confidence=False  # Disable for performance
                )
            except Exception as e:
                print(f"[ERROR] OCR failed: {e}")

        return frame

    def draw_info(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw system information on frame.

        Args:
            frame: Input video frame

        Returns:
            Frame with information overlay
        """
        # Update FPS more frequently for accurate display
        current_time = time.time()
        time_diff = current_time - self.fps_update_time

        if time_diff >= 0.5:  # Update every 0.5 seconds
            self.fps = int(self.frame_count / time_diff)
            self.frame_count = 0
            self.fps_update_time = current_time

        # Draw info text
        info_y = 30
        info_color = (0, 255, 0)  # Green for better visibility
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2

        # FPS with background
        fps_text = f"FPS: {self.fps}"
        text_size = cv2.getTextSize(fps_text, font, font_scale, thickness)[0]
        cv2.rectangle(frame, (5, 5), (15 + text_size[0], info_y + 5), (0, 0, 0), cv2.FILLED)
        cv2.putText(frame, fps_text, (10, info_y), font, font_scale, info_color, thickness)

        # Active modules
        modules = []
        if self.enable_face_recognition:
            modules.append("Face")
        if self.enable_object_detection:
            modules.append("Objects")
        if self.enable_ocr:
            modules.append("OCR")

        modules_text = f"Modules: {' | '.join(modules)}"
        text_size = cv2.getTextSize(modules_text, font, font_scale, thickness)[0]
        cv2.rectangle(frame, (5, info_y + 10), (15 + text_size[0], info_y + 45), (0, 0, 0), cv2.FILLED)
        cv2.putText(frame, modules_text, (10, info_y + 35), font, font_scale, info_color, thickness)

        return frame

    def run(self):
        """Main application loop - capture and process video from webcam."""
        # Open webcam
        cap = cv2.VideoCapture(self.camera_id)

        if not cap.isOpened():
            print("[ERROR] Failed to open camera!")
            return

        # Set camera properties with optimizations
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        cap.set(cv2.CAP_PROP_FPS, self.fps_limit)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer to reduce lag

        print("[INFO] Camera opened successfully")
        print(f"[INFO] Resolution: {self.frame_width}x{self.frame_height}")
        print("[INFO] Starting video processing...")
        print("[INFO] Press 'q' to quit, 's' to save frame, 't' to toggle OCR")
        print()

        # ocr_enabled = self.enable_ocr

        try:
            while True:
                ret, frame = cap.read()

                if not ret:
                    print("[ERROR] Failed to read frame from camera")
                    break

                # Process frame through all modules
                frame = self.process_frame(frame)

                # Draw info overlay
                frame = self.draw_info(frame)

                # Display frame
                cv2.imshow("Multi-Detection System", frame)

                self.frame_count += 1

                # Handle keyboard input with minimal wait for responsiveness
                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):
                    print("\n[INFO] Quitting application...")
                    break
                elif key == ord('s'):
                    # Save current frame
                    filename = f"logs/frame_{int(time.time())}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"[INFO] Frame saved to {filename}")
                elif key == ord('t'):
                    # Toggle OCR
                    self.enable_ocr = not self.enable_ocr
                    status = "enabled" if self.enable_ocr else "disabled"
                    print(f"[INFO] OCR {status}")

        except KeyboardInterrupt:
            print("\n[INFO] Interrupted by user")
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
        finally:
            # Cleanup
            cap.release()
            cv2.destroyAllWindows()

            # Save face encodings
            if self.face_system:
                print("[INFO] Saving face encodings...")
                self.face_system.save_encodings()

            print("[INFO] Application closed")

    def get_statistics(self) -> dict:
        """Get system statistics."""
        stats = {
            'frame_count': self.frame_count,
            'fps': self.fps,
            'modules_enabled': {
                'face_recognition': self.enable_face_recognition,
                'object_detection': self.enable_object_detection,
                'ocr': self.enable_ocr
            }
        }

        if self.face_system:
            stats['faces'] = self.face_system.get_statistics()

        return stats


def main():
    """
    Main entry point for the application.
    """
    print("=" * 60)
    print("Multi-Detection System - Face Recognition, Objects & OCR")
    print("=" * 60)
    print()

    # Configuration
    config = {
        'enable_face_recognition': True,
        'enable_object_detection': True,
        'enable_ocr': True,
        'yolo_model': 'yolov8n.pt',  # Using nano for speed
        'camera_id': 0,
        'frame_width': 1280,
        'frame_height': 720,
        'fps_limit': 30
    }

    # Create and run system
    system = MultiDetectionSystem(**config)
    system.run()


if __name__ == "__main__":
    main()
