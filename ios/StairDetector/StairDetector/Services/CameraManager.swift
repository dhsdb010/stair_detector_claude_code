//
//  CameraManager.swift
//  StairDetector
//
//  Manages camera feed and frame capture
//

import Foundation
import AVFoundation
import UIKit
import Combine

class CameraManager: NSObject, ObservableObject {
    @Published var currentFrame: UIImage?
    @Published var isSessionRunning = false
    @Published var authorizationStatus: AVAuthorizationStatus = .notDetermined

    private let captureSession = AVCaptureSession()
    private let videoOutput = AVCaptureVideoDataOutput()
    private let sessionQueue = DispatchQueue(label: "camera.session.queue")

    var onFrameCaptured: ((UIImage) -> Void)?

    override init() {
        super.init()
        checkAuthorization()
    }

    /// Check camera authorization
    func checkAuthorization() {
        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized:
            authorizationStatus = .authorized
            setupCaptureSession()

        case .notDetermined:
            AVCaptureDevice.requestAccess(for: .video) { [weak self] granted in
                DispatchQueue.main.async {
                    self?.authorizationStatus = granted ? .authorized : .denied
                    if granted {
                        self?.setupCaptureSession()
                    }
                }
            }

        case .denied, .restricted:
            authorizationStatus = .denied

        @unknown default:
            authorizationStatus = .denied
        }
    }

    /// Setup capture session
    private func setupCaptureSession() {
        sessionQueue.async { [weak self] in
            guard let self = self else { return }

            self.captureSession.beginConfiguration()

            // Set session preset
            if self.captureSession.canSetSessionPreset(.medium) {
                self.captureSession.sessionPreset = .medium
            }

            // Add camera input
            guard let camera = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
                  let input = try? AVCaptureDeviceInput(device: camera),
                  self.captureSession.canAddInput(input) else {
                print("Failed to add camera input")
                self.captureSession.commitConfiguration()
                return
            }

            self.captureSession.addInput(input)

            // Configure video output
            self.videoOutput.setSampleBufferDelegate(self, queue: DispatchQueue(label: "camera.frame.queue"))
            self.videoOutput.videoSettings = [
                kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA
            ]

            if self.captureSession.canAddOutput(self.videoOutput) {
                self.captureSession.addOutput(self.videoOutput)
            }

            // Set video orientation
            if let connection = self.videoOutput.connection(with: .video) {
                connection.videoOrientation = .portrait
            }

            self.captureSession.commitConfiguration()
        }
    }

    /// Start capture session
    func startSession() {
        guard authorizationStatus == .authorized else {
            print("Camera not authorized")
            return
        }

        sessionQueue.async { [weak self] in
            guard let self = self else { return }

            if !self.captureSession.isRunning {
                self.captureSession.startRunning()

                DispatchQueue.main.async {
                    self.isSessionRunning = true
                }
            }
        }
    }

    /// Stop capture session
    func stopSession() {
        sessionQueue.async { [weak self] in
            guard let self = self else { return }

            if self.captureSession.isRunning {
                self.captureSession.stopRunning()

                DispatchQueue.main.async {
                    self.isSessionRunning = false
                }
            }
        }
    }

    /// Get preview layer
    func getPreviewLayer() -> AVCaptureVideoPreviewLayer {
        let previewLayer = AVCaptureVideoPreviewLayer(session: captureSession)
        previewLayer.videoGravity = .resizeAspectFill
        return previewLayer
    }
}

// MARK: - AVCaptureVideoDataOutputSampleBufferDelegate
extension CameraManager: AVCaptureVideoDataOutputSampleBufferDelegate {
    func captureOutput(_ output: AVCaptureOutput,
                      didOutput sampleBuffer: CMSampleBuffer,
                      from connection: AVCaptureConnection) {
        guard let imageBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }

        // Convert to UIImage
        let ciImage = CIImage(cvPixelBuffer: imageBuffer)
        let context = CIContext()

        guard let cgImage = context.createCGImage(ciImage, from: ciImage.extent) else { return }

        let image = UIImage(cgImage: cgImage)

        DispatchQueue.main.async { [weak self] in
            self?.currentFrame = image
            self?.onFrameCaptured?(image)
        }
    }
}
