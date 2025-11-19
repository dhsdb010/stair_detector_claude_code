//
//  AlertSystem.swift
//  StairDetector
//
//  Manages warnings and alerts with haptic feedback and notifications
//

import Foundation
import UIKit
import AVFoundation
import Combine

enum AlertLevel: Int {
    case none = 0
    case low = 1
    case medium = 2
    case high = 3
    case critical = 4

    var color: UIColor {
        switch self {
        case .none: return .systemGreen
        case .low: return .systemYellow
        case .medium: return .systemOrange
        case .high: return .systemRed
        case .critical: return .systemRed
        }
    }

    var hapticStyle: UIImpactFeedbackGenerator.FeedbackStyle {
        switch self {
        case .none, .low: return .light
        case .medium: return .medium
        case .high, .critical: return .heavy
        }
    }
}

enum AlertType: String {
    case stairDetected = "stair_detected"
    case distractedWalking = "distracted_walking"
    case imminentDanger = "imminent_danger"
}

struct Alert: Identifiable {
    let id = UUID()
    let type: AlertType
    let level: AlertLevel
    let message: String
    let timestamp: Date
    let metadata: [String: Any]

    init(type: AlertType, level: AlertLevel, message: String, metadata: [String: Any] = [:]) {
        self.type = type
        self.level = level
        self.message = message
        self.timestamp = Date()
        self.metadata = metadata
    }
}

class AlertSystem: ObservableObject {
    @Published var currentAlert: Alert?
    @Published var alertHistory: [Alert] = []
    @Published var isAudioEnabled: Bool = true
    @Published var isHapticEnabled: Bool = true

    private var lastAlertTime: [AlertType: Date] = [:]
    private var audioPlayer: AVAudioPlayer?

    private let alertCooldown: [AlertLevel: TimeInterval] = [
        .low: 5.0,
        .medium: 3.0,
        .high: 1.0,
        .critical: 0.5
    ]

    private let maxHistory = 100

    /// Trigger an alert
    @discardableResult
    func triggerAlert(type: AlertType, level: AlertLevel, message: String, metadata: [String: Any] = [:]) -> Bool {
        let now = Date()

        // Check cooldown
        if let lastTime = lastAlertTime[type] {
            let cooldown = alertCooldown[level] ?? 3.0
            if now.timeIntervalSince(lastTime) < cooldown {
                return false
            }
        }

        // Create alert
        let alert = Alert(type: type, level: level, message: message, metadata: metadata)

        // Update state
        DispatchQueue.main.async {
            self.currentAlert = alert
            self.alertHistory.append(alert)

            if self.alertHistory.count > self.maxHistory {
                self.alertHistory.removeFirst()
            }
        }

        lastAlertTime[type] = now

        // Execute alert notifications
        executeAlert(alert)

        return true
    }

    /// Execute alert notifications
    private func executeAlert(_ alert: Alert) {
        // Haptic feedback
        if isHapticEnabled {
            triggerHaptic(for: alert.level)
        }

        // Audio alert
        if isAudioEnabled {
            playAlertSound(for: alert.level)
        }

        // Visual alert (handled by UI through published properties)
    }

    /// Trigger haptic feedback
    private func triggerHaptic(for level: AlertLevel) {
        let generator = UIImpactFeedbackGenerator(style: level.hapticStyle)
        generator.prepare()

        switch level {
        case .critical:
            // Triple vibration for critical
            generator.impactOccurred()
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
                generator.impactOccurred()
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) {
                generator.impactOccurred()
            }

        case .high:
            // Double vibration for high
            generator.impactOccurred()
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
                generator.impactOccurred()
            }

        default:
            // Single vibration
            generator.impactOccurred()
        }
    }

    /// Play alert sound
    private func playAlertSound(for level: AlertLevel) {
        // Use system sounds for alerts
        var soundID: SystemSoundID

        switch level {
        case .critical, .high:
            soundID = 1053 // Critical alert sound
        case .medium:
            soundID = 1054 // Alert sound
        case .low:
            soundID = 1057 // Notification sound
        case .none:
            return
        }

        AudioServicesPlaySystemSound(soundID)

        // For critical alerts, also speak the message
        if level == .critical {
            speakAlert(message: "Warning! Stairs ahead!")
        }
    }

    /// Speak alert message using text-to-speech
    private func speakAlert(message: String) {
        let utterance = AVSpeechUtterance(string: message)
        utterance.voice = AVSpeechSynthesisVoice(language: "en-US")
        utterance.rate = AVSpeechUtteranceDefaultSpeechRate * 1.2
        utterance.volume = 1.0

        let synthesizer = AVSpeechSynthesizer()
        synthesizer.speak(utterance)
    }

    /// Evaluate situation and determine alert
    func evaluateSituation(stairsDetected: Bool, stairsConfidence: Double,
                          isWalking: Bool, isLookingAtPhone: Bool) -> Alert? {
        guard stairsDetected else { return nil }

        // Calculate risk score
        var riskScore = stairsConfidence

        if isWalking {
            riskScore *= 1.5
        }

        if isLookingAtPhone {
            riskScore *= 2.0
        }

        // Determine alert level and message
        let (level, type, message): (AlertLevel, AlertType, String)

        if riskScore >= 2.0 {
            level = .critical
            type = .imminentDanger
            message = "⚠️ DANGER! STAIRS AHEAD - STOP!"
        } else if riskScore >= 1.2 {
            level = .high
            type = .stairDetected
            message = "⚠️ WARNING: Stairs detected while distracted!"
        } else if riskScore >= 0.8 {
            level = .medium
            type = .stairDetected
            message = "⚠️ Caution: Stairs ahead"
        } else {
            level = .low
            type = .stairDetected
            message = "ℹ️ Stairs detected nearby"
        }

        return Alert(
            type: type,
            level: level,
            message: message,
            metadata: [
                "stairsConfidence": stairsConfidence,
                "isWalking": isWalking,
                "isLookingAtPhone": isLookingAtPhone,
                "riskScore": riskScore
            ]
        )
    }

    /// Clear current alert
    func clearAlert() {
        currentAlert = nil
    }

    /// Get alert statistics
    func getStatistics() -> [String: Any] {
        var byLevel: [String: Int] = [:]
        var byType: [String: Int] = [:]

        for alert in alertHistory {
            let levelKey = "\(alert.level)"
            let typeKey = alert.type.rawValue

            byLevel[levelKey, default: 0] += 1
            byType[typeKey, default: 0] += 1
        }

        return [
            "total": alertHistory.count,
            "byLevel": byLevel,
            "byType": byType
        ]
    }

    /// Reset alert system
    func reset() {
        alertHistory.removeAll()
        currentAlert = nil
        lastAlertTime.removeAll()
    }
}
