#!/usr/bin/env python3
"""
Real-Time Nameplate/License Plate Reader for Raspberry Pi 5
Optimized for 8-15 FPS performance on ARM64 architecture

Features:
- YOLOv8n for plate detection (640x480 resolution)
- PaddleOCR for text recognition (ARM optimized)
- Real-time video processing with OpenCV
- FP16 support when available
- Production-ready error handling
- Minimal resource overhead

Author: Computer Vision Specialist
Target: Raspberry Pi 5 (4GB RAM minimum)
"""

import cv2
import numpy as np
import time
import threading
from pathlib import Path
from typing import Tuple, Optional, List
from collections import deque
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from ultralytics import YOLO
    logger.info("✓ ultralytics (YOLOv8) imported successfully")
except ImportError as e:
    logger.error(f"✗ Failed to import ultralytics: {e}")
    raise

try:
    from paddleocr import PaddleOCR
    logger.info("✓ PaddleOCR imported successfully")
except ImportError as e:
    logger.error(f"✗ Failed to import paddleocr: {e}")
    raise


class PlateDetectionModel:
    """
    YOLOv8n-based plate detection with FP16 optimization for Raspberry Pi.

    Attributes:
        model: YOLOv8n model instance
        use_fp16: Whether FP16 precision is supported
        conf_threshold: Confidence threshold for detections
    """

    def __init__(self, model_path: str = "yolov8n.pt", conf_threshold: float = 0.5):
        """
        Initialize the plate detection model.

        Args:
            model_path: Path to YOLOv8 model (default: nano model)
            conf_threshold: Minimum confidence threshold (0-1)
        """
        self.conf_threshold = conf_threshold
        self.use_fp16 = False

        try:
            logger.info(f"Loading YOLOv8 model: {model_path}")
            self.model = YOLO(model_path)

            # Check for FP16 support
            self._check_fp16_support()

            logger.info("✓ YOLOv8 model loaded successfully")
        except Exception as e:
            logger.error(f"✗ Failed to load YOLOv8 model: {e}")
            raise

    def _check_fp16_support(self):
        """Check if FP16 (half precision) is supported on current hardware."""
        try:
            import torch
            if torch.cuda.is_available():
                self.use_fp16 = True
                logger.info("✓ FP16 support detected (CUDA available)")
            else:
                # Check ARM NEON support (Raspberry Pi 5)
                try:
                    import platform
                    if 'aarch64' in platform.machine():
                        self.use_fp16 = True
                        logger.info("✓ ARM64 architecture detected - FP16 enabled")
                except:
                    pass
        except:
            self.use_fp16 = False
            logger.warning("FP16 not available - using FP32")

    def detect(self, frame: np.ndarray) -> List[dict]:
        """
        Detect plates in a frame.

        Args:
            frame: Input image (BGR format)

        Returns:
            List of detections with format:
            [{'box': [x1, y1, x2, y2], 'conf': confidence}, ...]
        """
        try:
            # Run inference with FP16 if available
            results = self.model(
                frame,
                conf=self.conf_threshold,
                imgsz=640,
                verbose=False,
                half=self.use_fp16
            )

            detections = []
            if results and len(results) > 0:
                boxes = results[0].boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    conf = float(box.conf[0].cpu().numpy())

                    detections.append({
                        'box': [x1, y1, x2, y2],
                        'conf': conf
                    })

            return detections
        except Exception as e:
            logger.error(f"✗ Detection error: {e}")
            return []


class TextRecognitionModel:
    """
    PaddleOCR-based text recognition optimized for ARM.

    Uses CPU-only inference suitable for Raspberry Pi.
    """

    def __init__(self):
        """Initialize PaddleOCR for plate text recognition."""
        try:
            logger.info("Initializing PaddleOCR...")
            # Use only essential parameters supported by current PaddleOCR
            self.ocr = PaddleOCR(
                lang='en'
            )
            logger.info("✓ PaddleOCR initialized successfully")
        except Exception as e:
            logger.error(f"✗ Failed to initialize PaddleOCR: {e}")
            raise

    def recognize(self, plate_crop: np.ndarray) -> str:
        """
        Recognize text from a plate crop.

        Args:
            plate_crop: Cropped plate region (BGR format)

        Returns:
            Recognized text as string, or empty string if recognition fails
        """
        try:
            if plate_crop is None or plate_crop.size == 0:
                return ""

            # PaddleOCR expects BGR format
            results = self.ocr.ocr(plate_crop, cls=True)

            if not results or not results[0]:
                return ""

            # Extract text from results
            text = "".join([line[1][0] for line in results[0]])
            return text.strip()
        except Exception as e:
            logger.warning(f"✗ OCR recognition error: {e}")
            return ""


class CameraReader:
    """
    Non-blocking camera reader using threading.
    Decouples frame capture from processing to maintain consistent FPS.

    This ensures camera I/O doesn't block inference operations.
    """

    def __init__(self, camera_id: int = 0, resolution: Tuple[int, int] = (640, 480)):
        """
        Initialize camera reader thread.

        Args:
            camera_id: Camera device ID (0 for default)
            resolution: Target resolution (width, height)
        """
        self.camera_id = camera_id
        self.resolution = resolution
        self.frame = None
        self.running = False
        self.thread = None
        self.cap = None
        self.fps = 0
        self.frame_count = 0
        self.last_time = time.time()

    def start(self) -> bool:
        """
        Start the camera reader thread.

        Returns:
            True if camera initialized successfully, False otherwise
        """
        try:
            logger.info(f"Initializing camera {self.camera_id}...")
            self.cap = cv2.VideoCapture(self.camera_id)

            if not self.cap or not self.cap.isOpened():
                logger.error("✗ Camera not found or cannot be opened")
                return False

            # Set camera properties for optimal performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Single frame buffer

            # Disable autofocus for faster frame reading
            try:
                self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            except:
                pass

            self.running = True
            self.thread = threading.Thread(target=self._read_frames, daemon=True)
            self.thread.start()

            logger.info("✓ Camera initialized and reader thread started")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to initialize camera: {e}")
            return False

    def _read_frames(self):
        """Continuously read frames from camera (runs in separate thread)."""
        while self.running:
            try:
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.frame = frame

                    # Update FPS counter
                    self.frame_count += 1
                    current_time = time.time()
                    if current_time - self.last_time >= 1.0:
                        self.fps = self.frame_count
                        self.frame_count = 0
                        self.last_time = current_time
                else:
                    time.sleep(0.01)
            except Exception as e:
                logger.error(f"✗ Error reading frame: {e}")
                break

    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Get the latest frame (non-blocking).

        Returns:
            Tuple of (success, frame) where success is bool and frame is numpy array
        """
        if self.frame is not None:
            return True, self.frame.copy()
        return False, None

    def stop(self):
        """Stop the camera reader and release resources."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.cap:
            self.cap.release()
        logger.info("✓ Camera reader stopped")

    def get_fps(self) -> int:
        """Get current camera FPS."""
        return self.fps


class PlateReaderPipeline:
    """
    Main pipeline combining detection, recognition, and visualization.

    Optimized for real-time performance on Raspberry Pi 5:
    - Preloaded models
    - Efficient frame handling
    - Minimal memory allocations
    - Threading for I/O decoupling
    """

    def __init__(
        self,
        camera_id: int = 0,
        model_path: str = "yolov8n.pt",
        conf_threshold: float = 0.5,
        target_fps: int = 15
    ):
        """
        Initialize the plate reader pipeline.

        Args:
            camera_id: Camera device ID
            model_path: Path to YOLOv8 model
            conf_threshold: Detection confidence threshold
            target_fps: Target frames per second
        """
        self.camera_id = camera_id
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps

        # Initialize components
        self.camera = None
        self.detector = None
        self.recognizer = None
        self.running = False

        # Performance tracking
        self.frame_count = 0
        self.detection_times = deque(maxlen=30)
        self.recognition_times = deque(maxlen=30)
        self.total_times = deque(maxlen=30)

        # Initialize models and camera
        self._initialize()

    def _initialize(self):
        """Initialize all components."""
        try:
            # Initialize camera
            self.camera = CameraReader(self.camera_id)
            if not self.camera.start():
                raise RuntimeError("Camera initialization failed")

            # Initialize detection model
            self.detector = PlateDetectionModel(
                model_path=self.model_path,
                conf_threshold=self.conf_threshold
            )

            # Initialize recognition model
            self.recognizer = TextRecognitionModel()

            logger.info("✓ Pipeline initialized successfully")
        except Exception as e:
            logger.error(f"✗ Pipeline initialization failed: {e}")
            raise

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, List[dict]]:
        """
        Process a frame through detection and recognition pipeline.

        Args:
            frame: Input frame (BGR format)

        Returns:
            Tuple of (annotated_frame, results) where results is list of
            {'box': [x1, y1, x2, y2], 'text': recognized_text, 'conf': confidence}
        """
        frame_start = time.time()
        results = []

        try:
            # Detection phase
            detect_start = time.time()
            detections = self.detector.detect(frame)
            detect_time = time.time() - detect_start
            self.detection_times.append(detect_time)

            # Recognition phase
            recognize_start = time.time()
            for detection in detections:
                x1, y1, x2, y2 = detection['box']

                # Ensure valid crop region
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(frame.shape[1], x2)
                y2 = min(frame.shape[0], y2)

                if x2 <= x1 or y2 <= y1:
                    continue

                # Crop and recognize
                plate_crop = frame[y1:y2, x1:x2]
                text = self.recognizer.recognize(plate_crop)

                if text:
                    results.append({
                        'box': [x1, y1, x2, y2],
                        'text': text,
                        'conf': detection['conf']
                    })

            recognize_time = time.time() - recognize_start
            self.recognition_times.append(recognize_time)

            # Annotate frame
            annotated_frame = self._annotate_frame(frame, results)

            frame_time = time.time() - frame_start
            self.total_times.append(frame_time)

            return annotated_frame, results

        except Exception as e:
            logger.error(f"✗ Frame processing error: {e}")
            return frame, []

    def _annotate_frame(self, frame: np.ndarray, results: List[dict]) -> np.ndarray:
        """
        Draw bounding boxes and recognized text on frame.

        Args:
            frame: Input frame
            results: Detection and recognition results

        Returns:
            Annotated frame
        """
        annotated = frame.copy()

        for result in results:
            x1, y1, x2, y2 = result['box']
            text = result['text']
            conf = result['conf']

            # Draw bounding box (green for valid detections)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Draw text with confidence
            label = f"{text} ({conf:.2f})"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]

            # Draw label background
            cv2.rectangle(
                annotated,
                (x1, y1 - label_size[1] - 10),
                (x1 + label_size[0], y1),
                (0, 255, 0),
                -1
            )

            # Draw label text
            cv2.putText(
                annotated,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 0),
                2
            )

        # Draw performance metrics
        self._draw_metrics(annotated)

        return annotated

    def _draw_metrics(self, frame: np.ndarray):
        """Draw FPS and performance metrics on frame."""
        try:
            avg_detect = np.mean(self.detection_times) * 1000 if self.detection_times else 0
            avg_recognize = np.mean(self.recognition_times) * 1000 if self.recognition_times else 0
            avg_total = np.mean(self.total_times) * 1000 if self.total_times else 0

            fps = self.camera.get_fps() if self.camera else 0

            metrics = [
                f"FPS: {fps}",
                f"Detect: {avg_detect:.1f}ms",
                f"OCR: {avg_recognize:.1f}ms",
                f"Total: {avg_total:.1f}ms"
            ]

            y_offset = 30
            for metric in metrics:
                cv2.putText(
                    frame,
                    metric,
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )
                y_offset += 30
        except Exception as e:
            logger.warning(f"Error drawing metrics: {e}")

    def run(self, window_name: str = "Real-Time Plate Reader"):
        """
        Run the plate reader in a continuous loop.

        Args:
            window_name: Window title for display
        """
        self.running = True
        logger.info("Starting plate reader pipeline...")
        logger.info(f"Target FPS: {self.target_fps}")
        logger.info("Press 'q' to quit")

        try:
            # Wait for camera to buffer initial frames
            time.sleep(0.5)

            while self.running:
                frame_start = time.time()

                # Get frame from camera
                ret, frame = self.camera.get_frame()
                if not ret or frame is None:
                    time.sleep(0.01)
                    continue

                # Process frame
                annotated_frame, results = self.process_frame(frame)

                # Display results
                cv2.imshow(window_name, annotated_frame)

                # Log plate detections
                if results:
                    for result in results:
                        logger.info(f"Detected plate: {result['text']} (conf: {result['conf']:.2f})")

                self.frame_count += 1

                # FPS regulation
                elapsed = time.time() - frame_start
                if elapsed < self.frame_time:
                    time.sleep(self.frame_time - elapsed)

                # Keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    logger.info("User quit requested")
                    break

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"✗ Pipeline error: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the pipeline and release all resources."""
        self.running = False

        if self.camera:
            self.camera.stop()

        cv2.destroyAllWindows()

        # Print final statistics
        if self.frame_count > 0:
            logger.info(f"\n=== Final Statistics ===")
            logger.info(f"Total frames processed: {self.frame_count}")
            if self.detection_times:
                logger.info(f"Avg detection time: {np.mean(self.detection_times)*1000:.1f}ms")
            if self.recognition_times:
                logger.info(f"Avg OCR time: {np.mean(self.recognition_times)*1000:.1f}ms")
            if self.total_times:
                logger.info(f"Avg frame time: {np.mean(self.total_times)*1000:.1f}ms")
                logger.info(f"Avg FPS: {self.camera.get_fps()}")

        logger.info("✓ Pipeline stopped")


def main():
    """Main entry point."""
    try:
        # Initialize pipeline
        pipeline = PlateReaderPipeline(
            camera_id=0,
            model_path="yolov8n.pt",
            conf_threshold=0.5,
            target_fps=15
        )

        # Run pipeline
        pipeline.run()

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"✗ Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
