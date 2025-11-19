# Stair Detection Safety System - iOS App

Native iOS implementation of the Stair Detection Safety System using Swift, SwiftUI, Vision framework, and CoreMotion.

## Features

### Core Functionality
- ✅ Real-time stair detection using Vision framework
- ✅ Motion sensor integration (accelerometer + gyroscope)
- ✅ Walking detection with step counting
- ✅ Phone orientation tracking
- ✅ Multi-level alert system (Low, Medium, High, Critical)
- ✅ Haptic feedback (vibration patterns)
- ✅ Audio alerts with text-to-speech for critical warnings
- ✅ Live camera preview with overlay UI
- ✅ Statistics and session tracking

### iOS-Specific Features
- Native haptic engine integration
- System sound alerts
- AVSpeechSynthesizer for voice warnings
- Portrait-only orientation lock
- Background mode support (when needed)
- Battery-optimized processing

## Requirements

- iOS 15.0 or later
- iPhone with camera
- Xcode 14.0 or later
- Swift 5.0 or later

## Installation

### Option 1: Open in Xcode

1. Navigate to the iOS directory:
```bash
cd ios/StairDetector
```

2. Open the project in Xcode:
```bash
open StairDetector.xcodeproj
```

3. Select your development team in **Signing & Capabilities**

4. Connect your iPhone device

5. Build and run (⌘ + R)

### Option 2: Command Line Build

```bash
cd ios/StairDetector

# Build for device
xcodebuild -scheme StairDetector \
  -configuration Release \
  -destination 'generic/platform=iOS' \
  build

# Or use xcodebuild with simulator
xcodebuild -scheme StairDetector \
  -configuration Debug \
  -destination 'platform=iOS Simulator,name=iPhone 14' \
  build
```

## Project Structure

```
ios/StairDetector/
├── StairDetector/
│   ├── Services/
│   │   ├── StairDetector.swift      # Vision-based stair detection
│   │   ├── MotionSensor.swift       # CoreMotion integration
│   │   ├── AlertSystem.swift        # Alert management + haptics
│   │   └── CameraManager.swift      # Camera capture + preview
│   ├── Models/
│   │   └── StairDetectorViewModel.swift  # Main coordinator
│   ├── Views/
│   │   ├── ContentView.swift        # Main app view
│   │   ├── CameraPreviewView.swift  # Camera preview wrapper
│   │   ├── SettingsView.swift       # Settings screen
│   │   └── StatisticsView.swift     # Statistics screen
│   ├── Resources/
│   │   └── Assets.xcassets          # App icons and images
│   ├── Info.plist                   # App configuration
│   └── StairDetectorApp.swift       # App entry point
└── StairDetector.xcodeproj/         # Xcode project
```

## Usage

### First Launch

1. **Grant Permissions**: The app will request:
   - Camera access (required for stair detection)
   - Motion sensor access (required for walking detection)

2. **Tap "Start Detection"** to begin monitoring

3. **Walk normally** - the app runs in the background

### Main Screen

- **Camera Preview**: Shows live feed from rear camera
- **Status Panel**: Displays current detection state
  - Stairs detected (YES/NO)
  - Walking (YES/NO)
  - Looking at phone (YES/NO)
  - FPS and confidence metrics
- **Alert Banner**: Shows warnings when risks are detected
- **Control Button**: Start/Stop detection

### Settings

Access via gear icon (⚙️):

- **Sensitivity**: Adjust detection sensitivity (0.0 - 1.0)
  - Higher = more sensitive, but more false positives
  - Lower = less sensitive, fewer alerts
- **Audio Alerts**: Enable/disable sound alerts
- **Haptic Feedback**: Enable/disable vibration
- **Reset Statistics**: Clear session data

### Statistics

Access via chart icon (📊):

- Session duration and frame count
- Detection metrics
- Motion data (walking, tilt angle)
- Alert history and counts
- Recent alerts log

## How It Works

### 1. Stair Detection (Vision Framework)

```swift
// Two-stage detection approach:

1. Rectangle Detection
   - Uses VNDetectRectanglesRequest
   - Filters for horizontal rectangles (stair steps)
   - Checks spacing consistency

2. Edge Detection
   - Applies CIFilter edge detection
   - Scans for horizontal lines
   - Counts lines in lower 2/3 of frame
```

### 2. Motion Sensing (CoreMotion)

```swift
// Combines multiple sensors:

1. Device Motion (CMDeviceMotion)
   - Attitude (pitch, roll, yaw)
   - Gravity vector
   - Calculates tilt angle

2. Accelerometer (CMAccelerometer)
   - Detects walking patterns
   - Analyzes periodic motion (1-2 Hz)
   - Counts steps via peak detection

3. Gyroscope (CMGyroscope)
   - Tracks rotational changes
   - Assists in orientation calculation
```

### 3. Alert System

```swift
// Risk calculation:
riskScore = stairsConfidence × walkingMultiplier × distractionMultiplier

// Alert levels:
if riskScore >= 2.0 {
    level = .critical  // Red alert + triple vibration + voice
} else if riskScore >= 1.2 {
    level = .high      // Red alert + double vibration
} else if riskScore >= 0.8 {
    level = .medium    // Orange alert + single vibration
} else {
    level = .low       // Yellow alert + gentle vibration
}
```

### 4. Haptic Patterns

The app uses iOS haptic engine for tactile feedback:

- **Critical**: Heavy impact × 3 (0.2s intervals)
- **High**: Heavy impact × 2 (0.2s intervals)
- **Medium**: Medium impact × 1
- **Low**: Light impact × 1

## Permissions

The app requires the following permissions (configured in `Info.plist`):

### Camera (`NSCameraUsageDescription`)
```
"The camera is used to detect stairs in real-time to help prevent accidents while walking."
```

### Motion Sensors (`NSMotionUsageDescription`)
```
"Motion sensors are used to detect when you're walking and looking at your phone to provide safety alerts."
```

## Performance

- **Target FPS**: 15-30 FPS (configurable)
- **Battery Impact**: Medium (continuous camera + sensors)
- **Memory Usage**: ~50-100 MB
- **CPU Usage**: 20-40% on modern devices

### Optimization Tips

1. **Reduce FPS**: Lower frame rate = better battery life
2. **Adjust Sensitivity**: Lower sensitivity = less processing
3. **Disable Audio**: Saves resources if not needed
4. **Use in Portrait**: Optimized for portrait mode

## Troubleshooting

### Camera Not Working

1. Check Settings → Privacy → Camera → StairDetector (ON)
2. Restart the app
3. Restart your device

### Motion Sensors Not Responding

1. Check Settings → Privacy → Motion & Fitness → StairDetector (ON)
2. Ensure device is not in Low Power Mode
3. Calibrate compass (Settings → Privacy → Location Services → System Services → Compass Calibration)

### Frequent False Positives

1. Increase sensitivity threshold in Settings
2. Ensure good lighting conditions
3. Keep camera lens clean

### High Battery Drain

1. Reduce detection sensitivity
2. Use only when needed (not continuously)
3. Disable audio alerts
4. Close other background apps

## Development

### Building from Source

1. Clone the repository:
```bash
git clone https://github.com/dhsdb010/stair_detector_claude_code.git
cd stair_detector_claude_code/ios/StairDetector
```

2. Open in Xcode:
```bash
open StairDetector.xcodeproj
```

3. Update bundle identifier and team in project settings

4. Build and run on device

### Adding New Features

The app follows MVVM architecture:

- **Models**: Data structures and business logic
- **Views**: SwiftUI UI components
- **ViewModels**: Coordination and state management
- **Services**: Core functionality (detection, sensors, alerts)

Example - Adding a new alert type:

```swift
// 1. Add to AlertType enum in AlertSystem.swift
enum AlertType: String {
    case stairDetected = "stair_detected"
    case distractedWalking = "distracted_walking"
    case imminentDanger = "imminent_danger"
    case newAlertType = "new_alert_type"  // Add here
}

// 2. Update evaluateSituation() logic
func evaluateSituation(...) -> Alert? {
    // Your custom logic
}

// 3. Update UI in ContentView.swift if needed
```

## Testing

### Manual Testing Scenarios

1. **Stair Detection**
   - Point camera at stairs → Should detect within 1-2 seconds
   - Point at flat surface → Should not detect

2. **Walking Detection**
   - Walk normally with phone → Should detect walking
   - Stand still → Should show not walking

3. **Phone Orientation**
   - Hold phone at viewing angle (30-80°) → "Looking at phone" = YES
   - Hold phone vertically → "Looking at phone" = NO

4. **Alert System**
   - Walk toward stairs while looking at phone → Should trigger critical alert
   - Stand near stairs → Should trigger low alert only

### Unit Testing

```bash
# Run tests from command line
xcodebuild test -scheme StairDetector \
  -destination 'platform=iOS Simulator,name=iPhone 14'
```

## Safety Notice

⚠️ **IMPORTANT**: This app is an assistive safety tool and should NOT be relied upon as the sole means of preventing accidents.

Users should always:
- Remain aware of their surroundings
- Avoid phone use while walking in hazardous areas
- Use handrails on stairs
- Follow all safety guidelines

## Privacy

The app:
- ✅ Processes all data locally on device
- ✅ Does NOT collect or transmit any data
- ✅ Does NOT store camera images
- ✅ Does NOT track location
- ✅ Does NOT require internet connection

## Known Limitations

- Works best in good lighting conditions
- May not detect all stair types (spiral, transparent, etc.)
- Walking detection requires consistent gait
- Camera must have clear view of stairs
- Performance varies by device model

## Future Enhancements

- [ ] Machine learning model for improved detection
- [ ] Depth sensor support (LiDAR on Pro models)
- [ ] Obstacle detection (not just stairs)
- [ ] Widget support
- [ ] Apple Watch companion app
- [ ] Accessibility features (VoiceOver support)
- [ ] Localization (multiple languages)
- [ ] Dark mode optimization

## Support

For issues, questions, or feature requests:

- GitHub Issues: https://github.com/dhsdb010/stair_detector_claude_code/issues
- Email: [Your contact]

## License

MIT License - see [LICENSE](../LICENSE) file for details.

## Acknowledgments

- Apple Vision framework documentation
- CoreMotion programming guide
- SwiftUI tutorials and community
- iOS haptic feedback design guidelines

---

**Made with ❤️ for pedestrian safety**

Stay safe! Look up, not down (at your phone) when near stairs! 🚶‍♂️📱⚠️
