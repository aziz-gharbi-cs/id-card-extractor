import cv2
import numpy as np
from PIL import Image

def load_image(path):
    """
    Loads an image from the specified path using OpenCV.
    """
    try:
        image = cv2.imread(path)
        if image is None:
            raise FileNotFoundError(f"Image not found at path: {path}")
        return image
    except Exception as e:
        raise RuntimeError(f"Error loading image: {e}")

def preprocess_image(image):
    """
    Prepares the image for OCR by converting to grayscale, removing noise,
    and applying thresholding.
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian Blur to remove noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Adaptive Thresholding to binarize the image (handle uneven lighting)
    # Block size and C constant might need tuning based on image resolution
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    
    return gray, thresh

def correct_skew(image):
    """
    Detects and corrects skew in the image using minAreaRect.
    """
    # Use the thresholded image for contour detection
    gray, thresh = preprocess_image(image)
    
    # Invert the image (text is usually black on white, we want white on black for contours)
    coords = np.column_stack(np.where(thresh > 0))
    
    # If the image is mostly white (standard document), we might want to invert logic
    # But usually adaptive threshold gives a good edge map. 
    # Let's try a safer approach: find the largest contour which is likely the card boundary
    
    # For text skew, we can use the text lines themselves
    # But for now, let's implement a simple rotation based on edges
    
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
    
    angle = 0.0
    if lines is not None:
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x2 - x1 == 0: continue 
            rads = np.arctan2((y2 - y1), (x2 - x1))
            deg = np.degrees(rads)
            if -45 < deg < 45: # Only consider horizontal-ish lines
                angles.append(deg)
        
        if angles:
            angle = np.median(angles)
    
    if abs(angle) > 0.5:
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated
    
    return image

def pil_to_cv2(pil_image):
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

def cv2_to_pil(cv_image):
    return Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
