# Face Locking System 🔒

A real-time face tracking and behavior monitoring system that locks onto specific enrolled identities and tracks their actions over time.

## 🎯 Overview

The Face Locking System extends traditional face recognition by adding **persistent tracking** and **action detection**. When a target person appears in the camera frame, the system:

1. **Locks onto their face** with high confidence recognition
2. **Tracks consistently** across frames, even during brief recognition failures  
3. **Detects face actions** like movement, blinking, and smiling
4. **Records action history** to timestamped files for analysis

## 🚀 Features

### Core Functionality
- **Manual Identity Selection**: Choose which enrolled person to track
- **Intelligent Face Locking**: Locks when target appears with high confidence (66%+ similarity)
- **Stable Tracking**: Maintains lock even during brief recognition failures
- **Automatic Lock Release**: Releases lock after 3 seconds without detection

### Action Detection
The system detects and records these actions while locked:

| Action Type | Detection Method | Description |
|-------------|------------------|-------------|
| **Movement** | Face center tracking | Detects left/right face movement (>30px threshold) |
| **Eye Blink** | Eye aspect ratio analysis | Monitors eye opening/closing patterns |
| **Smile/Laugh** | Mouth curvature analysis | Detects facial expression changes |

### History Recording
- **Automatic file creation**: `<name>_history_<timestamp>.txt`
- **Real-time logging**: Each action recorded with precise timestamp
- **Session summaries**: Total actions and duration statistics
- **Structured format**: Easy to parse and analyze

## 📁 Project Structure

```
Face-Locking/
├── src/
│   ├── face_locking.py      # Main face locking system
│   ├── recognize.py         # Base recognition pipeline  
│   ├── enroll.py           # Face enrollment
│   ├── haar_5pt.py         # Face detection & alignment
│   └── embed.py            # ArcFace embeddings
├── models/
│   └── embedder_arcface.onnx # Pre-trained ArcFace model
├── data/
│   ├── db/                 # Face database (embeddings)
│   ├── enroll/             # Enrollment face crops
│   └── history/            # Action history files
└── README.md
```

## 🛠️ Installation & Setup

### 1. Install Dependencies
```bash
cd Face-Locking
pip install -r requirements.txt
```

**Required packages:**
- `opencv-python` - Computer vision operations
- `numpy` - Numerical computations  
- `onnxruntime>=1.15.1` - ONNX model inference
- `mediapipe==0.10.11` - Facial landmark detection

### 2. Verify Installation
```bash
python -m src.camera  # Test camera access
```

## 📖 Usage Guide

### Step 1: Enroll Faces (First Time)
```bash
python -m src.enroll
```
- Enter person's name when prompted
- Capture 15+ face samples using **SPACE** or **'a'** (auto-capture)
- Press **'s'** to save to database
- Repeat for each person you want to track

### Step 2: Run Face Locking
```bash
python -m src.face_locking
```
- Select target identity from enrolled list
- Position target person in camera view
- System automatically locks when it recognizes them
- Actions are detected and logged in real-time

### Step 3: Review History Files
History files are saved in `data/history/` with format:
```
<name>_history_<timestamp>.txt
```

**Example: `charles_history_20260131143022.txt`**
```
Face Locking History for: charles
Session started: 2026-01-31 14:30:22
==================================================
Timestamp		Action Type	Description		Value
----------------------------------------------------------------------
14:30:25.123	movement	face moved right	45.230
14:30:27.456	blink		eye blink detected	0.187
14:30:29.789	smile		smile or laugh detected	0.034
----------------------------------------------------------------------
Session ended: 2026-01-31 14:32:15
Total actions recorded: 23
Action Summary:
  movement: 12
  blink: 8  
  smile: 3
```

## 🎮 Controls

### During Face Locking:
| Key | Action |
|-----|--------|
| **q** | Quit application |
| **r** | Manually release current lock |
| **t** | Change target identity (restart required) |
| **s** | Show current statistics |

### During Enrollment:
| Key | Action |
|-----|--------|
| **SPACE** | Capture one face sample |
| **a** | Toggle auto-capture mode |
| **s** | Save person to database |
| **r** | Reset new samples |
| **q** | Quit enrollment |

## 🔧 Configuration

Key parameters in `FaceLockConfig`:

```python
@dataclass
class FaceLockConfig:
    lock_confidence_threshold: float = 0.66    # Similarity to lock (66%)
    lock_timeout_seconds: float = 3.0          # Release after 3s without detection
    tracking_tolerance: float = 0.45           # Lower threshold while tracking
    movement_threshold: float = 30.0           # Pixels for movement detection
    blink_threshold: float = 0.25             # Eye aspect ratio for blinks
    smile_threshold: float = 0.02             # Mouth curve for smiles
```

## 🧠 How Face Locking Works

### 1. **Recognition Pipeline**
```
Camera Frame → Haar Face Detection → MediaPipe 5-Point Landmarks → 
Face Alignment (112x112) → ArcFace Embedding → Cosine Similarity Matching
```

### 2. **Locking Logic**
- **Lock Trigger**: Target identity recognized with ≥66% similarity
- **Lock Maintenance**: Continue tracking with ≥45% similarity (lower threshold)
- **Lock Release**: No detection for 3+ seconds

### 3. **Action Detection**
- **Movement**: Track face center position changes
- **Blink**: Monitor eye aspect ratio fluctuations  
- **Smile**: Analyze mouth landmark curvature changes

### 4. **Tracking Stability**
- Uses spatial proximity to maintain face association
- Tolerates brief recognition failures
- Prevents jumping between different faces

## 📊 Technical Details

### Face Detection & Landmarks
- **Haar Cascade**: Multi-face detection with configurable minimum size
- **MediaPipe FaceMesh**: 5-point facial landmarks (eyes, nose, mouth corners)
- **Face Alignment**: Standardized 112x112 pixel face crops

### Embedding & Matching  
- **ArcFace ONNX**: 512-dimensional L2-normalized face embeddings
- **Cosine Similarity**: Distance metric for face matching
- **Dynamic Thresholds**: Higher confidence for locking, lower for tracking

### Action Detection Algorithms
- **Movement**: Euclidean distance between face centers across frames
- **Blink**: Eye aspect ratio based on landmark geometry
- **Smile**: Mouth curvature approximation using corner positions

## 🎯 Example Use Cases

1. **Security Monitoring**: Track specific individuals in surveillance footage
2. **Behavioral Analysis**: Study facial expressions and movements over time  
3. **Interactive Systems**: Respond to specific people's actions and gestures
4. **Accessibility**: Monitor user engagement and attention patterns
5. **Research**: Collect behavioral data for psychological or UX studies

## 🔍 Troubleshooting

### Common Issues:

**"No face database found"**
- Run `python -m src.enroll` first to create face database

**"Camera not available"** 
- Check camera permissions and connections
- Try different camera indices (0, 1, 2) in code

**"Poor tracking performance"**
- Ensure good lighting conditions
- Adjust `lock_confidence_threshold` and `tracking_tolerance`
- Re-enroll with more diverse face samples

**"Actions not detected"**
- Check detection thresholds in configuration
- Ensure clear view of face landmarks
- Verify face is properly aligned

## 🚀 Future Enhancements

- **Multi-target tracking**: Lock onto multiple identities simultaneously
- **Advanced actions**: Head pose, gaze direction, emotion classification
- **Real-time alerts**: Trigger notifications for specific action patterns
- **Data visualization**: Graphical analysis of action history
- **Mobile deployment**: Port to mobile devices with optimized models

## 📄 License

This project builds upon the ArcFace ONNX face recognition system and is intended for educational and research purposes.

---

**Built with ❤️ for intelligent computer vision applications**