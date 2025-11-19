#!/usr/bin/env python3
"""
Stair Detection Safety System - Main Application
Monitors camera and sensors to warn users of stairs when distracted.
"""

import cv2
import time
import argparse
import sys
from typing import Optional

from stair_detector import StairDetector
from motion_sensor import MotionSensor, SensorSimulator
from alert_system import AlertSystem, AlertLevel, AlertType


class StairDetectionApp:
    """
    Main application for stair detection safety system.
    """

    def __init__(self, camera_index: int = 0, sensitivity: float = 0.7,
                 simulation_mode: bool = False):
        """
        Initialize the application.

        Args:
            camera_index: Camera device index
            sensitivity: Detection sensitivity (0.0 to 1.0)
            simulation_mode: Use simulated sensor data instead of real sensors
        """
        self.camera_index = camera_index
        self.sensitivity = sensitivity
        self.simulation_mode = simulation_mode

        # Initialize components
        self.stair_detector = StairDetector(sensitivity=sensitivity)
        self.motion_sensor = MotionSensor()
        self.alert_system = AlertSystem()

        # Simulation
        self.sensor_simulator = SensorSimulator() if simulation_mode else None

        # Camera
        self.camera: Optional[cv2.VideoCapture] = None

        # Statistics
        self.frame_count = 0
        self.detection_count = 0
        self.start_time = time.time()

        # Control flags
        self.running = False
        self.show_visualization = True

    def initialize_camera(self) -> bool:
        """Initialize the camera."""
        print(f"Initializing camera (index: {self.camera_index})...")
        self.camera = cv2.VideoCapture(self.camera_index)

        if not self.camera.isOpened():
            print(f"Error: Could not open camera {self.camera_index}")
            return False

        # Set camera properties for better performance
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera.set(cv2.CAP_PROP_FPS, 30)

        print("Camera initialized successfully")
        return True

    def run(self):
        """Main application loop."""
        print("=" * 60)
        print("Stair Detection Safety System")
        print("=" * 60)
        print(f"Sensitivity: {self.sensitivity}")
        print(f"Simulation Mode: {self.simulation_mode}")
        print("Press 'q' to quit, 's' to toggle visualization")
        print("=" * 60)

        if not self.initialize_camera():
            print("Failed to initialize camera. Exiting...")
            return

        self.running = True
        self.start_time = time.time()

        try:
            while self.running:
                success = self.process_frame()

                if not success:
                    print("Error processing frame. Retrying...")
                    time.sleep(0.1)
                    continue

                # Handle keyboard input
                if self.show_visualization:
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        print("\nShutting down...")
                        break
                    elif key == ord('s'):
                        self.show_visualization = not self.show_visualization
                        print(f"\nVisualization: {'ON' if self.show_visualization else 'OFF'}")

        except KeyboardInterrupt:
            print("\n\nInterrupted by user")

        finally:
            self.cleanup()

    def process_frame(self) -> bool:
        """
        Process a single frame.

        Returns:
            True if successful, False otherwise
        """
        # Capture frame
        ret, frame = self.camera.read()
        if not ret or frame is None:
            return False

        self.frame_count += 1
        current_time = time.time()

        # Detect stairs
        stairs_detected, confidence, annotated_frame = self.stair_detector.detect_stairs(frame)

        # Get sensor data
        if self.simulation_mode:
            # Simulate sensors based on stair detection
            # When stairs are detected, simulate walking while looking at phone
            gyro_data, accel_data = self.sensor_simulator.generate_walking_sensors(
                looking_at_phone=stairs_detected
            )
        else:
            # In a real implementation, this would read from actual sensors
            # For now, we'll use simulated data
            gyro_data, accel_data = self.sensor_simulator.generate_walking_sensors(
                looking_at_phone=True
            ) if self.sensor_simulator else ({
                'x': 0, 'y': 0, 'z': 0
            }, {
                'x': 0, 'y': 0, 'z': 9.8
            })

        # Process sensor data
        motion_state = self.motion_sensor.update(gyro_data, accel_data, current_time)

        # Evaluate situation and trigger alerts if necessary
        alert_info = self.alert_system.evaluate_situation(
            stairs_detected=stairs_detected,
            stairs_confidence=confidence,
            is_walking=motion_state['is_walking'],
            is_looking_at_phone=motion_state['is_looking_at_phone']
        )

        if alert_info:
            self.alert_system.trigger_alert(
                alert_type=alert_info['type'],
                level=alert_info['level'],
                message=alert_info['message'],
                metadata=alert_info['metadata']
            )

        # Update statistics
        if stairs_detected:
            self.detection_count += 1

        # Visualization
        if self.show_visualization and annotated_frame is not None:
            self._add_overlay_info(annotated_frame, stairs_detected, confidence,
                                  motion_state, alert_info)
            cv2.imshow('Stair Detection Safety System', annotated_frame)

        # Print status every 30 frames (~1 second)
        if self.frame_count % 30 == 0:
            self._print_status(stairs_detected, confidence, motion_state)

        return True

    def _add_overlay_info(self, frame, stairs_detected: bool, confidence: float,
                         motion_state: dict, alert_info: Optional[dict]):
        """Add information overlay to the frame."""
        height, width = frame.shape[:2]

        # Create semi-transparent overlay panel
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, height - 150), (400, height - 10),
                     (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Add text information
        y_offset = height - 130
        line_height = 25

        info_lines = [
            f"Stairs: {'YES' if stairs_detected else 'NO'} ({confidence:.2f})",
            f"Walking: {'YES' if motion_state['is_walking'] else 'NO'}",
            f"Looking at Phone: {'YES' if motion_state['is_looking_at_phone'] else 'NO'}",
            f"Phone Tilt: {motion_state['phone_orientation']['tilt_angle']:.1f}°"
        ]

        for i, line in enumerate(info_lines):
            color = (0, 255, 0)
            if i == 0 and stairs_detected:
                color = (0, 0, 255)
            elif i == 2 and motion_state['is_looking_at_phone']:
                color = (0, 165, 255)

            cv2.putText(frame, line, (20, y_offset + i * line_height),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Add alert indicator if active
        if alert_info:
            alert_color = {
                AlertLevel.LOW: (0, 255, 255),
                AlertLevel.MEDIUM: (0, 165, 255),
                AlertLevel.HIGH: (0, 0, 255),
                AlertLevel.CRITICAL: (0, 0, 255)
            }.get(alert_info['level'], (255, 255, 255))

            cv2.rectangle(frame, (10, 10), (width - 10, 70), alert_color, 3)

        # Add FPS counter
        elapsed = time.time() - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        cv2.putText(frame, f"FPS: {fps:.1f}", (width - 120, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    def _print_status(self, stairs_detected: bool, confidence: float,
                     motion_state: dict):
        """Print status information to console."""
        elapsed = time.time() - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0

        status = (
            f"\r[{elapsed:.1f}s] "
            f"FPS: {fps:.1f} | "
            f"Frames: {self.frame_count} | "
            f"Stairs: {'YES' if stairs_detected else 'NO '} ({confidence:.2f}) | "
            f"Walking: {'YES' if motion_state['is_walking'] else 'NO '} | "
            f"Looking: {'YES' if motion_state['is_looking_at_phone'] else 'NO '}"
        )

        print(status, end='', flush=True)

    def cleanup(self):
        """Clean up resources."""
        print("\n\nCleaning up...")

        if self.camera:
            self.camera.release()

        cv2.destroyAllWindows()

        # Print final statistics
        self._print_final_statistics()

    def _print_final_statistics(self):
        """Print final statistics."""
        elapsed = time.time() - self.start_time
        avg_fps = self.frame_count / elapsed if elapsed > 0 else 0

        print("\n" + "=" * 60)
        print("Session Statistics")
        print("=" * 60)
        print(f"Duration: {elapsed:.1f} seconds")
        print(f"Total Frames: {self.frame_count}")
        print(f"Average FPS: {avg_fps:.1f}")
        print(f"Stair Detections: {self.detection_count}")

        alert_stats = self.alert_system.get_alert_statistics()
        print(f"\nTotal Alerts: {alert_stats['total_alerts']}")

        if alert_stats['by_level']:
            print("\nAlerts by Level:")
            for level, count in alert_stats['by_level'].items():
                print(f"  {level}: {count}")

        print("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Stair Detection Safety System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings
  python main.py

  # Run with custom camera and sensitivity
  python main.py --camera 1 --sensitivity 0.8

  # Run in simulation mode
  python main.py --simulate

  # Run without visualization (headless)
  python main.py --no-viz
        """
    )

    parser.add_argument(
        '--camera', '-c',
        type=int,
        default=0,
        help='Camera device index (default: 0)'
    )

    parser.add_argument(
        '--sensitivity', '-s',
        type=float,
        default=0.7,
        help='Detection sensitivity 0.0-1.0 (default: 0.7)'
    )

    parser.add_argument(
        '--simulate',
        action='store_true',
        help='Use simulated sensor data'
    )

    parser.add_argument(
        '--no-viz',
        action='store_true',
        help='Disable visualization window'
    )

    args = parser.parse_args()

    # Validate sensitivity
    if not 0.0 <= args.sensitivity <= 1.0:
        print("Error: Sensitivity must be between 0.0 and 1.0")
        sys.exit(1)

    # Create and run application
    app = StairDetectionApp(
        camera_index=args.camera,
        sensitivity=args.sensitivity,
        simulation_mode=args.simulate
    )

    if args.no_viz:
        app.show_visualization = False

    app.run()


if __name__ == '__main__':
    main()
