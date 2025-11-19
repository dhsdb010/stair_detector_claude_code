"""
Configuration file for Stair Detection Safety System
Adjust these settings to customize the system behavior.
"""

# Camera Settings
CAMERA_INDEX = 0  # Default camera device index
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# Detection Settings
STAIR_DETECTION_SENSITIVITY = 0.7  # 0.0 (low) to 1.0 (high)
MIN_STAIR_CONFIDENCE = 0.5  # Minimum confidence to trigger alert

# Motion Sensor Settings
MOTION_WINDOW_SIZE = 20  # Number of sensor samples to keep
WALKING_ACCEL_THRESHOLD = 1.5  # m/s^2 variation to detect walking
PHONE_TILT_THRESHOLD = 30  # Degrees from vertical to consider "looking at phone"

# Alert Settings
ENABLE_AUDIO_ALERTS = True
ENABLE_VISUAL_ALERTS = True
ENABLE_VIBRATION_ALERTS = True

# Alert cooldown periods (seconds)
ALERT_COOLDOWN_LOW = 5.0
ALERT_COOLDOWN_MEDIUM = 3.0
ALERT_COOLDOWN_HIGH = 1.0
ALERT_COOLDOWN_CRITICAL = 0.5

# Risk Level Thresholds
RISK_THRESHOLD_MEDIUM = 0.8
RISK_THRESHOLD_HIGH = 1.2
RISK_THRESHOLD_CRITICAL = 2.0

# Display Settings
SHOW_VISUALIZATION = True
DISPLAY_FPS = True
DISPLAY_DETECTION_INFO = True

# Performance Settings
TEMPORAL_FILTER_FRAMES = 5  # Number of frames for temporal consistency
MAX_FRAME_RATE = 30  # Maximum processing frame rate

# Logging Settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = False
LOG_FILE_PATH = "stair_detector.log"

# Advanced Settings
USE_GPU_ACCELERATION = False  # Requires OpenCV with CUDA support
ENABLE_TELEMETRY = False  # Log usage statistics
