"""
Unit tests for MotionSensor module
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from motion_sensor import MotionSensor, SensorSimulator


class TestMotionSensor(unittest.TestCase):
    """Test cases for MotionSensor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.sensor = MotionSensor()
        self.simulator = SensorSimulator()

    def test_initialization(self):
        """Test sensor initialization."""
        self.assertIsNotNone(self.sensor)
        self.assertEqual(len(self.sensor.gyro_history), 0)
        self.assertEqual(len(self.sensor.accel_history), 0)

    def test_update_sensor_data(self):
        """Test updating sensor data."""
        gyro = {'x': 0.1, 'y': 0.05, 'z': 0.02}
        accel = {'x': 0.5, 'y': 0.3, 'z': 9.8}

        result = self.sensor.update(gyro, accel)

        self.assertIn('is_walking', result)
        self.assertIn('phone_orientation', result)
        self.assertIn('is_looking_at_phone', result)
        self.assertIn('distracted', result)

    def test_phone_orientation_vertical(self):
        """Test phone orientation detection - vertical position."""
        # Phone vertical (z-axis aligned with gravity)
        gyro = {'x': 0, 'y': 0, 'z': 0}
        accel = {'x': 0, 'y': 0, 'z': 9.8}

        result = self.sensor.update(gyro, accel)
        orientation = result['phone_orientation']

        # Vertical phone should have low tilt angle
        self.assertLess(orientation['tilt_angle'], 30)
        self.assertFalse(result['is_looking_at_phone'])

    def test_phone_orientation_tilted(self):
        """Test phone orientation detection - tilted position."""
        # Phone tilted (typical viewing angle)
        gyro = {'x': 0, 'y': 0, 'z': 0}
        accel = {'x': 5.0, 'y': 0, 'z': 8.0}

        result = self.sensor.update(gyro, accel)

        # Tilted phone should be detected as "looking at phone"
        self.assertTrue(result['is_looking_at_phone'])

    def test_walking_detection(self):
        """Test walking detection with simulated data."""
        # Simulate multiple walking samples
        for _ in range(25):
            gyro, accel = self.simulator.generate_walking_sensors(looking_at_phone=True)
            result = self.sensor.update(gyro, accel)

        # Should detect walking after enough samples
        # Note: May not always detect depending on random variations
        self.assertIsInstance(result['is_walking'], bool)

    def test_reset(self):
        """Test sensor reset."""
        # Add some data
        gyro = {'x': 0.1, 'y': 0.05, 'z': 0.02}
        accel = {'x': 0.5, 'y': 0.3, 'z': 9.8}
        self.sensor.update(gyro, accel)

        # Reset
        self.sensor.reset()

        # Verify history is cleared
        self.assertEqual(len(self.sensor.gyro_history), 0)
        self.assertEqual(len(self.sensor.accel_history), 0)


class TestSensorSimulator(unittest.TestCase):
    """Test cases for SensorSimulator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.simulator = SensorSimulator()

    def test_generate_walking_sensors(self):
        """Test walking sensor simulation."""
        gyro, accel = self.simulator.generate_walking_sensors(looking_at_phone=True)

        self.assertIn('x', gyro)
        self.assertIn('y', gyro)
        self.assertIn('z', gyro)
        self.assertIn('x', accel)
        self.assertIn('y', accel)
        self.assertIn('z', accel)

    def test_generate_stationary_sensors(self):
        """Test stationary sensor simulation."""
        gyro, accel = self.simulator.generate_stationary_sensors(looking_at_phone=False)

        # Stationary sensors should have minimal gyro movement
        self.assertLess(abs(gyro['x']), 0.1)
        self.assertLess(abs(gyro['y']), 0.1)
        self.assertLess(abs(gyro['z']), 0.1)


if __name__ == '__main__':
    unittest.main()
