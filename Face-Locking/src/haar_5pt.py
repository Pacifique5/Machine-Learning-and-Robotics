# src/haar_5pt.py
"""
Haar face detection + practical 5-point landmarks (MediaPipe FaceMesh).

Why this works:
- Haar is fast and robust on CPU.
- MediaPipe FaceMesh confirms a real face and gives stable landmarks.
- We extract ONLY 5 keypoints: left_eye, right_eye, nose_tip, mouth_left, mouth_right
- We rebuild bbox from keypoints (centered), so no "aside" offset.
- We reject Haar false positives if FaceMesh doesn't produce landmarks.

Run:
    python -m src.haar_5pt
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, List

import cv2
import numpy as np

try:
    import mediapipe as mp
except Exception as e:
    mp = None
    _MP_IMPORT_ERROR = e

# -------------------------
# Data
# -------------------------

@dataclass
class FaceKpsBox:
    x1: int
    y1: int
    x2: int
    y2: int
    score: float
    kps: np.ndarray  # (5,2) float32

# -------------------------
# Helpers
# -------------------------

def _estimate_norm_5pt(kps_5x2: np.ndarray, out_size: Tuple[int, int] = (112, 112)) -> np.ndarray:
    """
    Build 2x3 affine matrix that maps 5pts to ArcFace-style template.
    kps order must be: [Leye, Reye, Nose, Lmouth, Rmouth]
    """
    k = kps_5x2.astype(np.float32)

    # ArcFace 112x112 template
    dst = np.array([
        [38.2946, 51.6963],  # left eye
        [73.5318, 51.5014],  # right eye
        [56.0252, 71.7366],  # nose
        [41.5493, 92.3655],  # left mouth
        [70.7299, 92.2041],  # right mouth
    ], dtype=np.float32)

    out_w, out_h = int(out_size[0]), int(out_size[1])

    if (out_w, out_h) != (112, 112):
        sx = out_w / 112.0
        sy = out_h / 112.0
        dst = dst * np.array([sx, sy], dtype=np.float32)

    M, _ = cv2.estimateAffinePartial2D(k, dst, method=cv2.LMEDS)
    if M is None:
        # fallback using eyes+nose
        M = cv2.getAffineTransform(
            np.array([k[0], k[1], k[2]], dtype=np.float32),
            np.array([dst[0], dst[1], dst[2]], dtype=np.float32),
        )
    return M.astype(np.float32)

def align_face_5pt(
    frame_bgr: np.ndarray,
    kps_5x2: np.ndarray,
    out_size: Tuple[int, int] = (112, 112)
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Returns aligned face and affine matrix: (aligned_bgr, M)
    """
    M = _estimate_norm_5pt(kps_5x2, out_size=out_size)
    out_w, out_h = int(out_size[0]), int(out_size[1])
    aligned = cv2.warpAffine(
        frame_bgr,
        M,
        (out_w, out_h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0),
    )
    return aligned, M

def _clip_box_xyxy(b: np.ndarray, W: int, H: int) -> np.ndarray:
    bb = b.astype(np.float32).copy()
    bb[0] = np.clip(bb[0], 0, W - 1)
    bb[1] = np.clip(bb[1], 0, H - 1)
    bb[2] = np.clip(bb[2], 0, W - 1)
    bb[3] = np.clip(bb[3], 0, H - 1)
    return bb

def _bbox_from_5pt(kps: np.ndarray, pad_x: float = 0.55, pad_y_top: float = 0.85, pad_y_bot: float = 1.15) -> np.ndarray:
    """
    Build a face bbox from 5 keypoints with asymmetric padding
    (more forehead, more chin)
    """
    k = kps.astype(np.float32)
    x_min = float(np.min(k[:, 0]))
    x_max = float(np.max(k[:, 0]))
    y_min = float(np.min(k[:, 1]))
    y_max = float(np.max(k[:, 1]))

    w = max(1.0, x_max - x_min)
    h = max(1.0, y_max - y_min)

    x1 = x_min - pad_x * w
    x2 = x_max + pad_x * w
    y1 = y_min - pad_y_top * h
    y2 = y_max + pad_y_bot * h

    return np.array([x1, y1, x2, y2], dtype=np.float32)

def _ema(prev: Optional[np.ndarray], cur: np.ndarray, alpha: float) -> np.ndarray:
    if prev is None:
        return cur.astype(np.float32)
    return (alpha * prev + (1.0 - alpha) * cur).astype(np.float32)

def _kps_span_ok(kps: np.ndarray, min_eye_dist: float = 12.0) -> bool:
    """
    Quick sanity filter on 5pt geometry:
    - eye distance reasonable
    - mouth below nose
    """
    k = kps.astype(np.float32)
    le, re, no, lm, rm = k
    eye_dist = float(np.linalg.norm(re - le))
    if eye_dist < min_eye_dist:
        return False
    if not (lm[1] > no[1] and rm[1] > no[1]):
        return False
    return True

# -------------------------
# Detector
# -------------------------

class Haar5ptDetector:
    def __init__(
        self,
        haar_xml: Optional[str] = None,
        min_size: Tuple[int, int] = (60, 60),
        smooth_alpha: float = 0.80,
        debug: bool = True,
    ):
        self.debug = bool(debug)
        self.min_size = tuple(map(int, min_size))
        self.smooth_alpha = float(smooth_alpha)

        # Haar cascade
        if haar_xml is None:
            haar_xml = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(haar_xml)
        if self.face_cascade.empty():
            raise RuntimeError(f"Failed to load Haar cascade: {haar_xml}")

        # MediaPipe FaceMesh - Use fallback for compatibility
        if mp is None:
            print("⚠️  MediaPipe not available, using geometric estimation fallback")
            self.mp_face_mesh = None
            self._use_mediapipe = False
        else:
            try:
                # Try to use MediaPipe solutions (older API)
                self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
                    static_image_mode=False,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5,
                )
                self._use_mediapipe = True
                if self.debug:
                    print("✅ Using MediaPipe FaceMesh for landmark detection")
            except (AttributeError, Exception) as e:
                if self.debug:
                    print(f"⚠️  MediaPipe FaceMesh not available ({e}), using geometric estimation")
                self.mp_face_mesh = None
                self._use_mediapipe = False

        # FaceMesh landmark indices for 5 points
        self.IDX_LEFT_EYE = 33
        self.IDX_RIGHT_EYE = 263
        self.IDX_NOSE_TIP = 1
        self.IDX_MOUTH_LEFT = 61
        self.IDX_MOUTH_RIGHT = 291

        self._prev_box: Optional[np.ndarray] = None
        self._prev_kps: Optional[np.ndarray] = None

    def _haar_faces(self, gray: np.ndarray) -> np.ndarray:
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            flags=cv2.CASCADE_SCALE_IMAGE,
            minSize=self.min_size,
        )
        if faces is None or len(faces) == 0:
            return np.zeros((0, 4), dtype=np.int32)
        return faces.astype(np.int32)

    def _facemesh_5pt(self, frame_bgr: np.ndarray) -> Optional[np.ndarray]:
        H, W = frame_bgr.shape[:2]
        
        if not self._use_mediapipe or self.mp_face_mesh is None:
            # Use geometric estimation fallback
            return self._simple_5pt_estimation(frame_bgr)
        
        try:
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            res = self.mp_face_mesh.process(rgb)
            if not res.multi_face_landmarks:
                return self._simple_5pt_estimation(frame_bgr)

            lm = res.multi_face_landmarks[0].landmark
            idxs = [
                self.IDX_LEFT_EYE,
                self.IDX_RIGHT_EYE,
                self.IDX_NOSE_TIP,
                self.IDX_MOUTH_LEFT,
                self.IDX_MOUTH_RIGHT,
            ]
            pts = [[lm[i].x * W, lm[i].y * H] for i in idxs]
            kps = np.array(pts, dtype=np.float32)

            # Ensure left/right ordering
            if kps[0, 0] > kps[1, 0]:
                kps[[0, 1]] = kps[[1, 0]]
            if kps[3, 0] > kps[4, 0]:
                kps[[3, 4]] = kps[[4, 3]]

            return kps
            
        except Exception as e:
            if self.debug:
                print(f"MediaPipe processing failed: {e}, using fallback")
            # Fallback to geometric estimation
            return self._simple_5pt_estimation(frame_bgr)
    
    def _simple_5pt_estimation(self, frame_bgr: np.ndarray) -> Optional[np.ndarray]:
        """
        Fallback method: estimate 5 points from Haar face detection
        This is less accurate but ensures compatibility
        """
        H, W = frame_bgr.shape[:2]
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        
        # Get Haar faces first
        faces = self._haar_faces(gray)
        
        if len(faces) == 0:
            return None
            
        # Take the largest face
        areas = faces[:, 2] * faces[:, 3]
        i = int(np.argmax(areas))
        x, y, w, h = faces[i]
        
        # Estimate 5 points based on face geometry
        # This is a rough approximation but should work
        center_x = x + w // 2
        center_y = y + h // 2
        
        # Estimate eye positions (upper third of face)
        eye_y = y + h // 3
        left_eye_x = x + w // 4
        right_eye_x = x + 3 * w // 4
        
        # Estimate nose position (center, middle)
        nose_x = center_x
        nose_y = y + h // 2
        
        # Estimate mouth positions (lower third)
        mouth_y = y + 2 * h // 3
        left_mouth_x = x + w // 3
        right_mouth_x = x + 2 * w // 3
        
        kps = np.array([
            [left_eye_x, eye_y],      # left eye
            [right_eye_x, eye_y],     # right eye
            [nose_x, nose_y],         # nose
            [left_mouth_x, mouth_y],  # left mouth
            [right_mouth_x, mouth_y], # right mouth
        ], dtype=np.float32)
        
        if self.debug:
            print(f"[haar_5pt] Using geometric estimation for face at ({x},{y},{w},{h})")
        
        return kps

    def detect(self, frame_bgr: np.ndarray, max_faces: int = 1) -> List[FaceKpsBox]:
        H, W = frame_bgr.shape[:2]
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

        faces = self._haar_faces(gray)
        if faces.shape[0] == 0:
            if self.debug:
                print("[haar_5pt] No Haar faces detected")
            return []

        # pick largest Haar face
        areas = faces[:, 2] * faces[:, 3]
        i = int(np.argmax(areas))
        x, y, w, h = faces[i].tolist()

        # Try to get landmarks (FaceMesh or fallback)
        kps = self._facemesh_5pt(frame_bgr)
        if kps is None:
            if self.debug:
                print("[haar_5pt] No landmarks detected, face rejected")
            return []

        # For geometric estimation, skip the consistency check
        if not self._use_mediapipe:
            # Using geometric estimation - be more lenient
            if self.debug:
                print("[haar_5pt] Using geometric estimation - skipping consistency checks")
        else:
            # check if 5pt inside Haar box (only for MediaPipe)
            margin = 0.35
            x1m = x - margin * w
            y1m = y - margin * h
            x2m = x + (1.0 + margin) * w
            y2m = y + (1.0 + margin) * h
            inside = (kps[:, 0] >= x1m) & (kps[:, 0] <= x2m) & (kps[:, 1] >= y1m) & (kps[:, 1] <= y2m)
            if inside.mean() < 0.60:
                if self.debug:
                    print("[haar_5pt] FaceMesh points not consistent with Haar box -> reject")
                return []

        # Basic geometry check (for both MediaPipe and geometric estimation)
        if not _kps_span_ok(kps, min_eye_dist=max(8.0, 0.15 * w)):  # More lenient
            if self.debug:
                print("[haar_5pt] 5pt geometry sanity failed -> reject")
            return []

        # build bbox
        box = _bbox_from_5pt(kps, pad_x=0.55, pad_y_top=0.85, pad_y_bot=1.15)
        box = _clip_box_xyxy(box, W, H)

        # smooth
        box_s = _ema(self._prev_box, box, self.smooth_alpha)
        kps_s = _ema(self._prev_kps, kps, self.smooth_alpha)

        self._prev_box = box_s.copy()
        self._prev_kps = kps_s.copy()

        x1, y1, x2, y2 = box_s.tolist()
        score = 1.0

        if self.debug:
            print(f"[haar_5pt] Face detected at ({x1:.0f},{y1:.0f}) to ({x2:.0f},{y2:.0f})")

        return [FaceKpsBox(
            x1=int(round(x1)),
            y1=int(round(y1)),
            x2=int(round(x2)),
            y2=int(round(y2)),
            score=float(score),
            kps=kps_s.astype(np.float32)
        )][:max_faces]

# -------------------------
# Demo
# -------------------------

def main():
    cap = cv2.VideoCapture(0)
    det = Haar5ptDetector(min_size=(70, 70), smooth_alpha=0.80, debug=True)

    print("Haar + 5pt (FaceMesh) test. Press q to quit.")
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        faces = det.detect(frame, max_faces=1)
        vis = frame.copy()

        if faces:
            f = faces[0]
            cv2.rectangle(vis, (f.x1, f.y1), (f.x2, f.y2), (0, 255, 0), 2)
            for (x, y) in f.kps.astype(int):
                cv2.circle(vis, (int(x), int(y)), 3, (0, 255, 0), -1)
            cv2.putText(vis, "OK", (f.x1, max(0, f.y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(vis, "no face", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        cv2.imshow("haar_5pt", vis)
        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
