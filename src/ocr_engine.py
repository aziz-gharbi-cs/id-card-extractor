import pytesseract
from PIL import Image
import sys
import os

# NOTE: Tesseract binary path might need to be configured by the user 
# if it is not in the system PATH.
# Example: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_tesseract(image, config='--psm 3', lang='eng'):
    """
    Extracts raw text from the image using Tesseract OCR.
    PSM 3 is 'Fully automatic page segmentation, but no OSD.'
    """
    try:
        # Pytesseract accepts both PIL Image and Numpy array (OpenCV image)
        text = pytesseract.image_to_string(image, config=config, lang=lang)
        return text
    except pytesseract.TesseractNotFoundError:
        raise OSError("Tesseract is not installed or not in your PATH. Please see README.")
    except Exception as e:
        raise RuntimeError(f"OCR failed: {e}")

def extract_data_with_confidence(image, config='--psm 3'):
    """
    Extracts text with confidence scores.
    Returns a dictionary including text and confidence levels.
    """
    try:
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, config=config)
        return data  # Contains keys: 'level', 'page_num', 'block_num', ..., 'text', 'conf'
    except Exception as e:
        raise RuntimeError(f"OCR data extraction failed: {e}")
