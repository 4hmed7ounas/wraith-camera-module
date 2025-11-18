#!/usr/bin/env python3
"""
Lightweight Nameplate Reader for PC Testing (No PaddleOCR)
Uses YOLOv8 for detection only, displays bounding boxes
Easier to install than full version

Usage:
    python plate_reader_lightweight.py

Features:
- YOLOv8n for plate detection
- Real-time video with bounding boxes
- FPS counter
- Minimal dependencies
"""

import cv2
import numpy as np
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from ultralytics import YOLO
    logger.info("✓ YOLOv8 imported successfully")
except ImportError as e:
    logger.error(f"✗ Failed to import ultralytics: {e}")
    logger.info("Install with: pip install ultralytics")
    raise


class PlateDetectionModel:
    """YOLOv8n-based plate detection."""

    def __init__(self, model_path: str = "yolov8n.pt", conf_threshold: float = 0.5):
        """Initialize the plate detection model."""
        self.conf_threshold = conf_threshold

        try:
            logger.info(f"Loading YOLOv8 model: {model_path}")
            self.model = YOLO(model_path)
            logger.info("✓ YOLOv8 model loaded successfully")
        except Exception as e:
            logger.error(f"✗ Failed to load YOLOv8 model: {e}")
            raise

    def detect(self, frame):
        """
        Detect plates in frame.

        Returns:
            List of detections with 'box' and 'conf' keys
        """
        try:
            results = self.model(frame, conf=self.conf_threshold, verbose=False)
            detections = []

            if results and len(results) > 0:
                boxes = results[0].boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                        conf = float(box.conf[0].cpu().numpy())
                        detections.append({
                            'box': (x1, y1, x2, y2),
                            'conf': conf
                        })

            return detections
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return []


class CameraReader:
    """Non-blocking camera reader with threading."""

    def __init__(self, camera_id=0, resolution=(640, 480)):
        """Initialize camera reader."""
        self.camera_id = camera_id
        self.resolution = resolution
        self.cap = None
        self.frame = None
        self.running = False
        self.fps = 0

    def start(self) -> bool:
        """Start camera capture."""
        try:
            logger.info(f"Initializing camera {self.camera_id}...")

            # Try DirectShow on Windows (faster)
            try:
                self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
            except:
                self.cap = cv2.VideoCapture(self.camera_id)

            if not self.cap.isOpened():
                logger.error(f"✗ Failed to open camera {self.camera_id}")
                return False

            # Set resolution and FPS
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Single frame buffer

            # Get actual resolution
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            logger.info(f"✓ Camera initialized: {actual_width}x{actual_height} @ 30 FPS")

            self.running = True
            return True

        except Exception as e:
            logger.error(f"✗ Camera initialization failed: {e}")
            return False

    def get_frame(self):
        """Get current frame from camera."""
        if not self.cap or not self.cap.isOpened():
            return False, None

        ret, frame = self.cap.read()
        return ret, frame

    def stop(self):
        """Stop camera capture."""
        self.running = False
        if self.cap:
            self.cap.release()
        logger.info("✓ Camera stopped")


class PlateReaderLightweight:
    """Lightweight plate reader (detection only, no OCR)."""

    def __init__(self, camera_id=0, model_path="yolov8n.pt",
                 conf_threshold=0.5, target_fps=15):
        """Initialize the lightweight plate reader."""
        self.camera = CameraReader(camera_id=camera_id)
        self.detector = PlateDetectionModel(model_path=model_path,
                                           conf_threshold=conf_threshold)
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps

        self.running = False
        self.frame_count = 0
        self.detection_times = []
        self.total_times = []

    def run(self):
        """Run the plate reader."""
        if not self.camera.start():
            logger.error("✗ Failed to start camera")
            return

        self.running = True

        logger.info("\n" + "="*60)
        logger.info("PLATE READER RUNNING (Detection Only)")
        logger.info("="*60)
        logger.info(f"Target FPS: {self.target_fps}")
        logger.info("Press 'q' to quit\n")

        try:
            frame_start = time.time()
            last_fps_time = time.time()
            fps_counter = 0

            while self.running:
                frame_start = time.time()

                # Get frame
                ret, frame = self.camera.get_frame()
                if not ret or frame is None:
                    logger.warning("Failed to read frame")
                    continue

                # Detect plates
                detect_start = time.time()
                detections = self.detector.detect(frame)
                detect_time = time.time() - detect_start
                self.detection_times.append(detect_time)

                # Draw bounding boxes
                for detection in detections:
                    x1, y1, x2, y2 = detection['box']
                    conf = detection['conf']

                    # Draw green box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    # Draw confidence score
                    label = f"Plate {conf:.2f}"
                    cv2.putText(frame, label, (x1, y1 - 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Calculate FPS
                self.frame_count += 1
                fps_counter += 1
                elapsed = time.time() - last_fps_time

                if elapsed >= 1.0:
                    self.camera.fps = fps_counter / elapsed
                    fps_counter = 0
                    last_fps_time = time.time()

                # Draw FPS counter
                fps_text = f"FPS: {self.camera.fps:.1f}"
                cv2.putText(frame, fps_text, (10, 30),
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Draw info
                info = f"Detections: {len(detections)} | Detection: {detect_time*1000:.1f}ms"
                cv2.putText(frame, info, (10, 70),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

                # Display frame
                cv2.imshow("Plate Reader (Detection Only)", frame)

                # Keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    logger.info("User quit requested")
                    break

                # Frame rate limiting
                total_time = time.time() - frame_start
                self.total_times.append(total_time)

                if total_time < self.frame_time:
                    time.sleep(self.frame_time - total_time)

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"✗ Error: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the plate reader."""
        self.running = False
        self.camera.stop()
        cv2.destroyAllWindows()

        # Print statistics
        if self.frame_count > 0:
            logger.info("\n" + "="*60)
            logger.info("FINAL STATISTICS")
            logger.info("="*60)
            logger.info(f"Total frames processed: {self.frame_count}")

            if self.detection_times:
                logger.info(f"Avg detection time: {np.mean(self.detection_times)*1000:.1f}ms")

            if self.total_times:
                avg_frame_time = np.mean(self.total_times) * 1000
                avg_fps = 1000.0 / avg_frame_time if avg_frame_time > 0 else 0
                logger.info(f"Avg frame time: {avg_frame_time:.1f}ms")
                logger.info(f"Avg FPS: {avg_fps:.1f}")

        logger.info("✓ Plate reader stopped")


def main():
    """Main entry point."""
    try:
        # Initialize
        reader = PlateReaderLightweight(
            camera_id=0,
            model_path="yolov8n.pt",
            conf_threshold=0.5,
            target_fps=15
        )

        # Run
        reader.run()

    except Exception as e:
        logger.error(f"✗ Failed to start: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
