"""
Unit tests for AlertSystem module
"""

import unittest
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from alert_system import AlertSystem, AlertLevel, AlertType


class TestAlertSystem(unittest.TestCase):
    """Test cases for AlertSystem class."""

    def setUp(self):
        """Set up test fixtures."""
        self.alert_system = AlertSystem()

    def test_initialization(self):
        """Test alert system initialization."""
        self.assertIsNotNone(self.alert_system)
        self.assertTrue(self.alert_system.audio_enabled)
        self.assertTrue(self.alert_system.visual_enabled)
        self.assertTrue(self.alert_system.vibration_enabled)

    def test_trigger_alert(self):
        """Test triggering an alert."""
        result = self.alert_system.trigger_alert(
            AlertType.STAIR_DETECTED,
            AlertLevel.MEDIUM,
            "Test alert"
        )

        self.assertTrue(result)
        self.assertEqual(len(self.alert_system.active_alerts), 1)
        self.assertEqual(len(self.alert_system.alert_history), 1)

    def test_alert_cooldown(self):
        """Test alert cooldown mechanism."""
        # Trigger first alert
        result1 = self.alert_system.trigger_alert(
            AlertType.STAIR_DETECTED,
            AlertLevel.MEDIUM,
            "First alert"
        )
        self.assertTrue(result1)

        # Immediately trigger second alert (should be suppressed)
        result2 = self.alert_system.trigger_alert(
            AlertType.STAIR_DETECTED,
            AlertLevel.MEDIUM,
            "Second alert"
        )
        self.assertFalse(result2)

        # Wait for cooldown and try again
        time.sleep(3.1)  # Medium alert cooldown is 3 seconds

        result3 = self.alert_system.trigger_alert(
            AlertType.STAIR_DETECTED,
            AlertLevel.MEDIUM,
            "Third alert"
        )
        self.assertTrue(result3)

    def test_evaluate_situation_no_stairs(self):
        """Test situation evaluation with no stairs."""
        result = self.alert_system.evaluate_situation(
            stairs_detected=False,
            stairs_confidence=0.0,
            is_walking=True,
            is_looking_at_phone=True
        )

        self.assertIsNone(result)

    def test_evaluate_situation_critical(self):
        """Test situation evaluation for critical alert."""
        result = self.alert_system.evaluate_situation(
            stairs_detected=True,
            stairs_confidence=0.9,
            is_walking=True,
            is_looking_at_phone=True
        )

        self.assertIsNotNone(result)
        self.assertEqual(result['level'], AlertLevel.CRITICAL)

    def test_evaluate_situation_low_risk(self):
        """Test situation evaluation for low risk."""
        result = self.alert_system.evaluate_situation(
            stairs_detected=True,
            stairs_confidence=0.5,
            is_walking=False,
            is_looking_at_phone=False
        )

        self.assertIsNotNone(result)
        self.assertIn(result['level'], [AlertLevel.LOW, AlertLevel.MEDIUM])

    def test_alert_statistics(self):
        """Test alert statistics tracking."""
        # Trigger several alerts
        self.alert_system.trigger_alert(
            AlertType.STAIR_DETECTED,
            AlertLevel.LOW,
            "Alert 1"
        )

        time.sleep(0.1)

        self.alert_system.trigger_alert(
            AlertType.STAIR_DETECTED,
            AlertLevel.HIGH,
            "Alert 2"
        )

        stats = self.alert_system.get_alert_statistics()

        self.assertEqual(stats['total_alerts'], 2)
        self.assertIn('by_level', stats)
        self.assertIn('by_type', stats)

    def test_callback_registration(self):
        """Test callback registration."""
        callback_called = {'called': False}

        def test_callback(message, level):
            callback_called['called'] = True

        self.alert_system.register_callback('audio', test_callback)

        # Trigger alert
        self.alert_system.trigger_alert(
            AlertType.STAIR_DETECTED,
            AlertLevel.MEDIUM,
            "Test"
        )

        # Give callback time to execute
        time.sleep(0.1)

        self.assertTrue(callback_called['called'])

    def test_reset(self):
        """Test alert system reset."""
        # Trigger some alerts
        self.alert_system.trigger_alert(
            AlertType.STAIR_DETECTED,
            AlertLevel.MEDIUM,
            "Test"
        )

        # Reset
        self.alert_system.reset()

        # Verify active alerts are cleared
        self.assertEqual(len(self.alert_system.active_alerts), 0)


if __name__ == '__main__':
    unittest.main()
