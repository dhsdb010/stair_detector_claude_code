# Stair Detection Safety System

A phone-based safety system that uses computer vision and motion sensors to detect stairs and warn distracted users, preventing accidents while walking and using mobile devices.

## Overview

Walking while distracted by a phone is a common cause of accidents, especially near stairs. This system combines:

- **Computer Vision**: Real-time stair detection using edge detection and pattern recognition
- **Motion Sensors**: Gyroscope and accelerometer analysis to detect user activity and phone orientation
- **Smart Alerts**: Context-aware warnings based on risk level (audio, visual, and vibration)

## Features

### Stair Detection
- Real-time edge detection and line analysis
- Pattern recognition for horizontal parallel lines characteristic of stairs
- Temporal filtering to reduce false positives
- Adjustable sensitivity settings

### Motion Analysis
- Walking detection through accelerometer patterns
- Phone orientation tracking (gyroscope + accelerometer)
- Detection of "looking at phone" behavior based on tilt angle
- Risk level assessment

### Alert System
- Multi-level alerts (Low, Medium, High, Critical)
- Multiple notification channels:
  - Audio alerts with customizable sounds
  - Visual on-screen warnings
  - Vibration patterns
- Smart cooldown to prevent alert fatigue
- Context-aware risk evaluation

## Installation

### Prerequisites

- Python 3.7 or higher
- Camera device (webcam or phone camera)
- (Optional) Access to device gyroscope/accelerometer

### Setup

1. Clone the repository:
```bash
git clone https://github.com/dhsdb010/stair_detector_claude_code.git
cd stair_detector_claude_code
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Install additional dependencies for enhanced features:
```bash
pip install pillow scipy matplotlib
```

## Usage

### Quick Start

Run the demo to see the system in action with simulated data:

```bash
python demo.py
```

### Run with Camera

Start the full application with your camera:

```bash
python src/main.py
```

### Command Line Options

```bash
# Use a specific camera (default: 0)
python src/main.py --camera 1

# Adjust detection sensitivity (0.0 to 1.0, default: 0.7)
python src/main.py --sensitivity 0.8

# Run in simulation mode (for testing without sensors)
python src/main.py --simulate

# Run without visualization window (headless mode)
python src/main.py --no-viz

# Combine options
python src/main.py --camera 1 --sensitivity 0.8 --simulate
```

### Controls (when visualization is enabled)

- **Q**: Quit the application
- **S**: Toggle visualization on/off

## Project Structure

```
stair_detector_claude_code/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── stair_detector.py     # Computer vision stair detection
│   ├── motion_sensor.py      # Gyroscope/accelerometer processing
│   ├── alert_system.py       # Alert management and notifications
│   └── main.py              # Main application
├── tests/
│   ├── __init__.py
│   ├── test_stair_detector.py
│   ├── test_motion_sensor.py
│   └── test_alert_system.py
├── models/                   # Directory for trained ML models (future)
├── config.py                # Configuration settings
├── demo.py                  # Demonstration script
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## How It Works

### 1. Stair Detection Pipeline

```
Camera Frame
    ↓
Preprocessing (Grayscale, Blur, Contrast Enhancement)
    ↓
Edge Detection (Canny)
    ↓
Line Detection (Hough Transform)
    ↓
Pattern Analysis (Horizontal lines, spacing consistency)
    ↓
Temporal Filtering (Multiple frames consensus)
    ↓
Detection Result (Boolean + Confidence)
```

### 2. Motion Analysis Pipeline

```
Sensor Data (Gyro + Accel)
    ↓
Orientation Calculation (Pitch, Roll, Tilt)
    ↓
Activity Detection (Walking pattern analysis)
    ↓
Behavior Analysis (Phone usage detection)
    ↓
State Output (Walking, Looking at Phone)
```

### 3. Risk Evaluation

The system calculates a risk score based on:

```python
risk_score = stairs_confidence × walking_multiplier × distraction_multiplier

Where:
- walking_multiplier = 1.5 if walking, else 1.0
- distraction_multiplier = 2.0 if looking at phone, else 1.0
```

Alert levels:
- **Critical** (≥2.0): Immediate danger - stairs ahead while walking distracted
- **High** (≥1.2): Warning - stairs detected with high risk factors
- **Medium** (≥0.8): Caution - stairs nearby with some risk
- **Low** (<0.8): Information - stairs detected, low risk

## Configuration

Edit `config.py` to customize system behavior:

```python
# Detection sensitivity
STAIR_DETECTION_SENSITIVITY = 0.7  # 0.0 (low) to 1.0 (high)

# Motion thresholds
WALKING_ACCEL_THRESHOLD = 1.5  # m/s^2
PHONE_TILT_THRESHOLD = 30      # degrees

# Alert settings
ENABLE_AUDIO_ALERTS = True
ENABLE_VISUAL_ALERTS = True
ENABLE_VIBRATION_ALERTS = True
```

## Testing

Run the test suite:

```bash
# Run all tests
python -m unittest discover tests

# Run specific test module
python -m unittest tests.test_stair_detector

# Run with verbose output
python -m unittest discover tests -v
```

## Technical Details

### Stair Detection Algorithm

The stair detection module uses a multi-stage approach:

1. **Preprocessing**: Converts to grayscale, applies Gaussian blur, and enhances contrast using CLAHE
2. **Edge Detection**: Adaptive Canny edge detection with automatic threshold adjustment
3. **Line Detection**: Probabilistic Hough Transform to find line segments
4. **Pattern Matching**: Filters for horizontal lines in the lower 2/3 of the frame
5. **Spacing Analysis**: Checks for regular spacing between lines (characteristic of stairs)
6. **Temporal Filtering**: Requires consensus across multiple frames to confirm detection

### Motion Sensor Analysis

The motion sensor module analyzes:

- **Gyroscope**: Rotational velocity (rad/s) in x, y, z axes
- **Accelerometer**: Linear acceleration (m/s²) in x, y, z axes

Key calculations:
```python
# Phone orientation
pitch = arctan2(ax, sqrt(ay² + az²))
roll = arctan2(ay, sqrt(ax² + az²))
tilt_angle = arctan2(sqrt(ax² + ay²), az)

# Walking detection
# Periodic variation in acceleration magnitude (1-2 Hz typical)
# Standard deviation > threshold indicates walking
```

### Alert System

The alert system implements:
- **Cooldown periods**: Prevents alert spam while maintaining safety
- **Risk-based escalation**: Higher risk = more frequent/intense alerts
- **Multi-modal notifications**: Audio, visual, and haptic feedback
- **Callback architecture**: Extensible for custom alert handlers

## Mobile Deployment

While this implementation runs on desktop with a webcam, it can be adapted for mobile platforms:

### Android
- Use **Kivy** or **BeeWare** for Python-based mobile apps
- Access sensors via **Pyjnius** (Python-Java bridge)
- Alternative: Rewrite in Kotlin/Java using OpenCV Android SDK

### iOS
- Use **Kivy** or **BeeWare** for Python-based apps
- Alternative: Rewrite in Swift using Vision framework

### React Native / Flutter
- Python backend as a service (REST API)
- Native modules for sensor access
- WebRTC for camera streaming

## Performance Considerations

- **Frame Rate**: Targets 15-30 FPS on typical hardware
- **CPU Usage**: Optimized for mobile processors (efficient edge detection)
- **Battery**: Adjustable frame rate and sensitivity to balance safety vs. battery life
- **Memory**: Bounded history buffers prevent memory leaks

## Future Enhancements

- [ ] Machine Learning model for improved stair detection (CNN-based)
- [ ] Depth sensing support (using dual cameras or ToF sensors)
- [ ] Obstacle detection (not just stairs)
- [ ] User customizable alert preferences
- [ ] Cloud-based learning from user feedback
- [ ] Integration with accessibility features
- [ ] Multi-language support
- [ ] Wearable device integration (smartwatch alerts)

## Safety Disclaimer

This system is designed as an **assistive safety tool** and should **not be relied upon as the sole means of preventing accidents**. Users should always:

- Remain aware of their surroundings
- Avoid phone use while walking in hazardous areas
- Use handrails on stairs
- Follow all safety guidelines and local regulations

The developers are not liable for any accidents or injuries that may occur while using this system.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenCV community for excellent computer vision tools
- Research papers on pedestrian safety and distracted walking
- Contributors to NumPy and other open-source libraries

## Contact

For questions, issues, or suggestions:
- Open an issue on GitHub
- Contact: [Your contact information]

## Citation

If you use this project in your research, please cite:

```bibtex
@software{stair_detector_2024,
  title = {Stair Detection Safety System},
  author = {Stair Detector Team},
  year = {2024},
  url = {https://github.com/dhsdb010/stair_detector_claude_code}
}
```

---

**Stay Safe! Look Up, Not Down (at your phone) when near stairs!** 🚶‍♂️📱⚠️
