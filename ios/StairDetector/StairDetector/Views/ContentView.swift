//
//  ContentView.swift
//  StairDetector
//
//  Main view for the stair detection app
//

import SwiftUI

struct ContentView: View {
    @StateObject private var viewModel = StairDetectorViewModel()
    @State private var showSettings = false

    var body: some View {
        ZStack {
            // Camera preview
            CameraPreviewView(cameraManager: viewModel.cameraManager)
                .ignoresSafeArea()

            // Overlay UI
            VStack {
                // Top bar
                HStack {
                    // Settings button
                    Button(action: { showSettings.toggle() }) {
                        Image(systemName: "gearshape.fill")
                            .font(.title2)
                            .foregroundColor(.white)
                            .padding()
                            .background(Color.black.opacity(0.5))
                            .clipShape(Circle())
                    }

                    Spacer()

                    // Statistics button
                    Button(action: { viewModel.showStatistics.toggle() }) {
                        Image(systemName: "chart.bar.fill")
                            .font(.title2)
                            .foregroundColor(.white)
                            .padding()
                            .background(Color.black.opacity(0.5))
                            .clipShape(Circle())
                    }
                }
                .padding()

                Spacer()

                // Alert banner
                if let alert = viewModel.alertSystem.currentAlert {
                    AlertBannerView(alert: alert)
                        .transition(.move(edge: .top))
                        .animation(.spring(), value: alert.id)
                }

                Spacer()

                // Status panel
                StatusPanelView(viewModel: viewModel)
                    .padding()

                // Control button
                ControlButton(viewModel: viewModel)
                    .padding(.bottom, 40)
            }
        }
        .onAppear {
            viewModel.cameraManager.checkAuthorization()
        }
        .sheet(isPresented: $showSettings) {
            SettingsView(viewModel: viewModel)
        }
        .sheet(isPresented: $viewModel.showStatistics) {
            StatisticsView(viewModel: viewModel)
        }
    }
}

struct AlertBannerView: View {
    let alert: Alert

    var body: some View {
        VStack(spacing: 8) {
            HStack {
                Image(systemName: iconName)
                    .font(.title)
                Text(alert.message)
                    .font(.headline)
                    .fontWeight(.bold)
            }
            .foregroundColor(.white)
        }
        .padding()
        .frame(maxWidth: .infinity)
        .background(alert.level.color)
        .cornerRadius(12)
        .shadow(radius: 10)
        .padding(.horizontal)
    }

    private var iconName: String {
        switch alert.level {
        case .critical, .high:
            return "exclamationmark.triangle.fill"
        case .medium:
            return "exclamationmark.circle.fill"
        case .low:
            return "info.circle.fill"
        case .none:
            return "checkmark.circle.fill"
        }
    }
}

struct StatusPanelView: View {
    @ObservedObject var viewModel: StairDetectorViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            StatusRow(
                icon: "figure.stairs",
                label: "Stairs",
                value: viewModel.stairDetector.isStairsDetected ? "YES" : "NO",
                color: viewModel.stairDetector.isStairsDetected ? .red : .green
            )

            StatusRow(
                icon: "figure.walk",
                label: "Walking",
                value: viewModel.motionSensor.isWalking ? "YES" : "NO",
                color: viewModel.motionSensor.isWalking ? .orange : .green
            )

            StatusRow(
                icon: "iphone",
                label: "Looking at Phone",
                value: viewModel.motionSensor.isLookingAtPhone ? "YES" : "NO",
                color: viewModel.motionSensor.isLookingAtPhone ? .orange : .green
            )

            HStack {
                Image(systemName: "speedometer")
                    .foregroundColor(.white)
                Text("FPS: \(String(format: "%.1f", viewModel.fps))")
                    .foregroundColor(.white)
                    .font(.caption)

                Spacer()

                Text("Confidence: \(String(format: "%.0f%%", viewModel.stairDetector.confidence * 100))")
                    .foregroundColor(.white)
                    .font(.caption)
            }
        }
        .padding()
        .background(Color.black.opacity(0.7))
        .cornerRadius(12)
    }
}

struct StatusRow: View {
    let icon: String
    let label: String
    let value: String
    let color: Color

    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(.white)
                .frame(width: 30)

            Text(label)
                .foregroundColor(.white)
                .font(.subheadline)

            Spacer()

            Text(value)
                .foregroundColor(color)
                .font(.subheadline)
                .fontWeight(.bold)
        }
    }
}

struct ControlButton: View {
    @ObservedObject var viewModel: StairDetectorViewModel

    var body: some View {
        Button(action: {
            viewModel.toggleActive()
        }) {
            HStack {
                Image(systemName: viewModel.isActive ? "stop.fill" : "play.fill")
                    .font(.title2)
                Text(viewModel.isActive ? "Stop Detection" : "Start Detection")
                    .font(.headline)
                    .fontWeight(.semibold)
            }
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .padding()
            .background(viewModel.isActive ? Color.red : Color.green)
            .cornerRadius(12)
        }
        .padding(.horizontal)
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
