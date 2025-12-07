import cv2
import mediapipe as mp
import os

name = input("Enter your name: ").strip()

save_dir = f"dataset/{name}"
os.makedirs(save_dir, exist_ok=True)

mp_face = mp.solutions.face_mesh

cap = cv2.VideoCapture(0)
count = 0

with mp_face.FaceMesh(
        max_num_faces=1,
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

                # Draw rectangle
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max),
                              (0, 255, 0), 2)

                # Crop & save
                face_crop = frame[y_min:y_max, x_min:x_max]
                if face_crop.size > 0:
                    cv2.imwrite(f"{save_dir}/{count}.jpg", face_crop)
                    count += 1

        cv2.imshow("Capturing Faces", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

print(f"Saved {count} images to {save_dir}")
