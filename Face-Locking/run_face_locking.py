#!/usr/bin/env python3
"""
Face Locking System Launcher

Simple launcher script for the Face Locking System
"""

import subprocess
import sys
from pathlib import Path

def main():
    print("🔒 Face Locking System Launcher")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("src/face_locking.py").exists():
        print("❌ Error: Please run this script from the Face-Locking directory")
        return
    
    print("Choose an option:")
    print("1. 👤 Enroll new faces")
    print("2. 🔒 Start Face Locking")
    print("3. 📷 Test camera")
    print("4. 🧪 Run system tests")
    print("5. ❌ Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                print("\n🚀 Starting face enrollment...")
                subprocess.run([sys.executable, "-m", "src.enroll"])
                
            elif choice == "2":
                print("\n🚀 Starting Face Locking System...")
                subprocess.run([sys.executable, "-m", "src.face_locking"])
                
            elif choice == "3":
                print("\n🚀 Testing camera...")
                subprocess.run([sys.executable, "-m", "src.camera"])
                
            elif choice == "4":
                print("\n🚀 Running system tests...")
                subprocess.run([sys.executable, "test_system.py"])
                
            elif choice == "5":
                print("\n👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                continue
                
            print("\n" + "=" * 40)
            print("Choose another option or press 5 to exit:")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()