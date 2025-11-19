#!/usr/bin/env python3
"""
Demo script for Stair Detection Safety System
Runs a quick demonstration with simulated data.
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from stair_detector import StairDetector
from motion_sensor import MotionSensor, SensorSimulator
from alert_system import AlertSystem, AlertLevel, AlertType
import numpy as np
import cv2


def create_stair_image():
    """Create a synthetic stair image for demonstration."""
    img = np.ones((480, 640, 3), dtype=np.uint8) * 180

    # Add some texture
    noise = np.random.randint(-20, 20, (480, 640, 3), dtype=np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Draw stair pattern
    y_positions = [250, 280, 310, 340, 370, 400, 430]
    for i, y in enumerate(y_positions):
        # Draw horizontal line (stair edge)
        cv2.line(img, (50, y), (590, y), (80, 80, 80), 4)

        # Add depth perception with shading
        if i < len(y_positions) - 1:
            next_y = y_positions[i + 1]
            # Draw vertical line
            cv2.line(img, (50, y), (50, next_y), (100, 100, 100), 2)
            cv2.line(img, (590, y), (590, next_y), (100, 100, 100), 2)

            # Fill step area with slightly darker color
            pts = np.array([[50, y], [590, y], [590, next_y], [50, next_y]], np.int32)
            cv2.fillPoly(img, [pts], (150, 150, 150))

    return img


def run_demo():
    """Run a demonstration of the stair detection system."""
    print("=" * 70)
    print("Stair Detection Safety System - DEMO")
    print("=" * 70)
    print("\nThis demo simulates the stair detection system with synthetic data.")
    print("In a real deployment, this would use live camera and sensor data.")
    print("=" * 70)

    # Initialize components
    print("\n[1/4] Initializing components...")
    stair_detector = StairDetector(sensitivity=0.7)
    motion_sensor = MotionSensor()
    alert_system = AlertSystem()
    sensor_simulator = SensorSimulator()

    print("✓ Stair Detector initialized")
    print("✓ Motion Sensor initialized")
    print("✓ Alert System initialized")

    # Create test image
    print("\n[2/4] Creating synthetic stair image...")
    stair_image = create_stair_image()
    print("✓ Synthetic stair image created")

    # Test 1: Safe scenario (no stairs, not walking)
    print("\n[3/4] Running test scenarios...")
    print("\n--- Scenario 1: Safe (No Movement) ---")
    plain_image = np.ones((480, 640, 3), dtype=np.uint8) * 200

    for i in range(5):
        gyro, accel = sensor_simulator.generate_stationary_sensors(looking_at_phone=False)
        motion_state = motion_sensor.update(gyro, accel)

        detected, confidence, _ = stair_detector.detect_stairs(plain_image)

        alert_info = alert_system.evaluate_situation(
            detected, confidence,
            motion_state['is_walking'],
            motion_state['is_looking_at_phone']
        )

        print(f"  Frame {i+1}: Stairs={detected}, Walking={motion_state['is_walking']}, "
              f"Looking={motion_state['is_looking_at_phone']}, Alert={alert_info is not None}")

    # Test 2: Dangerous scenario (stairs detected, walking distracted)
    print("\n--- Scenario 2: Dangerous (Walking Distracted Near Stairs) ---")
    stair_detector.reset()
    motion_sensor.reset()
    alert_system.reset()

    for i in range(10):
        gyro, accel = sensor_simulator.generate_walking_sensors(looking_at_phone=True)
        motion_state = motion_sensor.update(gyro, accel)

        detected, confidence, annotated = stair_detector.detect_stairs(stair_image)

        alert_info = alert_system.evaluate_situation(
            detected, confidence,
            motion_state['is_walking'],
            motion_state['is_looking_at_phone']
        )

        if alert_info:
            alert_system.trigger_alert(
                alert_info['type'],
                alert_info['level'],
                alert_info['message'],
                alert_info['metadata']
            )

        print(f"  Frame {i+1}: Stairs={detected} ({confidence:.2f}), "
              f"Walking={motion_state['is_walking']}, "
              f"Looking={motion_state['is_looking_at_phone']}, "
              f"Alert={'YES - ' + alert_info['level'].name if alert_info else 'NO'}")

        time.sleep(0.1)

    # Test 3: Moderate risk (stairs detected, but not distracted)
    print("\n--- Scenario 3: Moderate Risk (Stairs, No Distraction) ---")
    stair_detector.reset()
    motion_sensor.reset()
    alert_system.reset()

    for i in range(5):
        gyro, accel = sensor_simulator.generate_walking_sensors(looking_at_phone=False)
        motion_state = motion_sensor.update(gyro, accel)

        detected, confidence, _ = stair_detector.detect_stairs(stair_image)

        alert_info = alert_system.evaluate_situation(
            detected, confidence,
            motion_state['is_walking'],
            motion_state['is_looking_at_phone']
        )

        if alert_info:
            alert_system.trigger_alert(
                alert_info['type'],
                alert_info['level'],
                alert_info['message'],
                alert_info['metadata']
            )

        print(f"  Frame {i+1}: Stairs={detected} ({confidence:.2f}), "
              f"Walking={motion_state['is_walking']}, "
              f"Looking={motion_state['is_looking_at_phone']}, "
              f"Alert={'YES - ' + alert_info['level'].name if alert_info else 'NO'}")

    # Display statistics
    print("\n[4/4] Final Statistics:")
    stats = alert_system.get_alert_statistics()
    print(f"\nTotal Alerts Triggered: {stats['total_alerts']}")

    if stats['by_level']:
        print("\nAlerts by Severity:")
        for level, count in sorted(stats['by_level'].items()):
            print(f"  {level}: {count}")

    if stats['by_type']:
        print("\nAlerts by Type:")
        for alert_type, count in stats['by_type'].items():
            print(f"  {alert_type}: {count}")

    # Save sample image
    print("\n[OPTIONAL] Saving sample stair detection image...")
    try:
        _, _, annotated = stair_detector.detect_stairs(stair_image)
        if annotated is not None:
            cv2.imwrite('demo_stair_detection.jpg', annotated)
            print("✓ Saved to: demo_stair_detection.jpg")
    except Exception as e:
        print(f"  Could not save image: {e}")

    print("\n" + "=" * 70)
    print("Demo completed successfully!")
    print("=" * 70)
    print("\nTo run the full application with a camera:")
    print("  python src/main.py")
    print("\nFor more options:")
    print("  python src/main.py --help")
    print("=" * 70)


if __name__ == '__main__':
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()
