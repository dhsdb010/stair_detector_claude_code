//
//  StatisticsView.swift
//  StairDetector
//
//  Statistics and session information view
//

import SwiftUI

struct StatisticsView: View {
    @ObservedObject var viewModel: StairDetectorViewModel
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Session Info
                    GroupBox(label: Label("Session", systemImage: "timer")) {
                        VStack(alignment: .leading, spacing: 12) {
                            StatRow(label: "Duration", value: formatDuration(viewModel.getSessionDuration()))
                            StatRow(label: "Frames Processed", value: "\(viewModel.frameCount)")
                            StatRow(label: "Average FPS", value: String(format: "%.1f", viewModel.fps))
                        }
                    }

                    // Detection Info
                    GroupBox(label: Label("Detection", systemImage: "figure.stairs")) {
                        VStack(alignment: .leading, spacing: 12) {
                            StatRow(
                                label: "Stairs Detected",
                                value: viewModel.stairDetector.isStairsDetected ? "YES" : "NO",
                                color: viewModel.stairDetector.isStairsDetected ? .red : .green
                            )
                            StatRow(
                                label: "Current Confidence",
                                value: String(format: "%.0f%%", viewModel.stairDetector.confidence * 100)
                            )
                        }
                    }

                    // Motion Info
                    GroupBox(label: Label("Motion", systemImage: "figure.walk")) {
                        VStack(alignment: .leading, spacing: 12) {
                            StatRow(
                                label: "Walking",
                                value: viewModel.motionSensor.isWalking ? "YES" : "NO",
                                color: viewModel.motionSensor.isWalking ? .orange : .green
                            )
                            StatRow(
                                label: "Looking at Phone",
                                value: viewModel.motionSensor.isLookingAtPhone ? "YES" : "NO",
                                color: viewModel.motionSensor.isLookingAtPhone ? .orange : .green
                            )
                            StatRow(
                                label: "Phone Tilt",
                                value: String(format: "%.1f°", viewModel.motionSensor.phoneOrientation.tiltAngle)
                            )
                            StatRow(
                                label: "Risk Level",
                                value: viewModel.motionSensor.getRiskLevel().uppercased(),
                                color: riskLevelColor(viewModel.motionSensor.getRiskLevel())
                            )
                        }
                    }

                    // Alert Statistics
                    let stats = viewModel.alertSystem.getStatistics()
                    GroupBox(label: Label("Alerts", systemImage: "bell.badge")) {
                        VStack(alignment: .leading, spacing: 12) {
                            StatRow(
                                label: "Total Alerts",
                                value: "\(stats["total"] as? Int ?? 0)"
                            )

                            if let byLevel = stats["byLevel"] as? [String: Int], !byLevel.isEmpty {
                                Divider()
                                Text("By Level:")
                                    .font(.caption)
                                    .foregroundColor(.secondary)

                                ForEach(byLevel.sorted(by: { $0.key < $1.key }), id: \.key) { key, value in
                                    StatRow(label: "  \(key)", value: "\(value)")
                                }
                            }
                        }
                    }

                    // Recent Alerts
                    if !viewModel.alertSystem.alertHistory.isEmpty {
                        GroupBox(label: Label("Recent Alerts", systemImage: "list.bullet")) {
                            VStack(alignment: .leading, spacing: 8) {
                                ForEach(viewModel.alertSystem.alertHistory.suffix(5).reversed()) { alert in
                                    HStack {
                                        Circle()
                                            .fill(alert.level.color)
                                            .frame(width: 8, height: 8)

                                        VStack(alignment: .leading) {
                                            Text(alert.message)
                                                .font(.caption)
                                            Text(formatTime(alert.timestamp))
                                                .font(.caption2)
                                                .foregroundColor(.secondary)
                                        }

                                        Spacer()
                                    }
                                    .padding(.vertical, 4)

                                    if alert.id != viewModel.alertSystem.alertHistory.suffix(5).last?.id {
                                        Divider()
                                    }
                                }
                            }
                        }
                    }
                }
                .padding()
            }
            .navigationTitle("Statistics")
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

    private func formatDuration(_ duration: TimeInterval) -> String {
        let minutes = Int(duration) / 60
        let seconds = Int(duration) % 60
        return String(format: "%02d:%02d", minutes, seconds)
    }

    private func formatTime(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.timeStyle = .medium
        return formatter.string(from: date)
    }

    private func riskLevelColor(_ level: String) -> Color {
        switch level.lowercased() {
        case "none":
            return .green
        case "low":
            return .yellow
        case "medium":
            return .orange
        case "high":
            return .red
        default:
            return .gray
        }
    }
}

struct StatRow: View {
    let label: String
    let value: String
    var color: Color = .primary

    var body: some View {
        HStack {
            Text(label)
                .font(.subheadline)
            Spacer()
            Text(value)
                .font(.subheadline)
                .fontWeight(.semibold)
                .foregroundColor(color)
        }
    }
}

struct StatisticsView_Previews: PreviewProvider {
    static var previews: some View {
        StatisticsView(viewModel: StairDetectorViewModel())
    }
}
