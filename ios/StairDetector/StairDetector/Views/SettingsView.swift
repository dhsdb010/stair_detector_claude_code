//
//  SettingsView.swift
//  StairDetector
//
//  Settings and configuration view
//

import SwiftUI

struct SettingsView: View {
    @ObservedObject var viewModel: StairDetectorViewModel
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Detection")) {
                    VStack(alignment: .leading) {
                        Text("Sensitivity: \(String(format: "%.1f", viewModel.sensitivity))")
                            .font(.subheadline)

                        Slider(value: $viewModel.sensitivity, in: 0.0...1.0, step: 0.1)
                    }

                    Text("Higher sensitivity detects stairs more easily but may have more false positives.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Section(header: Text("Alerts")) {
                    Toggle("Audio Alerts", isOn: $viewModel.alertSystem.isAudioEnabled)
                    Toggle("Haptic Feedback", isOn: $viewModel.alertSystem.isHapticEnabled)

                    Text("Audio alerts use system sounds and text-to-speech for critical warnings.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Section(header: Text("System")) {
                    HStack {
                        Text("Camera Status")
                        Spacer()
                        Text(cameraStatusText)
                            .foregroundColor(cameraStatusColor)
                    }

                    HStack {
                        Text("Motion Sensors")
                        Spacer()
                        Text("Active")
                            .foregroundColor(.green)
                    }
                }

                Section(header: Text("Actions")) {
                    Button(action: {
                        viewModel.reset()
                    }) {
                        HStack {
                            Image(systemName: "arrow.clockwise")
                            Text("Reset Statistics")
                        }
                    }
                }

                Section(header: Text("About")) {
                    HStack {
                        Text("Version")
                        Spacer()
                        Text("1.0.0")
                            .foregroundColor(.secondary)
                    }

                    Link(destination: URL(string: "https://github.com/dhsdb010/stair_detector_claude_code")!) {
                        HStack {
                            Image(systemName: "link")
                            Text("GitHub Repository")
                        }
                    }

                    Text("Stair Detection Safety System helps prevent accidents by warning you when stairs are detected while you're distracted by your phone.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }

    private var cameraStatusText: String {
        switch viewModel.cameraManager.authorizationStatus {
        case .authorized:
            return "Authorized"
        case .denied, .restricted:
            return "Denied"
        case .notDetermined:
            return "Not Determined"
        @unknown default:
            return "Unknown"
        }
    }

    private var cameraStatusColor: Color {
        switch viewModel.cameraManager.authorizationStatus {
        case .authorized:
            return .green
        case .denied, .restricted:
            return .red
        case .notDetermined:
            return .orange
        @unknown default:
            return .gray
        }
    }
}

struct SettingsView_Previews: PreviewProvider {
    static var previews: some View {
        SettingsView(viewModel: StairDetectorViewModel())
    }
}
