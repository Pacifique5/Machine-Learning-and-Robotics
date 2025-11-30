from pylibdmtx.pylibdmtx import decode
from PIL import Image
import cv2
import numpy as np
import os
import sys

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
    
    # Inverted (sometimes needed for dark barcodes on light background)
    inverted = cv2.bitwise_not(gray)
    enhanced.append(("Inverted", inverted))
    
    return enhanced

def decode_datamatrix(image_path):
    """Decode Data Matrix barcode from image with multiple preprocessing attempts"""
    
    # Validate file exists
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found!")
        return None
    
    print("="*70)
    print("DATA MATRIX BARCODE DECODER")
    print("="*70)
    print(f"Processing: {image_path}\n")
    
    try:
        # Load image
        cv_image = cv2.imread(image_path)
        if cv_image is None:
            print(f"Error: Unable to read image file '{image_path}'")
            return None
        
        print(f"Image loaded: {cv_image.shape}")
        
        # Try original image first
        pil_image = Image.open(image_path)
        results = decode(pil_image)
        
        if results:
            print(f"[SUCCESS] Decoded using original image")
        else:
            print("[INFO] Original image failed, trying enhanced variants...")
            
            # Try preprocessed versions
            enhanced_images = preprocess_image(cv_image)
            
            for name, img_data in enhanced_images:
                print(f"  Trying: {name}...", end=" ")
                try:
                    # Convert OpenCV image to PIL Image
                    pil_img = Image.fromarray(img_data)
                    results = decode(pil_img)
                    
                    if results:
                        print("SUCCESS!")
                        break
                    else:
                        print("failed")
                except Exception as e:
                    print(f"error: {e}")
        
        if not results:
            print("\n[FAILED] No Data Matrix barcode detected after trying all variants!")
            print("\nTips:")
            print("  - Ensure good image quality and lighting")
            print("  - Check if the Data Matrix is visible and undamaged")
            print("  - Try preprocessing the image (contrast, brightness)")
            return None
        
        # Reload image for visualization if we used a preprocessed version
        if cv_image is None:
            cv_image = cv2.imread(image_path)
        
        print(f"[SUCCESS] Found {len(results)} Data Matrix barcode(s)\n")
        
        decoded_data_list = []
        
        for i, result in enumerate(results, 1):
            # Extract data
            try:
                decoded_data = result.data.decode('utf-8')
            except:
                decoded_data = str(result.data)
            
            decoded_data_list.append(decoded_data)
            
            # Get dimensions
            rect = result.rect
            left, top = rect.left, rect.top
            width, height = rect.width, rect.height
            
            # Print details
            print(f"Data Matrix #{i}")
            print(f"   Data: {decoded_data}")
            print(f"   Position: (x={left}, y={top})")
            print(f"   Size: {width}x{height} pixels")
            print(f"   Data Length: {len(decoded_data)} characters")
            print("-" * 70)
            
            # Visualize
            cv2.rectangle(cv_image, 
                         (left, top), 
                         (left + width, top + height), 
                         (0, 255, 0), 3)
            
            cv2.putText(cv_image, 
                       f"DM-{i}", 
                       (left, top - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 
                       0.9, (0, 255, 0), 2)
        
        # Save annotated image
        output_path = "annotated_datamatrix.png"
        cv2.imwrite(output_path, cv_image)
        print(f"\n[INFO] Annotated image saved: {output_path}")
        
        # Display
        cv2.imshow("Data Matrix Detection", cv_image)
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
    # Use datamatrix.jpg as the image file
    image_file = "datamatrix.jpg"
    
    # Allow command line argument
    if len(sys.argv) > 1:
        image_file = sys.argv[1]
    
    # Decode the Data Matrix
    results = decode_datamatrix(image_file)
    
    if results:
        print("\n" + "="*70)
        print("SUMMARY - ALL DECODED DATA")
        print("="*70)
        for i, data in enumerate(results, 1):
            print(f"{i}. {data}")