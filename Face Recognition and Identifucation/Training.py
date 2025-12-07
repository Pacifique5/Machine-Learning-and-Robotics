import cv2
import os
import json
import numpy as np

# Paths
dataset_dir = "dataset"
model_path = "models/lbph_model.xml"
label_map_path = "models/label_map.json"

# Create models directory if it doesn't exist
os.makedirs("models", exist_ok=True)

# Prepare training data
faces = []
labels = []
label_map = {}
label_id = 0

for person_name in os.listdir(dataset_dir):
    person_dir = os.path.join(dataset_dir, person_name)
    if os.path.isdir(person_dir):
        label_map[label_id] = person_name
        for image_name in os.listdir(person_dir):
            image_path = os.path.join(person_dir, image_name)
            if image_path.endswith(('.jpg', '.jpeg', '.png')):
                img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    faces.append(img)
                    labels.append(label_id)
        label_id += 1

# Train LBPH recognizer
if faces:
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(labels))
    recognizer.save(model_path)

    # Save label map
    with open(label_map_path, "w") as f:
        json.dump(label_map, f)

    print(f"Trained model with {len(label_map)} people and {len(faces)} images.")
else:
    print("No faces found in dataset. Please capture some faces first.")
