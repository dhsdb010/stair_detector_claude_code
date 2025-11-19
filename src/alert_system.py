"""
Alert System Module
Manages warnings and alerts to notify users of potential stair hazards.
"""

import time
import threading
from typing import Optional, Callable
from enum import Enum


class AlertLevel(Enum):
    """Alert severity levels."""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class AlertType(Enum):
    """Types of alerts."""
    STAIR_DETECTED = "stair_detected"
    DISTRACTED_WALKING = "distracted_walking"
    IMMINENT_DANGER = "imminent_danger"


class AlertSystem:
    """
    Manages alert generation and notification delivery.
    """

    def __init__(self, audio_enabled: bool = True, visual_enabled: bool = True,
                 vibration_enabled: bool = True):
        """
        Initialize the alert system.

        Args:
            audio_enabled: Enable audio alerts
            visual_enabled: Enable visual alerts
            vibration_enabled: Enable vibration alerts
        """
        self.audio_enabled = audio_enabled
        self.visual_enabled = visual_enabled
        self.vibration_enabled = vibration_enabled

        self.last_alert_time = {}
        self.alert_cooldown = {
            AlertLevel.LOW: 5.0,      # 5 seconds
            AlertLevel.MEDIUM: 3.0,   # 3 seconds
            AlertLevel.HIGH: 1.0,     # 1 second
            AlertLevel.CRITICAL: 0.5  # 0.5 seconds
        }

        self.alert_callbacks = {
            'audio': None,
            'visual': None,
            'vibration': None
        }

        self.active_alerts = []
        self.alert_history = []
        self.max_history = 100

    def register_callback(self, callback_type: str, callback: Callable):
        """
        Register a callback function for alerts.

        Args:
            callback_type: Type of callback ('audio', 'visual', 'vibration')
            callback: Function to call when alert is triggered
        """
        if callback_type in self.alert_callbacks:
            self.alert_callbacks[callback_type] = callback

    def trigger_alert(self, alert_type: AlertType, level: AlertLevel,
                     message: str, metadata: Optional[dict] = None) -> bool:
        """
        Trigger an alert.

        Args:
            alert_type: Type of alert
            level: Severity level
            message: Alert message
            metadata: Additional alert data

        Returns:
            True if alert was triggered, False if suppressed due to cooldown
        """
        current_time = time.time()

        # Check cooldown
        if alert_type in self.last_alert_time:
            time_since_last = current_time - self.last_alert_time[alert_type]
            if time_since_last < self.alert_cooldown[level]:
                return False

        # Create alert object
        alert = {
            'type': alert_type,
            'level': level,
            'message': message,
            'metadata': metadata or {},
            'timestamp': current_time
        }

        # Add to active alerts
        self.active_alerts.append(alert)

        # Add to history
        self.alert_history.append(alert)
        if len(self.alert_history) > self.max_history:
            self.alert_history.pop(0)

        # Update last alert time
        self.last_alert_time[alert_type] = current_time

        # Trigger callbacks
        self._execute_alerts(alert)

        return True

    def _execute_alerts(self, alert: dict):
        """Execute alert notifications based on enabled channels."""
        level = alert['level']
        message = alert['message']

        # Audio alert
        if self.audio_enabled and self.alert_callbacks['audio']:
            threading.Thread(
                target=self.alert_callbacks['audio'],
                args=(message, level),
                daemon=True
            ).start()
        else:
            # Default audio alert (print with beep)
            if self.audio_enabled:
                self._default_audio_alert(message, level)

        # Visual alert
        if self.visual_enabled and self.alert_callbacks['visual']:
            self.alert_callbacks['visual'](message, level)
        else:
            # Default visual alert (print to console)
            if self.visual_enabled:
                self._default_visual_alert(message, level)

        # Vibration alert
        if self.vibration_enabled and self.alert_callbacks['vibration']:
            threading.Thread(
                target=self.alert_callbacks['vibration'],
                args=(level,),
                daemon=True
            ).start()
        else:
            # Default vibration simulation
            if self.vibration_enabled:
                self._default_vibration_alert(level)

    def _default_audio_alert(self, message: str, level: AlertLevel):
        """Default audio alert implementation."""
        # In a real app, this would play a sound file or use TTS
        # Here we just print with emphasis
        beeps = {
            AlertLevel.LOW: 1,
            AlertLevel.MEDIUM: 2,
            AlertLevel.HIGH: 3,
            AlertLevel.CRITICAL: 5
        }

        print("\a" * beeps.get(level, 1), end='')  # Terminal beep
        print(f"[AUDIO] {message}")

    def _default_visual_alert(self, message: str, level: AlertLevel):
        """Default visual alert implementation."""
        colors = {
            AlertLevel.NONE: '',
            AlertLevel.LOW: '\033[93m',      # Yellow
            AlertLevel.MEDIUM: '\033[38;5;208m',  # Orange
            AlertLevel.HIGH: '\033[91m',     # Red
            AlertLevel.CRITICAL: '\033[1;91m'  # Bold Red
        }
        reset = '\033[0m'

        symbols = {
            AlertLevel.NONE: 'ℹ',
            AlertLevel.LOW: '⚠',
            AlertLevel.MEDIUM: '⚠',
            AlertLevel.HIGH: '⛔',
            AlertLevel.CRITICAL: '🚨'
        }

        color = colors.get(level, '')
        symbol = symbols.get(level, '!')

        print(f"{color}{symbol} [{level.name}] {message}{reset}")

    def _default_vibration_alert(self, level: AlertLevel):
        """Default vibration alert implementation."""
        # Simulate vibration pattern
        patterns = {
            AlertLevel.LOW: [0.1],
            AlertLevel.MEDIUM: [0.1, 0.1, 0.1],
            AlertLevel.HIGH: [0.2, 0.1, 0.2],
            AlertLevel.CRITICAL: [0.3, 0.1, 0.3, 0.1, 0.3]
        }

        pattern = patterns.get(level, [0.1])
        print(f"[VIBRATION] Pattern: {pattern}")

    def evaluate_situation(self, stairs_detected: bool, stairs_confidence: float,
                          is_walking: bool, is_looking_at_phone: bool) -> Optional[dict]:
        """
        Evaluate the current situation and determine appropriate alert level.

        Args:
            stairs_detected: Whether stairs are detected
            stairs_confidence: Confidence level of stair detection (0-1)
            is_walking: Whether user is walking
            is_looking_at_phone: Whether user is looking at phone

        Returns:
            Alert dict if alert should be triggered, None otherwise
        """
        # No alert needed if no stairs
        if not stairs_detected:
            return None

        # Calculate risk level
        risk_score = stairs_confidence

        if is_walking:
            risk_score *= 1.5

        if is_looking_at_phone:
            risk_score *= 2.0

        # Determine alert level and message
        if risk_score >= 2.0:
            level = AlertLevel.CRITICAL
            alert_type = AlertType.IMMINENT_DANGER
            message = "⚠️ DANGER! STAIRS AHEAD - STOP LOOKING AT PHONE!"
        elif risk_score >= 1.2:
            level = AlertLevel.HIGH
            alert_type = AlertType.STAIR_DETECTED
            message = "⚠️ WARNING: Stairs detected while walking distracted!"
        elif risk_score >= 0.8:
            level = AlertLevel.MEDIUM
            alert_type = AlertType.STAIR_DETECTED
            message = "⚠️ Caution: Stairs ahead"
        else:
            level = AlertLevel.LOW
            alert_type = AlertType.STAIR_DETECTED
            message = "ℹ Stairs detected nearby"

        return {
            'type': alert_type,
            'level': level,
            'message': message,
            'metadata': {
                'stairs_confidence': stairs_confidence,
                'is_walking': is_walking,
                'is_looking_at_phone': is_looking_at_phone,
                'risk_score': risk_score
            }
        }

    def clear_active_alerts(self):
        """Clear all active alerts."""
        self.active_alerts = []

    def get_alert_statistics(self) -> dict:
        """Get statistics about triggered alerts."""
        if not self.alert_history:
            return {
                'total_alerts': 0,
                'by_level': {},
                'by_type': {}
            }

        by_level = {}
        by_type = {}

        for alert in self.alert_history:
            level = alert['level'].name
            alert_type = alert['type'].value

            by_level[level] = by_level.get(level, 0) + 1
            by_type[alert_type] = by_type.get(alert_type, 0) + 1

        return {
            'total_alerts': len(self.alert_history),
            'by_level': by_level,
            'by_type': by_type,
            'recent_alerts': self.alert_history[-10:]
        }

    def reset(self):
        """Reset the alert system."""
        self.active_alerts = []
        self.last_alert_time = {}
