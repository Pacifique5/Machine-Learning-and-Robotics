#!/usr/bin/env python3
"""
Test keyboard input with OpenCV windows
"""

import cv2
import numpy as np

def test_keyboard():
    """Test if keyboard input works with OpenCV"""
    
    print("🎮 Testing Keyboard Input")
    print("=" * 40)
    print("Instructions:")
    print("- Click on the OpenCV window to give it focus")
    print("- Press keys and see if they're detected")
    print("- Press 'q' to quit")
    print("- Press SPACE to test space key")
    print("- Press 'a' to test 'a' key")
    
    # Create a simple test window
    window_name = "Keyboard Test"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    # Create a test image
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    
    last_key = "None"
    key_count = 0
    
    while True:
        # Update display
        test_img = img.copy()
        
        # Draw instructions
        cv2.putText(test_img, "Keyboard Input Test", (20, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(test_img, "Click this window first!", (20, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(test_img, f"Last key pressed: {last_key}", (20, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(test_img, f"Total keys pressed: {key_count}", (20, 200), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Instructions
        cv2.putText(test_img, "Press 'q' to quit", (20, 300), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(test_img, "Press SPACE to test space", (20, 330), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(test_img, "Press 'a' to test 'a'", (20, 360), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.imshow(window_name, test_img)
        
        # Check for key press - try different wait times
        key = cv2.waitKey(30) & 0xFF  # Longer wait time
        
        if key != 255:  # 255 means no key pressed
            key_count += 1
            
            if key == ord('q'):
                last_key = "q (quit)"
                print(f"✅ 'q' key detected! Quitting...")
                break
            elif key == ord(' '):
                last_key = "SPACE"
                print(f"✅ SPACE key detected!")
            elif key == ord('a'):
                last_key = "a"
                print(f"✅ 'a' key detected!")
            elif key == 27:  # ESC
                last_key = "ESC"
                print(f"✅ ESC key detected!")
            else:
                last_key = f"'{chr(key)}' (code: {key})"
                print(f"✅ Key detected: {last_key}")
    
    cv2.destroyAllWindows()
    
    if key_count > 0:
        print(f"\n✅ Keyboard input is working! ({key_count} keys detected)")
    else:
        print(f"\n❌ No keyboard input detected!")
        print("Possible issues:")
        print("- OpenCV window doesn't have focus")
        print("- Keyboard input blocked by system")
        print("- OpenCV version issue")

if __name__ == "__main__":
    test_keyboard()