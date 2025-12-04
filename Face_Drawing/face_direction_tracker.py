import cv2
import mediapipe as mp

# === CONFIGURATION ===
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
CENTER_TOLERANCE = 100    # pixels before movement

# === SETUP ===
cap = cv2.VideoCapture(0)
cap.set(3, FRAME_WIDTH)
cap.set(4, FRAME_HEIGHT)

mp_face_detection = mp.solutions.face_detection

print("Face tracking starting... Press 'q' to quit.")

with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_h, frame_w = frame.shape[:2]
        frame_center = frame_w // 2

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(image_rgb)

        message = "No face detected"
        command = "S"  # S = still/center

        if results.detections:
            # pick largest detection by bbox area
            best = max(
                results.detections,
                key=lambda d: d.location_data.relative_bounding_box.width * d.location_data.relative_bounding_box.height
            )
            bbox = best.location_data.relative_bounding_box
            x = int(bbox.xmin * frame_w)
            y = int(bbox.ymin * frame_h)
            w = int(bbox.width * frame_w)
            h = int(bbox.height * frame_h)

            # clamp
            x = max(0, x)
            y = max(0, y)
            w = min(frame_w - x, w)
            h = min(frame_h - y, h)

            cx = x + w // 2

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.line(frame, (frame_center, 0), (frame_center, frame_h), (255, 0, 0), 1)

            if cx < frame_center - CENTER_TOLERANCE:
                message = "Move left"
                command = "L"
            elif cx > frame_center + CENTER_TOLERANCE:
                message = "Move right"
                command = "R"
            else:
                message = "Centered"
                command = "S"

            cv2.putText(frame, f"Command: {message}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            # Note: Arduino/serial communication removed — command is available in `command` variable.

        cv2.imshow("Face tracking (MediaPipe)", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()