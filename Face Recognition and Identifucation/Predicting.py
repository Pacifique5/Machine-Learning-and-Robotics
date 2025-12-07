import cv2
import mediapipe as mp
import json

# Load model
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("models/lbph_model.xml")

# Load label map
with open("models/label_map.json", "r") as f:
    label_map = json.load(f)

mp_face = mp.solutions.face_mesh

cap = cv2.VideoCapture(0)

with mp_face.FaceMesh(
        max_num_faces=2,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
) as fm:

    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = fm.process(rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                xs = [int(lm.x * w) for lm in face_landmarks.landmark]
                ys = [int(lm.y * h) for lm in face_landmarks.landmark]
                x_min, x_max = min(xs), max(xs)
                y_min, y_max = min(ys), max(ys)

                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max),
                              (0, 255, 0), 2)

                # Prepare face for prediction
                if x_max > x_min and y_max > y_min:
                    face_crop = frame[y_min:y_max, x_min:x_max]
                    if face_crop.size > 0:
                        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)

                        try:
                            label_id, confidence = recognizer.predict(gray)
                            name = label_map[str(label_id)]

                            text = f"{name} ({int(confidence)})"
                        except:
                            text = "Unknown"
                    else:
                        text = "Unknown"
                else:
                    text = "Unknown"

                cv2.putText(frame, text, (x_min, y_min - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                            (0, 255, 0), 2)

        cv2.imshow("Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
