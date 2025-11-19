//
//  StairDetector.swift
//  StairDetector
//
//  Detects stairs using Vision framework and image processing
//

import Foundation
import UIKit
import Vision

class StairDetector: ObservableObject {
    @Published var isStairsDetected: Bool = false
    @Published var confidence: Double = 0.0

    private var sensitivity: Double
    private var minLinesForDetection: Int
    private var detectionHistory: [Bool] = []
    private let maxHistory = 5

    init(sensitivity: Double = 0.7) {
        self.sensitivity = sensitivity
        self.minLinesForDetection = max(3, Int(10 * sensitivity))
    }

    /// Detect stairs in the given image
    func detectStairs(in image: UIImage) {
        guard let cgImage = image.cgImage else { return }

        // Create Vision request for rectangle detection
        let request = VNDetectRectanglesRequest { [weak self] request, error in
            guard let self = self else { return }

            if let error = error {
                print("Vision error: \(error.localizedDescription)")
                return
            }

            self.processVisionResults(request.results)
        }

        // Configure request
        request.minimumAspectRatio = 0.3
        request.maximumAspectRatio = 1.0
        request.minimumSize = 0.2
        request.minimumConfidence = Float(sensitivity * 0.5)

        // Perform request
        let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])

        do {
            try handler.perform([request])
        } catch {
            print("Failed to perform Vision request: \(error)")
        }

        // Also perform edge-based detection
        detectStairsUsingEdges(in: image)
    }

    /// Process Vision framework results
    private func processVisionResults(_ results: [Any]?) {
        guard let rectangles = results as? [VNRectangleObservation] else { return }

        // Filter for horizontal rectangles (potential stair steps)
        let horizontalRects = rectangles.filter { rect in
            let width = rect.boundingBox.width
            let height = rect.boundingBox.height
            let aspectRatio = width / height

            // Stair steps are typically wider than tall
            return aspectRatio > 1.5 && rect.boundingBox.minY > 0.3
        }

        // Check for stair pattern
        let hasStairPattern = checkStairPattern(rectangles: horizontalRects)

        updateDetection(detected: hasStairPattern,
                       confidence: Double(horizontalRects.count) / 10.0)
    }

    /// Check if rectangles form a stair pattern
    private func checkStairPattern(rectangles: [VNRectangleObservation]) -> Bool {
        guard rectangles.count >= minLinesForDetection else { return false }

        // Sort by vertical position (bottom to top)
        let sortedRects = rectangles.sorted { $0.boundingBox.minY > $1.boundingBox.minY }

        // Check spacing consistency
        if sortedRects.count >= 2 {
            var spacings: [CGFloat] = []

            for i in 0..<(sortedRects.count - 1) {
                let spacing = sortedRects[i].boundingBox.minY - sortedRects[i + 1].boundingBox.minY
                spacings.append(spacing)
            }

            // Calculate coefficient of variation
            let mean = spacings.reduce(0, +) / CGFloat(spacings.count)
            let variance = spacings.map { pow($0 - mean, 2) }.reduce(0, +) / CGFloat(spacings.count)
            let stdDev = sqrt(variance)
            let cv = mean > 0 ? stdDev / mean : 1.0

            // Regular spacing indicates stairs
            return cv < 0.5
        }

        return sortedRects.count >= minLinesForDetection
    }

    /// Detect stairs using edge detection (complementary method)
    private func detectStairsUsingEdges(in image: UIImage) {
        guard let ciImage = CIImage(image: image) else { return }

        // Apply edge detection
        let context = CIContext()

        // Convert to grayscale
        guard let grayFilter = CIFilter(name: "CIPhotoEffectMono") else { return }
        grayFilter.setValue(ciImage, forKey: kCIInputImageKey)

        guard let grayImage = grayFilter.outputImage else { return }

        // Apply edge detection
        guard let edgeFilter = CIFilter(name: "CIEdges") else { return }
        edgeFilter.setValue(grayImage, forKey: kCIInputImageKey)
        edgeFilter.setValue(sensitivity * 2.0, forKey: kCIInputIntensityKey)

        guard let edgeImage = edgeFilter.outputImage else { return }

        // Convert to UIImage for line detection
        guard let cgImage = context.createCGImage(edgeImage, from: edgeImage.extent) else { return }

        // Perform Hough-like line detection
        detectLines(in: cgImage)
    }

    /// Detect horizontal lines in edge image
    private func detectLines(in cgImage: CGImage) {
        let width = cgImage.width
        let height = cgImage.height

        guard let context = CGContext(
            data: nil,
            width: width,
            height: height,
            bitsPerComponent: 8,
            bytesPerRow: width,
            space: CGColorSpaceCreateDeviceGray(),
            bitmapInfo: CGImageAlphaInfo.none.rawValue
        ) else { return }

        context.draw(cgImage, in: CGRect(x: 0, y: 0, width: width, height: height))

        guard let pixelData = context.data else { return }
        let data = pixelData.bindMemory(to: UInt8.self, capacity: width * height)

        // Scan horizontal lines
        var horizontalLineCount = 0
        let threshold: UInt8 = 128
        let minLineLength = Int(Double(width) * 0.3)

        // Only scan lower 2/3 of image
        let startY = height / 3
        let scanInterval = 5 // Scan every 5 rows

        for y in stride(from: startY, to: height, by: scanInterval) {
            var lineLength = 0

            for x in 0..<width {
                let index = y * width + x
                if data[index] > threshold {
                    lineLength += 1
                } else {
                    if lineLength >= minLineLength {
                        horizontalLineCount += 1
                        break
                    }
                    lineLength = 0
                }
            }
        }

        let detected = horizontalLineCount >= minLinesForDetection
        let conf = min(1.0, Double(horizontalLineCount) / 15.0)

        updateDetection(detected: detected, confidence: conf)
    }

    /// Update detection state with temporal filtering
    private func updateDetection(detected: Bool, confidence: Double) {
        // Update history
        detectionHistory.append(detected)
        if detectionHistory.count > maxHistory {
            detectionHistory.removeFirst()
        }

        // Temporal filter - require majority agreement
        let detectionCount = detectionHistory.filter { $0 }.count
        let finalDetection = detectionCount >= (detectionHistory.count / 2)

        DispatchQueue.main.async {
            self.isStairsDetected = finalDetection
            self.confidence = confidence
        }
    }

    /// Reset detection history
    func reset() {
        detectionHistory.removeAll()
        isStairsDetected = false
        confidence = 0.0
    }
}
