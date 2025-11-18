"""
Test Phone Camera Streaming URLs
Helps find the correct RTSP/HTTP URL for your phone camera
"""

import cv2
import time
import sys
from urllib.request import urlopen
import json

def test_url(url: str, timeout: int = 5) -> bool:
    """Test if a URL is accessible and streams video"""
    print(f"\n[TEST] Trying: {url}")
    try:
        cap = cv2.VideoCapture(url)

        # Try to read a frame
        start_time = time.time()
        while time.time() - start_time < timeout:
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"  ✓ SUCCESS! Got frame: {frame.shape}")
                cap.release()
                return True
            time.sleep(0.1)

        cap.release()
        print(f"  ✗ Failed - timeout or no frames")
        return False

    except Exception as e:
        print(f"  ✗ Failed - {str(e)[:100]}")
        return False


def get_ip_webcam_urls(ip: str) -> list:
    """Generate possible IP Webcam URLs"""
    urls = [
        f"rtsp://{ip}:8080/h264_ulaw.sdp",   # H264/uLaw (RECOMMENDED)
        f"rtsp://{ip}:8080/h264_pcm.sdp",    # H264/HQ PCM
        f"http://{ip}:8080/video",           # HTTP streaming
        f"http://{ip}:8080/mjpegfeed",       # MJPEG HTTP
        f"rtsp://{ip}:554/stream",           # Standard RTSP
        f"rtsp://{ip}:8080/mpeg4",           # RTSP MPEG4
    ]
    return urls


def get_droidcam_urls(ip: str) -> list:
    """Generate possible DroidCam URLs"""
    urls = [
        f"rtsp://{ip}:4747/mjpegfeed",       # Main stream
        f"rtsp://{ip}:4747/video",           # Video
        f"rtsp://{ip}:4747/h264",            # H264
        f"http://{ip}:4747/mjpegfeed",       # HTTP MJPEG
    ]
    return urls


def get_generic_rtsp_urls(ip: str) -> list:
    """Generate generic RTSP URLs"""
    urls = [
        f"rtsp://{ip}:554/stream",
        f"rtsp://{ip}:554/live",
        f"rtsp://{ip}:8554/stream",
        f"rtsp://{ip}:1935/live/stream",
        f"rtsp://{ip}:5000/stream",
    ]
    return urls


def test_all_urls(ip: str):
    """Test all common URL patterns"""
    print("\n" + "="*60)
    print(f"Testing Phone Camera at IP: {ip}")
    print("="*60)

    all_urls = [
        ("IP Webcam", get_ip_webcam_urls(ip)),
        ("DroidCam", get_droidcam_urls(ip)),
        ("Generic RTSP", get_generic_rtsp_urls(ip)),
    ]

    working_urls = []

    for category, urls in all_urls:
        print(f"\n\n[TESTING] {category}")
        print("-" * 60)

        for url in urls:
            if test_url(url, timeout=3):
                working_urls.append(url)

    # Print results
    print("\n\n" + "="*60)
    print("RESULTS")
    print("="*60)

    if working_urls:
        print(f"\n✓ Found {len(working_urls)} working URL(s):\n")
        for i, url in enumerate(working_urls, 1):
            print(f"  {i}. {url}")
        print("\nUse one of these in the application!")
    else:
        print("\n✗ No working URLs found")
        print("\nTroubleshooting tips:")
        print("  1. Verify IP address is correct: ping 192.168.0.107")
        print("  2. Check streaming app is running on phone")
        print("  3. Verify phone and PC are on same network")
        print("  4. Check firewall isn't blocking connection")
        print("  5. Try restarting the streaming app on phone")


def main():
    """Main function"""
    print("="*60)
    print("Phone Camera URL Finder & Tester")
    print("="*60)
    print()

    if len(sys.argv) > 1:
        ip = sys.argv[1]
        print(f"Using IP: {ip}")
    else:
        ip = input("Enter your phone's IP address (e.g., 192.168.0.107): ").strip()

    if not ip:
        print("No IP provided!")
        return

    # Test connectivity
    print(f"\n[TEST] Testing connectivity to {ip}...")
    try:
        result = cv2.VideoCapture(f"rtsp://{ip}:554/stream")
        result.release()
        print("  ✓ Network reachable")
    except:
        print("  ! Connectivity test failed (will continue anyway)")

    # Test all URLs
    test_all_urls(ip)


if __name__ == "__main__":
    main()
