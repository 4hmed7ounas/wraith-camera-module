#!/usr/bin/env python3
"""Quick test for PaddleOCR initialization"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("Testing PaddleOCR initialization...")
    from paddleocr import PaddleOCR

    logger.info("Creating OCR instance with minimal parameters...")
    ocr = PaddleOCR(lang='en', use_gpu=False)

    logger.info("✓ PaddleOCR initialized successfully!")
    logger.info("Ready to use for plate recognition")

except Exception as e:
    logger.error(f"✗ Failed: {e}")
    sys.exit(1)
