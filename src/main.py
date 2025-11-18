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
import threading

# Import custom modules
from face_recognition_module import FaceRecognitionSystem
from object_detection_module import ObjectDetectionSystem
from ocr_module import OCRSystem
from http_camera_handler import HTTPCameraHandler


class ThreadedCameraReader:
    """
    Reads frames from camera in a separate thread to decouple I/O from processing.
    This prevents slow processing from blocking frame capture.
    """
    def __init__(self, camera_source, resolution=(640, 480)):
        self.camera_source = camera_source
        self.resolution = resolution
        self.frame = None
        self.running = False
        self.thread = None
        self.cap = None

    def start(self) -> bool:
        """Start the camera reader thread"""
        try:
            # Use DirectShow on Windows for faster I/O
            if isinstance(self.camera_source, int):
                try:
                    self.cap = cv2.VideoCapture(self.camera_source, cv2.CAP_DSHOW)
                except:
                    self.cap = cv2.VideoCapture(self.camera_source)

                # Set resolution and FPS
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)

            if not self.cap or not self.cap.isOpened():
                return False

            self.running = True
            self.thread = threading.Thread(target=self._read_frames, daemon=True)
            self.thread.start()
            return True

        except Exception as e:
            print(f"[THREADING] Failed to start camera reader: {e}")
            return False

    def _read_frames(self):
        """Continuously read frames from camera (runs in separate thread)"""
        while self.running:
            try:
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.frame = frame
                else:
                    time.sleep(0.01)  # Brief pause if no frame
            except Exception as e:
                print(f"[THREADING] Error reading frame: {e}")
                break

    def get_frame(self) -> tuple:
        """Get the latest frame (non-blocking)"""
        if self.frame is not None:
            return True, self.frame.copy()
        return False, None

    def stop(self):
        """Stop the camera reader"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.cap:
            self.cap.release()

    def is_opened(self) -> bool:
        """Check if camera is open and reading"""
        return self.frame is not None

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

        # For tracking unknown face prompts (rate limiting)
        self.last_face_prompt_time = 0
        self.face_prompt_cooldown = 3  # Wait 3 seconds between prompts

        # For tracking detected faces (avoid spam in logs)
        self.last_detected_faces = set()
        self.last_face_log_time = 0
        self.face_log_cooldown = 2  # Log same face max once per 2 seconds

    def _ask_for_name(self) -> Optional[str]:
        """
        Ask user to enter name for unknown face.
        Returns the name or None if user cancels.
        """
        print("\n[FACE] Unknown face detected!")
        user_input = input("Enter name (or press Enter to skip): ").strip()
        return user_input if user_input else None

    def _get_face_name_with_cooldown(self) -> Optional[str]:
        """
        Ask for face name with rate limiting to avoid spam.
        Only prompts once every 3 seconds.
        """
        current_time = time.time()
        if current_time - self.last_face_prompt_time < self.face_prompt_cooldown:
            return None  # Still in cooldown

        self.last_face_prompt_time = current_time
        return self._ask_for_name()

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
                    callback_unknown_face=self._get_face_name_with_cooldown  # Enable with rate limiting
                )
                if face_locations:
                    frame = self.face_system.draw_faces(frame, face_locations, face_names)
                    # Log detected faces to terminal (with rate limiting to avoid spam)
                    current_time = time.time()
                    unique_names = set(face_names)

                    if unique_names != self.last_detected_faces or (current_time - self.last_face_log_time) > self.face_log_cooldown:
                        for name in unique_names:
                            if name != "UNKNOWN":
                                print(f"[FACE] ✓ Detected: {name}")
                            else:
                                print(f"[FACE] ❓ Detected: UNKNOWN face ({len(face_locations)} face{'s' if len(face_locations) > 1 else ''})")
                        self.last_detected_faces = unique_names
                        self.last_face_log_time = current_time
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

    def _try_rtsp_connection(self, rtsp_url: str):
        """
        Try to connect to RTSP stream with multiple transport options.

        Returns:
            cv2.VideoCapture object if successful, None otherwise
        """
        print(f"[RTSP] Attempting connection to: {rtsp_url}")

        transports = [
            ("UDP", rtsp_url),
            ("TCP", rtsp_url.replace("rtsp://", "rtsp_tcp://")),
        ]

        for transport, url in transports:
            try:
                print(f"[RTSP] Trying {transport} transport...")
                cap = cv2.VideoCapture(url)

                # Try to read a test frame with timeout
                for attempt in range(5):
                    ret, frame = cap.read()
                    if ret and frame is not None and frame.size > 0:
                        print(f"[RTSP] ✓ Connected via {transport}!")
                        return cap
                    time.sleep(0.2)

                cap.release()
                print(f"[RTSP] ✗ No valid frames via {transport}")

            except Exception as e:
                print(f"[RTSP] {transport} failed: {str(e)[:80]}")

        return None

    def _suggest_http_fallback(self):
        """Suggest HTTP/MJPEG URLs to user."""
        print("\n[SUGGESTION] RTSP is having trouble. Try HTTP/MJPEG instead:")
        print("  - http://192.168.0.107:8080/video")
        print("  - http://192.168.0.107:8080/mjpegfeed")
        print("\nTo auto-test all URLs, run:")
        print("  python test_phone_camera.py 192.168.0.107")

    def _convert_rtsp_to_http(self, rtsp_url: str) -> str:
        """
        Attempt to convert RTSP URL to HTTP equivalent.

        Examples:
            rtsp://192.168.0.107:8080/h264_ulaw.sdp -> http://192.168.0.107:8080/video
        """
        try:
            # Extract IP and port from RTSP URL
            import re
            match = re.match(r'rtsp://([^:]+):(\d+)', rtsp_url)
            if match:
                ip, port = match.groups()
                http_urls = [
                    f"http://{ip}:{port}/video",
                    f"http://{ip}:{port}/mjpegfeed",
                    f"http://{ip}:{port}/stream",
                ]
                return http_urls
        except Exception as e:
            print(f"[HTTP] Failed to parse RTSP URL: {e}")

        return []

    def run(self):
        """Main application loop - capture and process video from webcam or phone."""
        # Determine camera source
        cap = None
        http_handler = None

        if isinstance(self.camera_id, str):
            # Phone camera - try RTSP first, then fall back to HTTP
            print(f"[INFO] Connecting to phone camera: {self.camera_id}")

            # Check if it's HTTP or RTSP
            if self.camera_id.startswith("http://"):
                # HTTP/MJPEG streaming
                print("[INFO] Using HTTP streaming mode")
                http_handler = HTTPCameraHandler(self.camera_id)
                if not http_handler.start():
                    print("[ERROR] Failed to connect to HTTP stream")
                    self._suggest_http_fallback()
                    return
            else:
                # RTSP streaming - try multiple transports
                cap = self._try_rtsp_connection(self.camera_id)

                if cap is None or not cap.isOpened():
                    print("[ERROR] Failed to establish RTSP connection")
                    print("\n[TRYING HTTP FALLBACK]")

                    # Try to auto-fallback to HTTP
                    http_urls = self._convert_rtsp_to_http(self.camera_id)

                    for http_url in http_urls:
                        print(f"[HTTP] Trying: {http_url}")
                        http_handler = HTTPCameraHandler(http_url)
                        if http_handler.start():
                            print("[SUCCESS] Connected via HTTP fallback!")
                            break
                        http_handler = None

                    if http_handler is None:
                        print("[ERROR] Both RTSP and HTTP failed!")
                        self._suggest_http_fallback()
                        return

        else:
            # Local webcam - use threaded reader to decouple I/O from processing
            print("[INFO] Using threaded camera reader for optimal performance")
            threaded_reader = ThreadedCameraReader(self.camera_id, (self.frame_width, self.frame_height))
            if not threaded_reader.start():
                print("[ERROR] Failed to start threaded camera reader")
                return
            cap = threaded_reader  # Use threaded reader as camera source

        if cap is None and http_handler is None:
            print("[ERROR] Failed to open camera!")
            return

        if cap is not None and not cap.isOpened():
            print("[ERROR] Failed to open camera!")
            return

        # Set camera properties with optimizations
        if cap is not None and isinstance(self.camera_id, int):
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            cap.set(cv2.CAP_PROP_FPS, self.fps_limit)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer to reduce lag

            # Disable hardware transformations (can be slow on some systems)
            cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # Disable autofocus for faster reading

        if cap is not None:
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer to reduce lag

        print("[INFO] Camera opened successfully")
        print(f"[INFO] Resolution: {self.frame_width}x{self.frame_height}")
        print("[INFO] Starting video processing...")
        print("[INFO] Press 'q' to quit, 's' to save frame, 't' to toggle OCR")
        print()

        frame_errors = 0
        max_frame_errors = 150  # Allow more tolerance for RTSP streaming
        successful_frames = 0
        black_frame_count = 0  # Track completely black frames

        try:
            while True:
                # Get frame from appropriate source
                if http_handler is not None:
                    ret, frame = http_handler.get_frame()
                elif isinstance(cap, ThreadedCameraReader):
                    # Use threaded reader's get_frame method
                    ret, frame = cap.get_frame()
                else:
                    # Standard VideoCapture
                    ret, frame = cap.read()

                if not ret or frame is None:
                    frame_errors += 1
                    # Print progress on first error and periodically
                    if frame_errors == 1:
                        print("[WAIT] Waiting for valid frames from stream...")
                    elif frame_errors % 50 == 0:
                        print(f"[WAIT] Still buffering... ({frame_errors} attempts, {successful_frames} frames)")

                    # Allow tolerance for frame errors
                    if frame_errors > max_frame_errors:
                        print("[ERROR] Stream disconnected - no valid frames received")
                        break
                    time.sleep(0.05)  # Wait longer for frame
                    continue

                # Reset error counter on successful frame
                if frame_errors > 0 and successful_frames == 0:
                    print(f"[OK] Connected! Receiving frames...")
                frame_errors = 0
                successful_frames += 1

                # Detect black frames (possible codec issue)
                if frame is not None and frame.size > 0:
                    # Check if frame is mostly black (possible H264 decode error)
                    mean_brightness = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).mean()
                    if mean_brightness < 10:
                        black_frame_count += 1
                        if black_frame_count > 30:
                            print("[WARNING] Receiving mostly black frames - possible codec issue")
                            print("[HINT] Try using HTTP stream instead:")
                            print("  http://192.168.0.107:8080/video")
                            black_frame_count = 0
                    else:
                        black_frame_count = 0

                # Skip first few frames which are often corrupted
                if successful_frames < 10:
                    continue

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
            if cap is not None:
                if isinstance(cap, ThreadedCameraReader):
                    cap.stop()
                else:
                    cap.release()
            if http_handler is not None:
                http_handler.stop()

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

    # Ask user to choose camera source
    print("Camera Source Selection:")
    print("  1. Built-in Webcam (default)")
    print("  2. Phone Camera via Phone Link (RTSP/HTTP)")
    print()

    choice = input("Select camera source (1 or 2, press Enter for 1): ").strip()

    # Performance/Resolution presets
    print("\nPerformance Mode Selection:")
    print("  1. High Quality (1280x720) - For good hardware")
    print("  2. Balanced (640x480) - Recommended for phone camera")
    print("  3. Fast (480x360) - For slower systems or older phones")
    print("  4. Ultra Fast (320x240) - Minimum, extremely fast")
    print()

    perf_choice = input("Select performance mode (1-4, press Enter for 2): ").strip()

    # Resolution presets
    resolution_presets = {
        '1': (1280, 720, "High Quality"),
        '2': (640, 480, "Balanced"),
        '3': (480, 360, "Fast"),
        '4': (320, 240, "Ultra Fast"),
    }

    if perf_choice not in resolution_presets:
        perf_choice = '2'  # Default to Balanced

    frame_width, frame_height, perf_name = resolution_presets[perf_choice]

    print(f"\n[INFO] Using {perf_name} mode: {frame_width}x{frame_height}")

    # Configuration
    config = {
        'enable_face_recognition': True,
        'enable_object_detection': True,
        'enable_ocr': False,  # Disabled by default for performance
        'yolo_model': 'yolov8n.pt',  # Using nano for speed
        'camera_id': 0,
        'frame_width': frame_width,
        'frame_height': frame_height,
        'fps_limit': 30
    }

    if choice == '2':
        print("\n[PHONE CAMERA] Phone Camera Setup:")
        print("  Supports: IP Webcam, DroidCam, Phone Link")
        print()
        print("URL format options:")
        print("  - HTTP: http://192.168.0.107:8080/video")
        print("  - RTSP: rtsp://192.168.0.107:8080/h264_ulaw.sdp")
        print()

        url = input("Enter Phone Camera URL: ").strip()

        if url:
            config['camera_id'] = url
            print(f"\n[INFO] Using phone camera: {url}")
        else:
            print("\n[INFO] No URL provided. Using default webcam.")

        # Offer URL tester
        print("\nTip: Run 'python test_phone_camera.py 192.168.0.107' to find working URLs")
    else:
        print("\n[INFO] Using built-in webcam")

    print()
    print("[INFO] Resolution: {}x{}".format(frame_width, frame_height))
    print("[INFO] Press 'q' to quit, 's' to save frame, 't' to toggle OCR")
    print()

    # Create and run system
    system = MultiDetectionSystem(**config)
    system.run()


if __name__ == "__main__":
    main()
