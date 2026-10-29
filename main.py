import argparse
import json
import sys
import os
from src.preprocessor import load_image, preprocess_image, correct_skew, cv2_to_pil
from src.ocr_engine import extract_text_tesseract
from src.parser import CombinedParser

def main():
    parser = argparse.ArgumentParser(description="ID Card Data Extractor")
    parser.add_argument("image_path", help="Path to the input image file")
    parser.add_argument("--debug", action="store_true", help="Enable debug output (show images)")
    args = parser.parse_args()

    if not os.path.exists(args.image_path):
        print(json.dumps({"error": "File not found"}), file=sys.stderr)
        sys.exit(1)

    try:
        # 1. Load Image
        image = load_image(args.image_path)
        
        # 2. Preprocessing
        # Deskew
        deskewed = correct_skew(image)
        # Denoise/Threshold (we might use original for some OCR, and optimized for other)
        # For Tesseract, a clean grayscale or binarized image is often best
        gray, thresh = preprocess_image(deskewed)
        
        pil_image = cv2_to_pil(deskewed) # Tesseract often works well with just the deskewed color/gray image too

        # 3. OCR text extraction
        # We try multiple configurations if needed, but starting simple
        raw_text = extract_text_tesseract(pil_image)
        
        # 4. Parsing
        data_parser = CombinedParser()
        result = data_parser.parse(raw_text)
        
        # Add metadata
        result["metadata"] = {
            "source_file": args.image_path,
            "success": True
        }
        
        print(json.dumps(result, indent=2))

    except Exception as e:
        error_response = {
            "error": str(e),
            "success": False
        }
        print(json.dumps(error_response), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
