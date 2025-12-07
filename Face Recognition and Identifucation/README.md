Face Recognition Pipeline (MediaPipe + LBPH)

This project implements a complete classical face-recognition pipeline using:

MediaPipe Face Mesh – for fast and accurate face detection

OpenCV LBPH – for feature-based face recognition (no machine learning models)

This satisfies the “AI Without ML” assignment requirement.

📂 Project Structure
project/
│── capture.py
│── train.py
│── predict.py
│
│── dataset/                # Captured face images
│
│── models/
│    ├── lbph_model.xml     # Trained LBPH model
│    └── label_map.json     # ID → Name mapping
│
└── README.md

🚀 1. Capture Face Images

Run:

python capture.py


The program will ask:

Enter your name:


Then look at the camera.
Press Q to stop capturing.

Images will be saved in:

dataset/<your_name>/

🚀 2. Train the LBPH Model

Run:

python train.py


This will generate:

models/lbph_model.xml
models/label_map.json

🚀 3. Run Face Recognition

Run:

python predict.py


The camera window will display:

A green rectangle around the detected face

The predicted name

The LBPH confidence score

Press Q to quit.

📦 Requirements

Install dependencies:

pip install opencv-python mediapipe
pip install opencv-contrib-python   # Required for LBPH

🎉 You're Done!

This pipeline supports any number of people.
Just follow the cycle:

Capture → Train → Predict
