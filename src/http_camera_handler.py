"""
HTTP Camera Handler
Handles HTTP/MJPEG streaming from IP Webcam and similar apps
"""

import cv2
import numpy as np
from urllib.request import urlopen
from urllib.error import URLError
import threading
import time


class HTTPCameraHandler:
    """
    Handles HTTP/MJPEG streaming from phone camera
    """

    def __init__(self, url: str, timeout: int = 5):
        """
        Initialize HTTP camera handler

        Args:
            url: HTTP stream URL (e.g., http://192.168.0.107:8080/mjpegfeed)
            timeout: Connection timeout in seconds
        """
        self.url = url
        self.timeout = timeout
        self.frame = None
        self.running = False
        self.thread = None
        self.fps = 0
        self.frame_count = 0
        self.last_time = time.time()
        self.error_count = 0
        self.max_errors = 10

    def _fetch_frames(self):
        """Fetch frames from HTTP stream with error recovery"""
        stream = None
        try:
            print(f"[HTTP] Starting frame fetch thread...")
            stream = urlopen(self.url, timeout=self.timeout)
            bytes_data = b""
            consecutive_decode_errors = 0

            while self.running:
                try:
                    # Read data chunk
                    chunk = stream.read(1024)
                    if not chunk:
                        print("[HTTP] Stream closed by server")
                        break

                    bytes_data += chunk

                    # Find JPEG boundaries
                    a = bytes_data.find(b'\xff\xd8')  # JPEG start
                    b = bytes_data.find(b'\xff\xd9')  # JPEG end

                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b+2]
                        bytes_data = bytes_data[b+2:]

                        # Decode frame
                        frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                        if frame is not None and frame.size > 0:
                            self.frame = frame
                            self.error_count = 0
                            consecutive_decode_errors = 0

                            # Update FPS
                            self.frame_count += 1
                            current_time = time.time()
                            if current_time - self.last_time >= 1.0:
                                self.fps = self.frame_count
                                self.frame_count = 0
                                self.last_time = current_time
                        else:
                            consecutive_decode_errors += 1
                            if consecutive_decode_errors > 20:
                                print("[HTTP] Too many decode errors, reconnecting...")
                                break

                except Exception as decode_error:
                    print(f"[HTTP] Decode error: {str(decode_error)[:60]}")
                    consecutive_decode_errors += 1
                    if consecutive_decode_errors > 20:
                        break

        except URLError as e:
            print(f"[HTTP STREAM ERROR] URL Error: {e}")
        except Exception as e:
            print(f"[HTTP STREAM ERROR] {str(e)[:100]}")
        finally:
            if stream:
                try:
                    stream.close()
                except:
                    pass
            self.running = False
            print("[HTTP] Frame fetch thread stopped")

    def start(self) -> bool:
        """Start fetching frames"""
        try:
            print(f"[HTTP] Connecting to: {self.url}")
            self.running = True
            self.thread = threading.Thread(target=self._fetch_frames, daemon=True)
            self.thread.start()

            # Wait for first frame with progress indication
            timeout_attempts = 50
            for attempt in range(timeout_attempts):
                if self.frame is not None:
                    print(f"[HTTP] ✓ Connected successfully! (Frame size: {self.frame.shape})")
                    return True
                if attempt % 10 == 0 and attempt > 0:
                    print(f"[HTTP] Still connecting... ({attempt}/{timeout_attempts})")
                time.sleep(0.1)

            print(f"[HTTP] Timeout waiting for frames after {timeout_attempts*0.1:.1f}s")
            self.stop()
            return False

        except Exception as e:
            print(f"[HTTP] Failed to connect: {e}")
            self.stop()
            return False

    def get_frame(self) -> tuple:
        """
        Get current frame

        Returns:
            Tuple of (success: bool, frame: np.ndarray or None)
        """
        if self.frame is not None and self.frame.size > 0:
            return True, self.frame.copy()
        return False, None

    def stop(self):
        """Stop fetching frames"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)

    def is_opened(self) -> bool:
        """Check if stream is open and receiving frames"""
        return self.running and self.frame is not None and self.frame.size > 0

    def release(self):
        """Release resources"""
        self.stop()

    def get_fps(self) -> int:
        """Get current FPS of the stream"""
        return self.fps
