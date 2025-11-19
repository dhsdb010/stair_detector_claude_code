//
//  StairDetectorViewModel.swift
//  StairDetector
//
//  Main view model coordinating all services
//

import Foundation
import SwiftUI
import Combine

class StairDetectorViewModel: ObservableObject {
    // Services
    @Published var cameraManager = CameraManager()
    @Published var stairDetector = StairDetector()
    @Published var motionSensor = MotionSensor()
    @Published var alertSystem = AlertSystem()

    // UI State
    @Published var isActive = false
    @Published var showStatistics = false
    @Published var frameCount: Int = 0
    @Published var fps: Double = 0.0

    // Settings
    @Published var sensitivity: Double = 0.7 {
        didSet {
            stairDetector = StairDetector(sensitivity: sensitivity)
        }
    }

    private var cancellables = Set<AnyCancellable>()
    private var startTime: Date?
    private var fpsTimer: Timer?

    init() {
        setupBindings()
    }

    /// Setup reactive bindings
    private func setupBindings() {
        // Handle camera frames
        cameraManager.onFrameCaptured = { [weak self] image in
            self?.processFrame(image)
        }

        // Monitor detection and motion state
        Publishers.CombineLatest4(
            stairDetector.$isStairsDetected,
            stairDetector.$confidence,
            motionSensor.$isWalking,
            motionSensor.$isLookingAtPhone
        )
        .debounce(for: .milliseconds(100), scheduler: DispatchQueue.main)
        .sink { [weak self] stairsDetected, confidence, isWalking, isLookingAtPhone in
            self?.evaluateAndAlert(
                stairsDetected: stairsDetected,
                confidence: confidence,
                isWalking: isWalking,
                isLookingAtPhone: isLookingAtPhone
            )
        }
        .store(in: &cancellables)
    }

    /// Start the detection system
    func start() {
        guard !isActive else { return }

        isActive = true
        startTime = Date()
        frameCount = 0

        // Start services
        cameraManager.startSession()
        motionSensor.startMonitoring()

        // Start FPS counter
        startFPSCounter()
    }

    /// Stop the detection system
    func stop() {
        guard isActive else { return }

        isActive = false

        // Stop services
        cameraManager.stopSession()
        motionSensor.stopMonitoring()

        // Stop FPS counter
        fpsTimer?.invalidate()
        fpsTimer = nil
    }

    /// Process a single frame
    private func processFrame(_ image: UIImage) {
        guard isActive else { return }

        frameCount += 1

        // Detect stairs in frame
        stairDetector.detectStairs(in: image)
    }

    /// Evaluate situation and trigger alerts
    private func evaluateAndAlert(stairsDetected: Bool, confidence: Double,
                                  isWalking: Bool, isLookingAtPhone: Bool) {
        guard let alert = alertSystem.evaluateSituation(
            stairsDetected: stairsDetected,
            stairsConfidence: confidence,
            isWalking: isWalking,
            isLookingAtPhone: isLookingAtPhone
        ) else {
            return
        }

        alertSystem.triggerAlert(
            type: alert.type,
            level: alert.level,
            message: alert.message,
            metadata: alert.metadata
        )
    }

    /// Start FPS counter
    private func startFPSCounter() {
        fpsTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            guard let self = self, let startTime = self.startTime else { return }

            let elapsed = Date().timeIntervalSince(startTime)
            self.fps = elapsed > 0 ? Double(self.frameCount) / elapsed : 0
        }
    }

    /// Get session duration
    func getSessionDuration() -> TimeInterval {
        guard let startTime = startTime else { return 0 }
        return Date().timeIntervalSince(startTime)
    }

    /// Reset all systems
    func reset() {
        stairDetector.reset()
        motionSensor.reset()
        alertSystem.reset()
        frameCount = 0
        startTime = nil
    }

    /// Toggle active state
    func toggleActive() {
        if isActive {
            stop()
        } else {
            start()
        }
    }

    deinit {
        stop()
    }
}
