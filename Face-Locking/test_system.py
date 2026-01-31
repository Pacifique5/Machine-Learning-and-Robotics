#!/usr/bin/env python3
"""
Test script for Face Locking System

This script tests the basic functionality of the face locking system
without requiring camera input.
"""

import sys
from pathlib import Path
import numpy as np

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import cv2
        print(f"✅ OpenCV: {cv2.__version__}")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import numpy as np
        print(f"✅ NumPy: {np.__version__}")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        import onnxruntime as ort
        print(f"✅ ONNX Runtime: {ort.__version__}")
    except ImportError as e:
        print(f"❌ ONNX Runtime import failed: {e}")
        return False
    
    try:
        import mediapipe as mp
        print(f"✅ MediaPipe: {mp.__version__}")
    except ImportError as e:
        print(f"❌ MediaPipe import failed: {e}")
        return False
    
    return True

def test_project_structure():
    """Test if required files and directories exist"""
    print("\n📁 Testing project structure...")
    
    required_files = [
        "models/embedder_arcface.onnx",
        "src/face_locking.py",
        "src/recognize.py",
        "src/enroll.py",
        "src/haar_5pt.py",
        "requirements.txt"
    ]
    
    required_dirs = [
        "src",
        "models", 
        "data"
    ]
    
    all_good = True
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing!")
            all_good = False
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - Missing!")
            all_good = False
    
    return all_good

def test_face_database():
    """Test if face database exists and is readable"""
    print("\n👤 Testing face database...")
    
    db_path = Path("data/db/face_db.npz")
    
    if not db_path.exists():
        print("⚠️  No face database found. Run enrollment first:")
        print("   python -m src.enroll")
        return False
    
    try:
        data = np.load(str(db_path), allow_pickle=True)
        identities = list(data.files)
        print(f"✅ Face database loaded successfully")
        print(f"📊 Found {len(identities)} enrolled identities:")
        for identity in identities:
            embedding = data[identity]
            print(f"   - {identity}: {embedding.shape} embedding")
        return True
    except Exception as e:
        print(f"❌ Failed to load face database: {e}")
        return False

def test_model_loading():
    """Test if ArcFace model can be loaded"""
    print("\n🤖 Testing ArcFace model...")
    
    model_path = Path("models/embedder_arcface.onnx")
    
    if not model_path.exists():
        print("❌ ArcFace model not found!")
        return False
    
    try:
        import onnxruntime as ort
        session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
        
        input_shape = session.get_inputs()[0].shape
        output_shape = session.get_outputs()[0].shape
        
        print(f"✅ ArcFace model loaded successfully")
        print(f"📐 Input shape: {input_shape}")
        print(f"📐 Output shape: {output_shape}")
        return True
    except Exception as e:
        print(f"❌ Failed to load ArcFace model: {e}")
        return False

def test_face_locking_import():
    """Test if face locking module can be imported"""
    print("\n🔒 Testing Face Locking module...")
    
    try:
        sys.path.insert(0, str(Path.cwd()))
        from src.face_locking import FaceLockingSystem, FaceLockConfig, ActionDetector
        print("✅ Face Locking module imported successfully")
        
        # Test configuration
        config = FaceLockConfig()
        print(f"✅ Configuration created: lock_threshold={config.lock_confidence_threshold}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to import Face Locking module: {e}")
        print(f"Error details: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Face Locking System - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Project Structure", test_project_structure), 
        ("Model Loading", test_model_loading),
        ("Face Database", test_face_database),
        ("Face Locking Module", test_face_locking_import)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Face Locking System is ready to use.")
        print("\nNext steps:")
        print("1. Enroll faces: python -m src.enroll")
        print("2. Run face locking: python -m src.face_locking")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues before running the system.")
        
        if not any(name == "Face Database" and result for name, result in results):
            print("\n💡 Tip: If face database test failed, run enrollment first:")
            print("   python -m src.enroll")

if __name__ == "__main__":
    main()