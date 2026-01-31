from pathlib import Path

# Canonical project structure
structure = {
    "data/enroll": [],
    "data/db": [],
    "models": [
        "embedder_arcface.onnx",
    ],
    "src": [
        "camera.py",
        "detect.py",
        "landmarks.py",
        "align.py",
        "embed.py",
        "enroll.py",
        "recognize.py",
        "evaluate.py",
        "haar_5pt.py",
    ],
    "book": [],
}

# Create folders and files
for folder, files in structure.items():
    folder_path = Path(folder)
    folder_path.mkdir(parents=True, exist_ok=True)

    for file in files:
        file_path = folder_path / file
        file_path.touch(exist_ok=True)

print("ArcFace ONNX Face Recognition project structure created successfully.")
