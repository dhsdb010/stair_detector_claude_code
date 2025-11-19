//
//  CameraPreviewView.swift
//  StairDetector
//
//  SwiftUI wrapper for camera preview
//

import SwiftUI
import AVFoundation

struct CameraPreviewView: UIViewRepresentable {
    let cameraManager: CameraManager

    func makeUIView(context: Context) -> CameraPreviewUIView {
        let view = CameraPreviewUIView()
        view.previewLayer = cameraManager.getPreviewLayer()
        return view
    }

    func updateUIView(_ uiView: CameraPreviewUIView, context: Context) {
        // Update if needed
    }
}

class CameraPreviewUIView: UIView {
    var previewLayer: AVCaptureVideoPreviewLayer? {
        didSet {
            if let previewLayer = previewLayer {
                layer.addSublayer(previewLayer)
            }
        }
    }

    override func layoutSubviews() {
        super.layoutSubviews()
        previewLayer?.frame = bounds
    }
}
