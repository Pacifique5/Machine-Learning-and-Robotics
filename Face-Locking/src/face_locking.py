# src/face_locking.py
"""
Face Locking System

This module implements face locking functionality that:
1. Locks onto a specific enrolled identity
2. Tracks the face consistently across frames
3. Detects face actions (movement, blink, smile)
4. Records action history to files

Usage: python -m src.face_locking
"""

from __future__ import annotations
import time
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

import cv2
import numpy as np

from .haar_5pt import align_face_5pt
from .recognize import (
    HaarFaceMesh5pt, ArcFaceEmbedderONNX, FaceDBMatcher, 
    load_db_npz, FaceDet, MatchResult, cosine_distance
)

# -------------------------
# Configuration
# -------------------------

@dataclass
class FaceLockConfig:
    # Face locking parameters
    lock_confidence_threshold: float = 0.66  # similarity threshold to lock
    lock_timeout_seconds: float = 3.0        # release lock after this time without detection
    tracking_tolerance: float = 0.45         # lower threshold while tracking
    
    # Action detection parameters
    movement_threshold: float = 30.0         # pixels for left/right movement
    blink_threshold: float = 0.25           # eye aspect ratio threshold
    smile_threshold: float = 0.02           # mouth curve threshold
    
    # History recording
    history_dir: Path = Path("data/history")
    
    # UI
    window_name: str = "Face Locking System"

# -------------------------
# Action Detection Classes
# -------------------------

@dataclass
class FaceAction:
    timestamp: float
    action_type: str
    description: str
    value: Optional[float] = None

class ActionDetector:
    """Detects face actions like movement, blink, smile"""
    
    def __init__(self, config: FaceLockConfig):
        self.config = config
        self.prev_center: Optional[Tuple[float, float]] = None
        self.prev_eye_ratio: Optional[float] = None
        self.prev_mouth_curve: Optional[float] = None
        self.blink_state = False
        
    def reset(self):
        """Reset detector state"""
        self.prev_center = None
        self.prev_eye_ratio = None
        self.prev_mouth_curve = None
        self.blink_state = False
    
    def detect_actions(self, face: FaceDet) -> List[FaceAction]:
        """Detect actions from face landmarks"""
        actions = []
        timestamp = time.time()
        
        # Calculate face center
        center_x = (face.x1 + face.x2) / 2
        center_y = (face.y1 + face.y2) / 2
        current_center = (center_x, center_y)
        
        # Detect movement
        if self.prev_center is not None:
            dx = center_x - self.prev_center[0]
            dy = center_y - self.prev_center[1]
            
            if abs(dx) > self.config.movement_threshold:
                direction = "right" if dx > 0 else "left"
                actions.append(FaceAction(
                    timestamp=timestamp,
                    action_type="movement",
                    description=f"face moved {direction}",
                    value=abs(dx)
                ))
        
        # Detect blink using eye aspect ratio
        eye_ratio = self._calculate_eye_aspect_ratio(face.kps)
        if eye_ratio is not None:
            if self.prev_eye_ratio is not None:
                # Detect blink (eye closing then opening)
                if not self.blink_state and eye_ratio < self.config.blink_threshold:
                    self.blink_state = True
                elif self.blink_state and eye_ratio > self.config.blink_threshold * 1.5:
                    self.blink_state = False
                    actions.append(FaceAction(
                        timestamp=timestamp,
                        action_type="blink",
                        description="eye blink detected",
                        value=eye_ratio
                    ))
            self.prev_eye_ratio = eye_ratio
        
        # Detect smile using mouth curvature
        mouth_curve = self._calculate_mouth_curve(face.kps)
        if mouth_curve is not None:
            if self.prev_mouth_curve is not None:
                curve_change = mouth_curve - self.prev_mouth_curve
                if curve_change > self.config.smile_threshold:
                    actions.append(FaceAction(
                        timestamp=timestamp,
                        action_type="smile",
                        description="smile or laugh detected",
                        value=mouth_curve
                    ))
            self.prev_mouth_curve = mouth_curve
        
        self.prev_center = current_center
        return actions
    
    def _calculate_eye_aspect_ratio(self, kps: np.ndarray) -> Optional[float]:
        """Calculate eye aspect ratio for blink detection"""
        try:
            # Using 5-point landmarks: left_eye, right_eye, nose, left_mouth, right_mouth
            left_eye = kps[0]   # left eye
            right_eye = kps[1]  # right eye
            
            # Simple eye aspect ratio approximation
            eye_distance = np.linalg.norm(right_eye - left_eye)
            if eye_distance > 0:
                # Estimate vertical eye opening based on distance from nose
                nose = kps[2]
                left_eye_to_nose = np.linalg.norm(left_eye - nose)
                right_eye_to_nose = np.linalg.norm(right_eye - nose)
                avg_eye_to_nose = (left_eye_to_nose + right_eye_to_nose) / 2
                
                # Eye aspect ratio approximation
                ratio = avg_eye_to_nose / eye_distance
                return float(ratio)
        except Exception:
            pass
        return None
    
    def _calculate_mouth_curve(self, kps: np.ndarray) -> Optional[float]:
        """Calculate mouth curvature for smile detection"""
        try:
            # Using 5-point landmarks
            left_mouth = kps[3]   # left mouth corner
            right_mouth = kps[4]  # right mouth corner
            nose = kps[2]         # nose tip
            
            # Calculate mouth center
            mouth_center = (left_mouth + right_mouth) / 2
            
            # Calculate curvature based on mouth corners relative to center
            mouth_width = np.linalg.norm(right_mouth - left_mouth)
            nose_to_mouth = np.linalg.norm(mouth_center - nose)
            
            if mouth_width > 0:
                # Simple curvature approximation
                curvature = nose_to_mouth / mouth_width
                return float(curvature)
        except Exception:
            pass
        return None

# -------------------------
# Face Locking System
# -------------------------

class FaceLockingSystem:
    """Main face locking system"""
    
    def __init__(self, config: FaceLockConfig, target_identity: str):
        self.config = config
        self.target_identity = target_identity
        
        # Initialize components
        self.detector = HaarFaceMesh5pt(min_size=(70, 70), debug=False)
        self.embedder = ArcFaceEmbedderONNX(
            model_path="models/embedder_arcface.onnx", 
            input_size=(112, 112)
        )
        
        # Load face database
        db = load_db_npz(Path("data/db/face_db.npz"))
        self.matcher = FaceDBMatcher(db=db, dist_thresh=0.34)
        
        # Action detection
        self.action_detector = ActionDetector(config)
        
        # Locking state
        self.is_locked = False
        self.locked_face: Optional[FaceDet] = None
        self.last_detection_time: Optional[float] = None
        self.lock_start_time: Optional[float] = None
        
        # History recording
        self.action_history: List[FaceAction] = []
        self.history_file: Optional[Path] = None
        
        # Ensure history directory exists
        self.config.history_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Face Locking System initialized for target: '{target_identity}'")
        print(f"Available identities: {list(self.matcher.db.keys())}")
    
    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process a single frame and return annotated frame"""
        vis_frame = frame.copy()
        
        # Detect all faces
        faces = self.detector.detect(frame, max_faces=5)
        
        if self.is_locked:
            # If locked, try to maintain lock
            self._update_locked_face(faces, frame)
        else:
            # If not locked, try to find target identity
            self._try_lock_target(faces, frame)
        
        # Draw visualization
        self._draw_visualization(vis_frame, faces)
        
        return vis_frame
    
    def _try_lock_target(self, faces: List[FaceDet], frame: np.ndarray):
        """Try to lock onto target identity"""
        for face in faces:
            # Get face embedding
            aligned, _ = align_face_5pt(frame, face.kps, out_size=(112, 112))
            embedding = self.embedder.embed(aligned)
            match_result = self.matcher.match(embedding)
            
            # Check if this is our target with high confidence
            if (match_result.name == self.target_identity and 
                match_result.similarity >= self.config.lock_confidence_threshold):
                
                # Lock onto this face
                self.is_locked = True
                self.locked_face = face
                self.last_detection_time = time.time()
                self.lock_start_time = time.time()
                
                # Reset action detector
                self.action_detector.reset()
                
                # Start new history file
                self._start_new_history_file()
                
                print(f"🔒 LOCKED onto {self.target_identity} (similarity: {match_result.similarity:.3f})")
                break
    
    def _update_locked_face(self, faces: List[FaceDet], frame: np.ndarray):
        """Update locked face tracking"""
        current_time = time.time()
        best_match: Optional[Tuple[FaceDet, float]] = None
        
        # Find best matching face for our locked target
        for face in faces:
            aligned, _ = align_face_5pt(frame, face.kps, out_size=(112, 112))
            embedding = self.embedder.embed(aligned)
            match_result = self.matcher.match(embedding)
            
            # Use lower threshold while tracking
            if (match_result.name == self.target_identity and 
                match_result.similarity >= self.config.tracking_tolerance):
                
                if best_match is None or match_result.similarity > best_match[1]:
                    best_match = (face, match_result.similarity)
        
        if best_match is not None:
            # Update locked face
            face, similarity = best_match
            self.locked_face = face
            self.last_detection_time = current_time
            
            # Detect actions
            actions = self.action_detector.detect_actions(face)
            for action in actions:
                self._record_action(action)
                print(f"📝 Action: {action.description}")
        
        else:
            # Check if we should release the lock
            if (self.last_detection_time is not None and 
                current_time - self.last_detection_time > self.config.lock_timeout_seconds):
                
                self._release_lock()
    
    def _release_lock(self):
        """Release the face lock"""
        if self.is_locked:
            lock_duration = time.time() - self.lock_start_time if self.lock_start_time else 0
            print(f"🔓 RELEASED lock on {self.target_identity} (duration: {lock_duration:.1f}s)")
            
            self.is_locked = False
            self.locked_face = None
            self.last_detection_time = None
            self.lock_start_time = None
            
            # Finalize history file
            self._finalize_history_file()
    
    def _start_new_history_file(self):
        """Start a new history recording file"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{self.target_identity.lower()}_history_{timestamp}.txt"
        self.history_file = self.config.history_dir / filename
        
        # Write header
        with open(self.history_file, 'w') as f:
            f.write(f"Face Locking History for: {self.target_identity}\n")
            f.write(f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n")
            f.write("Timestamp\t\tAction Type\tDescription\t\tValue\n")
            f.write("-" * 70 + "\n")
        
        self.action_history.clear()
        print(f"📁 Started history file: {filename}")
    
    def _record_action(self, action: FaceAction):
        """Record an action to history"""
        self.action_history.append(action)
        
        if self.history_file:
            timestamp_str = datetime.fromtimestamp(action.timestamp).strftime('%H:%M:%S.%f')[:-3]
            value_str = f"{action.value:.3f}" if action.value is not None else "N/A"
            
            with open(self.history_file, 'a') as f:
                f.write(f"{timestamp_str}\t{action.action_type}\t\t{action.description}\t{value_str}\n")
    
    def _finalize_history_file(self):
        """Finalize the history file"""
        if self.history_file and self.action_history:
            with open(self.history_file, 'a') as f:
                f.write("-" * 70 + "\n")
                f.write(f"Session ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total actions recorded: {len(self.action_history)}\n")
                
                # Action summary
                action_counts = {}
                for action in self.action_history:
                    action_counts[action.action_type] = action_counts.get(action.action_type, 0) + 1
                
                f.write("Action Summary:\n")
                for action_type, count in action_counts.items():
                    f.write(f"  {action_type}: {count}\n")
    
    def _draw_visualization(self, frame: np.ndarray, faces: List[FaceDet]):
        """Draw visualization on frame"""
        h, w = frame.shape[:2]
        
        # Draw all detected faces
        for face in faces:
            color = (0, 255, 0)  # Green for regular faces
            thickness = 2
            
            # Highlight locked face
            if self.is_locked and self.locked_face is not None:
                if self._faces_similar(face, self.locked_face):
                    color = (0, 0, 255)  # Red for locked face
                    thickness = 4
            
            # Draw bounding box
            cv2.rectangle(frame, (face.x1, face.y1), (face.x2, face.y2), color, thickness)
            
            # Draw landmarks
            for (x, y) in face.kps.astype(int):
                cv2.circle(frame, (int(x), int(y)), 3, color, -1)
        
        # Draw status information
        status_lines = [
            f"Target: {self.target_identity}",
            f"Status: {'🔒 LOCKED' if self.is_locked else '🔍 SEARCHING'}",
        ]
        
        if self.is_locked and self.lock_start_time:
            duration = time.time() - self.lock_start_time
            status_lines.append(f"Lock Duration: {duration:.1f}s")
            status_lines.append(f"Actions Recorded: {len(self.action_history)}")
        
        # Draw status with background
        y_offset = 30
        for line in status_lines:
            # Black background for text
            (text_w, text_h), _ = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(frame, (10, y_offset - text_h - 5), (10 + text_w + 10, y_offset + 5), (0, 0, 0), -1)
            
            # White text
            cv2.putText(frame, line, (15, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            y_offset += 35
        
        # Draw controls
        controls = [
            "Controls:",
            "q - Quit",
            "r - Release lock",
            "t - Change target",
            "s - Show stats"
        ]
        
        y_offset = h - 150
        for line in controls:
            cv2.putText(frame, line, (15, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_offset += 25
    
    def _faces_similar(self, face1: FaceDet, face2: FaceDet, threshold: float = 50.0) -> bool:
        """Check if two faces are similar (for tracking)"""
        center1 = ((face1.x1 + face1.x2) / 2, (face1.y1 + face1.y2) / 2)
        center2 = ((face2.x1 + face2.x2) / 2, (face2.y1 + face2.y2) / 2)
        
        distance = math.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
        return distance < threshold

# -------------------------
# Main Application
# -------------------------

def main():
    """Main face locking application"""
    
    # Load available identities
    db_path = Path("data/db/face_db.npz")
    if not db_path.exists():
        print("❌ No face database found! Please run enrollment first.")
        print("Run: python -m src.enroll")
        return
    
    db = load_db_npz(db_path)
    available_identities = list(db.keys())
    
    if not available_identities:
        print("❌ No enrolled identities found! Please enroll faces first.")
        print("Run: python -m src.enroll")
        return
    
    print("🎯 Face Locking System")
    print("Available enrolled identities:")
    for i, name in enumerate(available_identities, 1):
        print(f"  {i}. {name}")
    
    # Select target identity
    while True:
        try:
            choice = input(f"\nSelect target identity (1-{len(available_identities)}) or enter name: ").strip()
            
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(available_identities):
                    target_identity = available_identities[idx]
                    break
            else:
                if choice in available_identities:
                    target_identity = choice
                    break
                else:
                    print(f"❌ '{choice}' not found in database.")
                    continue
            
            print("❌ Invalid selection. Please try again.")
        except (ValueError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            return
    
    print(f"\n🎯 Target selected: {target_identity}")
    
    # Initialize system
    config = FaceLockConfig()
    face_locker = FaceLockingSystem(config, target_identity)
    
    # Start camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Failed to open camera!")
        return
    
    print("\n🚀 Face Locking System started!")
    print("Position the target person in front of the camera...")
    print("The system will automatically lock when it recognizes them with high confidence.")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read from camera!")
                break
            
            # Process frame
            processed_frame = face_locker.process_frame(frame)
            
            # Display
            cv2.imshow(config.window_name, processed_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                if face_locker.is_locked:
                    face_locker._release_lock()
                    print("🔓 Manually released lock")
            elif key == ord('t'):
                print("\n🔄 Change target (restart required)")
                break
            elif key == ord('s'):
                print(f"\n📊 Stats:")
                print(f"  Target: {target_identity}")
                print(f"  Locked: {face_locker.is_locked}")
                print(f"  Actions recorded: {len(face_locker.action_history)}")
                if face_locker.history_file:
                    print(f"  History file: {face_locker.history_file.name}")
    
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
    
    finally:
        # Cleanup
        if face_locker.is_locked:
            face_locker._release_lock()
        
        cap.release()
        cv2.destroyAllWindows()
        print("👋 Face Locking System stopped")

if __name__ == "__main__":
    main()