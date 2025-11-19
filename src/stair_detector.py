"""
Stair Detection Module
Uses computer vision to detect stairs in real-time camera feed.
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional


class StairDetector:
    """
    Detects stairs using edge detection, line detection, and pattern analysis.
    """

    def __init__(self, sensitivity: float = 0.7):
        """
        Initialize the stair detector.

        Args:
            sensitivity: Detection sensitivity (0.0 to 1.0)
        """
        self.sensitivity = sensitivity
        self.min_lines_for_detection = max(3, int(10 * sensitivity))
        self.frame_history = []
        self.max_history = 5

    def detect_stairs(self, frame: np.ndarray) -> Tuple[bool, float, Optional[np.ndarray]]:
        """
        Detect stairs in the given frame.

        Args:
            frame: Input image frame (BGR format)

        Returns:
            Tuple of (stairs_detected, confidence, annotated_frame)
        """
        if frame is None or frame.size == 0:
            return False, 0.0, None

        # Preprocess the frame
        processed = self._preprocess_frame(frame)

        # Detect edges
        edges = self._detect_edges(processed)

        # Detect lines (stair edges are typically horizontal parallel lines)
        lines = self._detect_lines(edges)

        # Analyze line patterns for stair characteristics
        stairs_detected, confidence = self._analyze_stair_pattern(lines, frame.shape)

        # Create annotated frame for visualization
        annotated_frame = self._annotate_frame(frame.copy(), lines, stairs_detected)

        # Update history for temporal consistency
        self._update_history(stairs_detected)

        # Use temporal filtering to reduce false positives
        final_detection = self._temporal_filter()

        return final_detection, confidence, annotated_frame

    def _preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Preprocess frame for better edge detection."""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(blurred)

        return enhanced

    def _detect_edges(self, frame: np.ndarray) -> np.ndarray:
        """Detect edges using Canny edge detection."""
        # Auto-adjust thresholds based on image statistics
        median = np.median(frame)
        lower = int(max(0, (1.0 - self.sensitivity) * median))
        upper = int(min(255, (1.0 + self.sensitivity) * median))

        edges = cv2.Canny(frame, lower, upper)
        return edges

    def _detect_lines(self, edges: np.ndarray) -> Optional[np.ndarray]:
        """Detect lines using Hough Line Transform."""
        # Use probabilistic Hough transform for better performance
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=50,
            minLineLength=int(edges.shape[1] * 0.3),  # At least 30% of frame width
            maxLineGap=20
        )

        return lines

    def _analyze_stair_pattern(self, lines: Optional[np.ndarray],
                               frame_shape: Tuple[int, int, int]) -> Tuple[bool, float]:
        """
        Analyze detected lines for stair patterns.

        Stairs typically have:
        - Multiple parallel horizontal lines
        - Regular spacing between lines
        - Lines in the lower 2/3 of the frame
        """
        if lines is None or len(lines) < self.min_lines_for_detection:
            return False, 0.0

        height, width = frame_shape[:2]
        horizontal_lines = []

        # Filter for horizontal lines in lower part of frame
        for line in lines:
            x1, y1, x2, y2 = line[0]

            # Calculate angle
            angle = abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)

            # Check if line is mostly horizontal (within 20 degrees)
            if angle < 20 or angle > 160:
                # Check if line is in lower 2/3 of frame
                avg_y = (y1 + y2) / 2
                if avg_y > height * 0.33:
                    horizontal_lines.append((avg_y, x1, x2))

        if len(horizontal_lines) < self.min_lines_for_detection:
            return False, 0.0

        # Sort lines by y-coordinate
        horizontal_lines.sort(key=lambda x: x[0])

        # Check for regular spacing (stair steps)
        spacing_consistency = self._check_line_spacing(horizontal_lines)

        # Calculate confidence based on number of lines and spacing consistency
        confidence = min(1.0, (len(horizontal_lines) / 15.0) * spacing_consistency)

        stairs_detected = confidence > (0.5 * self.sensitivity)

        return stairs_detected, confidence

    def _check_line_spacing(self, lines: List[Tuple[float, int, int]]) -> float:
        """Check if lines have consistent spacing (characteristic of stairs)."""
        if len(lines) < 2:
            return 0.0

        spacings = []
        for i in range(len(lines) - 1):
            spacing = lines[i + 1][0] - lines[i][0]
            spacings.append(spacing)

        if not spacings:
            return 0.0

        # Calculate coefficient of variation (lower is more consistent)
        mean_spacing = np.mean(spacings)
        std_spacing = np.std(spacings)

        if mean_spacing == 0:
            return 0.0

        cv = std_spacing / mean_spacing

        # Convert to consistency score (0 to 1)
        consistency = max(0.0, 1.0 - cv)

        return consistency

    def _annotate_frame(self, frame: np.ndarray, lines: Optional[np.ndarray],
                       stairs_detected: bool) -> np.ndarray:
        """Add visual annotations to the frame."""
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                color = (0, 255, 0) if stairs_detected else (0, 165, 255)
                cv2.line(frame, (x1, y1), (x2, y2), color, 2)

        # Add detection status
        status_text = "STAIRS DETECTED!" if stairs_detected else "No Stairs"
        color = (0, 0, 255) if stairs_detected else (0, 255, 0)
        cv2.putText(frame, status_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        return frame

    def _update_history(self, detection: bool):
        """Update detection history for temporal filtering."""
        self.frame_history.append(detection)
        if len(self.frame_history) > self.max_history:
            self.frame_history.pop(0)

    def _temporal_filter(self) -> bool:
        """Use temporal filtering to reduce false positives."""
        if not self.frame_history:
            return False

        # Require majority of recent frames to agree
        detection_count = sum(self.frame_history)
        return detection_count >= (len(self.frame_history) / 2)

    def reset(self):
        """Reset the detector state."""
        self.frame_history = []
