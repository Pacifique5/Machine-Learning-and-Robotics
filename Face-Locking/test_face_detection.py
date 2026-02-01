#!/usr/bin/env python3
"""
Simple face detection test to debug the enrollment issue
"""

import cv2
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path.cwd()))

from src.haar_5pt import Haar5ptDetector

def test_face_detection():
    """Test face detection with camera"""
    
    print("🔍 Testing Face Detection")
    print("=" * 40)
    
    # Initialize detector
    try:
        detector = Haar5ptDetector(min_size=(70, 70), smooth_alpha=0.80, debug=True)
        print("✅ Face detector initialized")
    except Exception as e:
        print(f"❌ Failed to initialize detector: {e}")
        return
    
    # Test camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Failed to open camera")
        return
    
    print("✅ Camera opened successfully")
    print("\n📷 Camera Test:")
    print("- Position your face in front of the camera")
    print("- Press SPACE to test detection")
    print("- Press 'q' to quit")
    
    detection_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame")
            break
        
        # Test detection
        faces = detector.detect(frame, max_faces=1)
        
        # Draw results
        vis = frame.copy()
        
        if faces:
            detection_count += 1
            face = faces[0]
            
            # Draw bounding box
            cv2.rectangle(vis, (face.x1, face.y1), (face.x2, face.y2), (0, 255, 0), 2)
            
            # Draw landmarks
            for (x, y) in face.kps.astype(int):
                cv2.circle(vis, (int(x), int(y)), 3, (0, 255, 0), -1)
            
            # Status text
            cv2.putText(vis, f"FACE DETECTED #{detection_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(vis, f"Score: {face.score:.2f}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(vis, f"Size: {face.x2-face.x1}x{face.y2-face.y1}", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            cv2.putText(vis, "NO FACE DETECTED", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(vis, "Move closer or improve lighting", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # Instructions
        cv2.putText(vis, "SPACE=test detection, q=quit", (10, vis.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow("Face Detection Test", vis)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):  # SPACE
            if faces:
                print(f"✅ Detection successful! Face at ({face.x1},{face.y1}) to ({face.x2},{face.y2})")
                print(f"   Landmarks: {face.kps.shape}")
            else:
                print("❌ No face detected. Try:")
                print("   - Move closer to camera")
                print("   - Improve lighting")
                print("   - Face the camera directly")
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\n📊 Test Results:")
    print(f"Total detections: {detection_count}")
    
    if detection_count > 0:
        print("✅ Face detection is working!")
        print("The enrollment issue might be elsewhere.")
    else:
        print("❌ Face detection failed!")
        print("Possible issues:")
        print("- Camera not working properly")
        print("- Poor lighting conditions")
        print("- Face too small or far away")
        print("- MediaPipe fallback not working")

if __name__ == "__main__":
    test_face_detection()