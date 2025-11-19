"""
Motion Sensor Module
Processes gyroscope and accelerometer data to detect phone orientation and user activity.
"""

import numpy as np
from typing import Dict, Tuple
from collections import deque
import time


class MotionSensor:
    """
    Analyzes motion sensor data to detect if user is walking while looking at phone.
    """

    def __init__(self, window_size: int = 20):
        """
        Initialize motion sensor.

        Args:
            window_size: Number of samples to keep for analysis
        """
        self.window_size = window_size
        self.gyro_history = deque(maxlen=window_size)
        self.accel_history = deque(maxlen=window_size)
        self.orientation_history = deque(maxlen=window_size)

        # Thresholds
        self.walking_accel_threshold = 1.5  # m/s^2 variation
        self.phone_tilt_threshold = 30  # degrees from horizontal

    def update(self, gyro_data: Dict[str, float], accel_data: Dict[str, float],
               timestamp: float = None) -> Dict[str, any]:
        """
        Update sensor data and analyze user state.

        Args:
            gyro_data: Dictionary with 'x', 'y', 'z' gyroscope values (rad/s)
            accel_data: Dictionary with 'x', 'y', 'z' accelerometer values (m/s^2)
            timestamp: Current timestamp (default: current time)

        Returns:
            Dictionary with analysis results
        """
        if timestamp is None:
            timestamp = time.time()

        # Store sensor data
        self.gyro_history.append({
            'data': gyro_data,
            'timestamp': timestamp
        })

        self.accel_history.append({
            'data': accel_data,
            'timestamp': timestamp
        })

        # Analyze current state
        is_walking = self._detect_walking()
        phone_orientation = self._get_phone_orientation(accel_data)
        is_looking_at_phone = self._is_looking_at_phone(phone_orientation)

        # Store orientation history
        self.orientation_history.append(phone_orientation)

        return {
            'is_walking': is_walking,
            'phone_orientation': phone_orientation,
            'is_looking_at_phone': is_looking_at_phone,
            'distracted': is_walking and is_looking_at_phone,
            'timestamp': timestamp
        }

    def _detect_walking(self) -> bool:
        """
        Detect if user is walking based on accelerometer patterns.

        Walking creates periodic acceleration patterns (typically 1-2 Hz).
        """
        if len(self.accel_history) < 10:
            return False

        # Extract vertical acceleration (z-axis typically, but we use magnitude)
        accel_magnitudes = []
        for entry in self.accel_history:
            data = entry['data']
            magnitude = np.sqrt(data['x']**2 + data['y']**2 + data['z']**2)
            accel_magnitudes.append(magnitude)

        accel_array = np.array(accel_magnitudes)

        # Remove gravity (approximately 9.8 m/s^2)
        accel_array = np.abs(accel_array - 9.8)

        # Check for periodic variation characteristic of walking
        variation = np.std(accel_array)
        mean_variation = np.mean(accel_array)

        # Walking typically shows regular acceleration patterns
        is_walking = variation > self.walking_accel_threshold and mean_variation > 0.5

        # Additional check: look for periodicity
        if is_walking and len(accel_array) >= 15:
            # Simple peak detection
            peaks = self._count_peaks(accel_array)
            # Walking at normal pace: ~2 steps per second, 0.5-3 Hz
            # In our window of samples, we should see some peaks
            is_walking = peaks >= 2

        return is_walking

    def _count_peaks(self, signal: np.ndarray, threshold_ratio: float = 0.6) -> int:
        """Count peaks in signal (simple peak detection)."""
        if len(signal) < 3:
            return 0

        threshold = np.mean(signal) + threshold_ratio * np.std(signal)
        peaks = 0

        for i in range(1, len(signal) - 1):
            if signal[i] > signal[i-1] and signal[i] > signal[i+1] and signal[i] > threshold:
                peaks += 1

        return peaks

    def _get_phone_orientation(self, accel_data: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate phone orientation from accelerometer data.

        Returns:
            Dictionary with 'pitch', 'roll', 'tilt_angle' in degrees
        """
        ax, ay, az = accel_data['x'], accel_data['y'], accel_data['z']

        # Calculate pitch and roll
        pitch = np.arctan2(ax, np.sqrt(ay**2 + az**2)) * 180 / np.pi
        roll = np.arctan2(ay, np.sqrt(ax**2 + az**2)) * 180 / np.pi

        # Calculate tilt from vertical (0 degrees = phone vertical, 90 = horizontal)
        tilt_angle = np.arctan2(np.sqrt(ax**2 + ay**2), az) * 180 / np.pi

        return {
            'pitch': pitch,
            'roll': roll,
            'tilt_angle': tilt_angle
        }

    def _is_looking_at_phone(self, orientation: Dict[str, float]) -> bool:
        """
        Determine if user is looking at phone based on orientation.

        Phone is considered "being looked at" when it's tilted towards the user
        (typically 30-80 degrees from vertical).
        """
        tilt = orientation['tilt_angle']

        # Phone is roughly horizontal/tilted when user is looking at it
        # Vertical (0°) = phone upright in pocket/hand not being viewed
        # Horizontal (90°) = phone flat
        # Typical viewing angle: 30-80 degrees
        return self.phone_tilt_threshold < tilt < 85

    def get_risk_level(self) -> str:
        """
        Get current risk level based on recent sensor data.

        Returns:
            Risk level: 'none', 'low', 'medium', 'high'
        """
        if len(self.accel_history) < 5:
            return 'none'

        # Analyze recent history
        recent_states = []
        for i in range(min(5, len(self.accel_history))):
            idx = -(i + 1)
            gyro = list(self.gyro_history)[idx]['data']
            accel = list(self.accel_history)[idx]['data']

            state = self.update(gyro, accel, list(self.accel_history)[idx]['timestamp'])
            recent_states.append(state['distracted'])

        distracted_count = sum(recent_states)
        ratio = distracted_count / len(recent_states)

        if ratio == 0:
            return 'none'
        elif ratio < 0.3:
            return 'low'
        elif ratio < 0.7:
            return 'medium'
        else:
            return 'high'

    def reset(self):
        """Reset all sensor history."""
        self.gyro_history.clear()
        self.accel_history.clear()
        self.orientation_history.clear()


class SensorSimulator:
    """
    Simulates sensor data for testing purposes.
    """

    def __init__(self):
        self.time_offset = 0
        self.walking_phase = 0

    def generate_walking_sensors(self, looking_at_phone: bool = True) -> Tuple[Dict, Dict]:
        """
        Generate simulated sensor data for a walking person.

        Args:
            looking_at_phone: Whether phone is tilted for viewing

        Returns:
            Tuple of (gyro_data, accel_data)
        """
        # Simulate walking gait (periodic motion)
        self.walking_phase += 0.3
        walking_cycle = np.sin(self.walking_phase)

        # Gyroscope data (small rotations while walking)
        gyro_data = {
            'x': 0.1 * np.random.randn() + 0.05 * walking_cycle,
            'y': 0.1 * np.random.randn() + 0.05 * np.cos(self.walking_phase),
            'z': 0.05 * np.random.randn()
        }

        # Accelerometer data
        # Base gravity + walking motion
        base_accel = 9.8
        walking_accel = 2.0 * walking_cycle  # Walking adds periodic acceleration

        if looking_at_phone:
            # Phone tilted ~45 degrees
            tilt = np.radians(45)
            accel_data = {
                'x': base_accel * np.sin(tilt) + 0.5 * np.random.randn(),
                'y': 0.5 * np.random.randn(),
                'z': base_accel * np.cos(tilt) + walking_accel + 0.5 * np.random.randn()
            }
        else:
            # Phone vertical (in pocket or at side)
            accel_data = {
                'x': 0.3 * np.random.randn(),
                'y': 0.3 * np.random.randn(),
                'z': base_accel + walking_accel + 0.5 * np.random.randn()
            }

        return gyro_data, accel_data

    def generate_stationary_sensors(self, looking_at_phone: bool = True) -> Tuple[Dict, Dict]:
        """Generate simulated sensor data for a stationary person."""
        # Gyroscope data (minimal motion)
        gyro_data = {
            'x': 0.01 * np.random.randn(),
            'y': 0.01 * np.random.randn(),
            'z': 0.01 * np.random.randn()
        }

        # Accelerometer data (just gravity)
        base_accel = 9.8

        if looking_at_phone:
            tilt = np.radians(45)
            accel_data = {
                'x': base_accel * np.sin(tilt) + 0.1 * np.random.randn(),
                'y': 0.1 * np.random.randn(),
                'z': base_accel * np.cos(tilt) + 0.1 * np.random.randn()
            }
        else:
            accel_data = {
                'x': 0.1 * np.random.randn(),
                'y': 0.1 * np.random.randn(),
                'z': base_accel + 0.1 * np.random.randn()
            }

        return gyro_data, accel_data
