"""
MaxiCode Decoder using ZXing (Java library)
MaxiCode is used primarily by UPS for package tracking and logistics
"""

import cv2
import numpy as np
import subprocess
import os
import sys
import shutil
from urllib.parse import quote

# Paths to required JAR files (same as PDF417)
JAVASE_JAR = "javase-3.5.0.jar"
CORE_JAR = "core-3.5.0.jar"
JCOMMANDER_JAR = "jcommander-1.82.jar"

def preprocess_image(img):
    """Create multiple enhanced versions of the image for better detection"""
    enhanced = []
    
    # Original grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    enhanced.append(("Original grayscale", gray))
    
    # Adaptive threshold
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    enhanced.append(("Adaptive threshold", thresh))
    
    # Otsu threshold
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    enhanced.append(("Otsu threshold", otsu))
    
    # Contrast enhancement using CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    clahe_img = clahe.apply(gray)
    enhanced.append(("CLAHE enhanced", clahe_img))
    
    # Denoised
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    enhanced.append(("Denoised", denoised))
    
    # Upscaled 2x for better detail
    upscaled = cv2.resize(gray, (gray.shape[1] * 2, gray.shape[0] * 2), 
                         interpolation=cv2.INTER_CUBIC)
    enhanced.append(("Upscaled 2x", upscaled))
    
    # Inverted (sometimes needed for dark codes on light background)
    inverted = cv2.bitwise_not(gray)
    enhanced.append(("Inverted", inverted))
    
    return enhanced

def validate_files():
    """Check if all required JAR files exist"""
    jar_files = [JAVASE_JAR, CORE_JAR, JCOMMANDER_JAR]
    missing = [f for f in jar_files if not os.path.exists(f)]
    if missing:
        print(f"[WARNING] Missing JAR files: {', '.join(missing)}")
        print("Attempting to copy from PDF417 directory...")
        # Get PDF417 directory (parent directory + PDF417)
        current_dir = os.getcwd()
        pdf417_dir = os.path.join(os.path.dirname(current_dir), "PDF417")
        for jar in missing:
            src = os.path.join(pdf417_dir, jar)
            if os.path.exists(src):
                shutil.copy(src, jar)
                print(f"  Copied {jar}")

def create_local_java_command(image_path):
    """Create Java command to run ZXing decoder"""
    classpath = f"{JAVASE_JAR};{CORE_JAR};{JCOMMANDER_JAR}"
    
    # Convert to proper file URI format for Windows paths with spaces
    abs_path = os.path.abspath(image_path)
    abs_path_forward = abs_path.replace("\\", "/")
    file_uri = f"file:///{quote(abs_path_forward, safe=':/')}"
    
    return [
        "java", "-cp", classpath,
        "com.google.zxing.client.j2se.CommandLineRunner",
        file_uri
    ]

def decode_with_zxing(image_path, debug=False):
    """Decode barcode using ZXing library"""
    try:
        cmd = create_local_java_command(image_path)
        result = subprocess.run(cmd, capture_output=True, text=True, 
                               timeout=30, check=False)
        output = result.stdout.strip()
        stderr = result.stderr.strip()
        
        if debug and stderr:
            print(f"  DEBUG stderr: {stderr}")
        
        if output:
            return output
        return None
    except Exception as e:
        if debug:
            print(f"  DEBUG: Exception: {e}")
        return None

def parse_zxing_output(output):
    """Parse ZXing output to extract decoded text"""
    lines = output.splitlines()
    decoded_text = None
    collecting = False
    collected_lines = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith("file://"):
            continue
        if "No barcode found" in line:
            return None
        
        # Check if we're starting to collect "Raw result:" or "Parsed result:"
        if line.startswith("Raw result:") or line.startswith("Parsed result:"):
            parts = line.split(":", 1)
            if len(parts) > 1 and parts[1].strip():
                decoded_text = parts[1].strip()
                collecting = True
                collected_lines = [decoded_text]
            else:
                collecting = True
                collected_lines = []
            continue
        
        # If we're collecting, add lines until we hit a metadata line
        if collecting:
            if ":" in line and not any(x in line.lower() for x in ["result", "format", "type", "found"]):
                # End of result data
                break
            elif line and not line.startswith("Found") and ":" not in line:
                collected_lines.append(line)
            elif line.startswith("Found"):
                break
        
        # If we haven't started collecting yet and find content
        if not collecting and decoded_text is None and ":" not in line:
            decoded_text = line
            if decoded_text:
                break
    
    # Join collected lines if we collected multiple
    if collected_lines:
        decoded_text = "".join(collected_lines).strip()
    
    return decoded_text

def decode_maxicode(image_path):
    """Decode MaxiCode from image with multiple preprocessing attempts using ZXing"""
    
    # Validate file exists
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found!")
        return None
    
    print("="*70)
    print("MAXICODE DECODER")
    print("="*70)
    print(f"Processing: {image_path}\n")
    
    # Check if Java is available
    if shutil.which("java") is None:
        print("[ERROR] Java is not installed or not in PATH")
        print("Please install Java JDK (version 17 or later)")
        return None
    
    # Validate JAR files
    validate_files()
    
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Unable to read image file '{image_path}'")
            return None
        
        print(f"Image loaded: {image.shape}")
        
        # Try original image first
        output = decode_with_zxing(image_path)
        decoded_text = parse_zxing_output(output) if output else None
        
        if decoded_text:
            print(f"[SUCCESS] Decoded using original image")
        else:
            print("[INFO] Original image failed, trying enhanced variants...")
            
            # Try preprocessed versions
            enhanced_images = preprocess_image(image)
            temp_files = []
            
            for name, img_data in enhanced_images:
                print(f"  Trying: {name}...", end=" ")
                try:
                    temp_path = f"temp_{name}"
                    cv2.imwrite(temp_path, img_data)
                    temp_files.append(temp_path)
                    
                    output = decode_with_zxing(temp_path)
                    decoded_text = parse_zxing_output(output) if output else None
                    
                    if decoded_text:
                        print("SUCCESS!")
                        break
                    else:
                        print("failed")
                except Exception as e:
                    print(f"error: {e}")
            
            # Clean up temp files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass
        
        if not decoded_text:
            print("\n[FAILED] No MaxiCode detected after trying all variants!")
            print("\nTips:")
            print("  - Ensure the bull's-eye center pattern is visible")
            print("  - Check image quality and resolution")
            print("  - MaxiCode requires good contrast and lighting")
            print("  - Ensure all hexagonal modules are clear")
            return None
        
        # Store decoded data
        decoded_data_list = [decoded_text]
        
        # Print details
        print(f"\n[SUCCESS] MaxiCode Decoded")
        print(f"   Data: {decoded_text}")
        print(f"   Type: MAXICODE")
        print(f"   Data Length: {len(decoded_text)} characters")
        
        # Parse structured data (UPS format)
        if len(decoded_text) > 20:
            print(f"\n   MaxiCode Structure:")
            print(f"      Raw Data: {decoded_text[:50]}...")
            print(f"      (Shipping/Tracking Information)")
        
        print("-" * 70)
        
        # Draw annotation on image (center marking)
        h, w = image.shape[:2]
        cv2.circle(image, (w//2, h//2), 50, (0, 255, 0), 3)
        cv2.putText(image, "MAXICODE", (w//2 - 50, h//2 - 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        # Save annotated image
        output_path = "annotated_maxicode.png"
        cv2.imwrite(output_path, image)
        print(f"\n[INFO] Annotated image saved: {output_path}")
        
        # Display
        cv2.imshow("MaxiCode Detection", image)
        print("\n[INFO] Press any key to close the preview window...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return decoded_data_list
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Use maxicode.png as the image file (checking both .png and .jpg)
    image_file = "maxicode.png"
    if not os.path.exists(image_file):
        image_file = "maxicode.jpg"
    
    # Allow command line argument
    if len(sys.argv) > 1:
        image_file = sys.argv[1]
    
    # Decode the MaxiCode
    results = decode_maxicode(image_file)
    
    if results:
        print("\n" + "="*70)
        print("SUMMARY - ALL DECODED DATA")
        print("="*70)
        for i, data in enumerate(results, 1):
            print(f"{i}. {data}")