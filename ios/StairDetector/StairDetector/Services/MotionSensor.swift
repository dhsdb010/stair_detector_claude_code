//
//  MotionSensor.swift
//  StairDetector
//
//  Processes gyroscope and accelerometer data to detect phone orientation and walking
//

import Foundation
import CoreMotion
import Combine

class MotionSensor: ObservableObject {
    @Published var isWalking: Bool = false
    @Published var isLookingAtPhone: Bool = false
    @Published var phoneOrientation: PhoneOrientation = PhoneOrientation()
    @Published var isDistracted: Bool = false

    private let motionManager = CMMotionManager()
    private var accelHistory: [(timestamp: Double, data: CMAcceleration)] = []
    private var gyroHistory: [(timestamp: Double, data: CMRotationRate)] = []

    private let windowSize = 20
    private let walkingAccelThreshold = 1.5
    private let phoneTiltThreshold = 30.0

    private var updateTimer: Timer?

    struct PhoneOrientation {
        var pitch: Double = 0.0
        var roll: Double = 0.0
        var tiltAngle: Double = 0.0
    }

    init() {
        setupMotionManager()
    }

    /// Setup and start motion manager
    private func setupMotionManager() {
        guard motionManager.isDeviceMotionAvailable else {
            print("Device motion is not available")
            return
        }

        motionManager.deviceMotionUpdateInterval = 0.1 // 10 Hz
        motionManager.accelerometerUpdateInterval = 0.1
        motionManager.gyroUpdateInterval = 0.1
    }

    /// Start monitoring motion
    func startMonitoring() {
        // Start device motion updates
        motionManager.startDeviceMotionUpdates(to: .main) { [weak self] motion, error in
            guard let self = self, let motion = motion else { return }

            self.processMotionData(motion)
        }

        // Start accelerometer updates for walking detection
        motionManager.startAccelerometerUpdates(to: .main) { [weak self] data, error in
            guard let self = self, let data = data else { return }

            self.processAccelerometerData(data)
        }

        // Start gyroscope updates
        motionManager.startGyroUpdates(to: .main) { [weak self] data, error in
            guard let self = self, let data = data else { return }

            self.processGyroData(data)
        }
    }

    /// Stop monitoring motion
    func stopMonitoring() {
        motionManager.stopDeviceMotionUpdates()
        motionManager.stopAccelerometerUpdates()
        motionManager.stopGyroUpdates()
        updateTimer?.invalidate()
    }

    /// Process device motion data
    private func processMotionData(_ motion: CMDeviceMotion) {
        let timestamp = Date().timeIntervalSince1970

        // Calculate phone orientation
        let attitude = motion.attitude

        // Calculate tilt angle from vertical
        // When phone is vertical (portrait): tilt ≈ 0
        // When phone is horizontal: tilt ≈ 90
        let gravity = motion.gravity
        let ax = gravity.x
        let ay = gravity.y
        let az = gravity.z

        let pitch = atan2(ax, sqrt(ay * ay + az * az)) * 180 / .pi
        let roll = atan2(ay, sqrt(ax * ax + az * az)) * 180 / .pi
        let tilt = atan2(sqrt(ax * ax + ay * ay), az) * 180 / .pi

        DispatchQueue.main.async {
            self.phoneOrientation = PhoneOrientation(
                pitch: pitch,
                roll: roll,
                tiltAngle: tilt
            )

            // Update looking at phone status
            // Typical viewing angle: 30-80 degrees from vertical
            self.isLookingAtPhone = tilt > self.phoneTiltThreshold && tilt < 85

            // Update distracted status
            self.isDistracted = self.isWalking && self.isLookingAtPhone
        }
    }

    /// Process accelerometer data for walking detection
    private func processAccelerometerData(_ data: CMAccelerometerData) {
        let timestamp = Date().timeIntervalSince1970

        // Add to history
        accelHistory.append((timestamp: timestamp, data: data.acceleration))

        // Maintain window size
        if accelHistory.count > windowSize {
            accelHistory.removeFirst()
        }

        // Detect walking if we have enough samples
        if accelHistory.count >= 10 {
            detectWalking()
        }
    }

    /// Process gyroscope data
    private func processGyroData(_ data: CMGyroData) {
        let timestamp = Date().timeIntervalSince1970

        gyroHistory.append((timestamp: timestamp, data: data.rotationRate))

        if gyroHistory.count > windowSize {
            gyroHistory.removeFirst()
        }
    }

    /// Detect walking based on accelerometer patterns
    private func detectWalking() {
        guard accelHistory.count >= 10 else { return }

        // Calculate magnitude of acceleration (removing gravity)
        var magnitudes: [Double] = []

        for entry in accelHistory {
            let accel = entry.data
            let magnitude = sqrt(accel.x * accel.x + accel.y * accel.y + accel.z * accel.z)
            magnitudes.append(abs(magnitude - 1.0)) // 1g = 9.8 m/s^2 normalized
        }

        // Calculate variation
        let mean = magnitudes.reduce(0, +) / Double(magnitudes.count)
        let variance = magnitudes.map { pow($0 - mean, 2) }.reduce(0, +) / Double(magnitudes.count)
        let stdDev = sqrt(variance)

        // Walking shows periodic variation
        let isWalkingDetected = stdDev > (walkingAccelThreshold / 10.0) && mean > 0.05

        // Additional check: count peaks (step detection)
        var peakCount = 0
        if isWalkingDetected && magnitudes.count >= 15 {
            let threshold = mean + 0.6 * stdDev

            for i in 1..<(magnitudes.count - 1) {
                if magnitudes[i] > magnitudes[i - 1] &&
                   magnitudes[i] > magnitudes[i + 1] &&
                   magnitudes[i] > threshold {
                    peakCount += 1
                }
            }
        }

        DispatchQueue.main.async {
            self.isWalking = isWalkingDetected && peakCount >= 2
        }
    }

    /// Get risk level
    func getRiskLevel() -> String {
        if !isWalking {
            return "none"
        }

        if isDistracted {
            return "high"
        }

        if isLookingAtPhone {
            return "medium"
        }

        return "low"
    }

    /// Reset sensor history
    func reset() {
        accelHistory.removeAll()
        gyroHistory.removeAll()
        isWalking = false
        isLookingAtPhone = false
        isDistracted = false
    }

    deinit {
        stopMonitoring()
    }
}
