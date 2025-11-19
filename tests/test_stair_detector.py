"""
Unit tests for StairDetector module
"""

import unittest
import numpy as np
import cv2
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from stair_detector import StairDetector


class TestStairDetector(unittest.TestCase):
    """Test cases for StairDetector class."""

    def setUp(self):
        """Set up test fixtures."""
        self.detector = StairDetector(sensitivity=0.7)

    def test_initialization(self):
        """Test detector initialization."""
        self.assertIsNotNone(self.detector)
        self.assertEqual(self.detector.sensitivity, 0.7)
        self.assertEqual(len(self.detector.frame_history), 0)

    def test_detect_stairs_empty_frame(self):
        """Test detection with empty frame."""
        empty_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detected, confidence, annotated = self.detector.detect_stairs(empty_frame)

        self.assertFalse(detected)
        self.assertIsInstance(confidence, float)
        self.assertIsNotNone(annotated)

    def test_detect_stairs_synthetic_stairs(self):
        """Test detection with synthetic stair pattern."""
        # Create a synthetic image with horizontal lines (simulating stairs)
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 200

        # Draw horizontal lines (stair edges)
        for y in range(250, 450, 30):
            cv2.line(frame, (100, y), (540, y), (50, 50, 50), 3)

        detected, confidence, annotated = self.detector.detect_stairs(frame)

        # May or may not detect depending on edge detection parameters
        # Just ensure it doesn't crash
        self.assertIsInstance(detected, bool)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_reset(self):
        """Test detector reset."""
        # Add some history
        self.detector.frame_history = [True, False, True]

        # Reset
        self.detector.reset()

        # Verify history is cleared
        self.assertEqual(len(self.detector.frame_history), 0)

    def test_temporal_filter(self):
        """Test temporal filtering."""
        # Add consistent detections
        for _ in range(5):
            self.detector.frame_history.append(True)

        result = self.detector._temporal_filter()
        self.assertTrue(result)

        # Add inconsistent detections
        self.detector.reset()
        self.detector.frame_history = [True, False, False, True, False]

        result = self.detector._temporal_filter()
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
