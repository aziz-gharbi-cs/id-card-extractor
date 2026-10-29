import gradio as gr
import cv2
import numpy as np
import json
import os
from PIL import Image
import pytesseract
from mrz.checker.td1 import TD1CodeChecker
from mrz.checker.td3 import TD3CodeChecker
import re

# Set Tesseract Language Path to local directory if it exists
local_tessdata = os.path.join(os.path.dirname(__file__), 'tessdata')
if os.path.exists(local_tessdata):
    os.environ['TESSDATA_PREFIX'] = local_tessdata

# Set Tesseract path (adjust if needed)
# Try common paths
tesseract_paths = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',  # Windows
    '/usr/bin/tesseract',  # Linux
    '/usr/local/bin/tesseract',  # macOS/Homebrew
]

for path in tesseract_paths:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        break
else:
    # If none found, assume it's in PATH
    pass

# Image Preprocessing Functions
def load_image_from_bytes(image_bytes):
    """Loads an image from bytes using OpenCV."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Invalid image data")
    return image

def preprocess_image(image):
    """Prepares the image for OCR by converting to grayscale, removing noise, and applying thresholding."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)
    return gray, thresh

def correct_skew(image):
    """Detects and corrects skew in the image using Hough lines."""
    gray, thresh = preprocess_image(image)
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
            if -45 < deg < 45:
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

def cv2_to_pil(cv_image):
    """Converts OpenCV image to PIL Image."""
    return Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))

# OCR Engine
def extract_text_tesseract(image, config='--psm 3', lang='eng'):
    """Extracts raw text from the image using Tesseract OCR."""
    try:
        text = pytesseract.image_to_string(image, config=config, lang=lang)
        return text
    except pytesseract.TesseractNotFoundError:
        raise RuntimeError("Tesseract OCR is not installed or not found in PATH. Please install Tesseract OCR.")
    except Exception as e:
        raise RuntimeError(f"OCR failed: {e}")

# Parsers
class MRZParser:
    def find_mrz_candidates(self, text):
        """Extracts lines that look like MRZ lines."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        candidates = []
        for line in lines:
            clean_line = line.replace(' ', '')
            if len(clean_line) > 20 and '<' in clean_line:
                candidates.append(clean_line)
        return candidates

    def parse(self, text):
        candidates = self.find_mrz_candidates(text)
        if not candidates:
            return None

        mrz_data = {"raw": candidates, "parsed": {}, "type": "Unknown", "valid": False}
        reversed_cand = list(reversed(candidates))

        # Check for TD3 (Passport) - 2 lines
        for i in range(len(reversed_cand) - 1):
            line2 = reversed_cand[i]
            line1 = reversed_cand[i+1]
            try:
                td3_check = TD3CodeChecker(line1 + "\n" + line2)
                if td3_check.valid:
                    mrz_data["parsed"] = td3_check.fields()
                    mrz_data["type"] = "TD3 (Passport)"
                    mrz_data["valid"] = True
                    return mrz_data
            except Exception:
                pass

        # Check for TD1 (ID Card) - 3 lines
        for i in range(len(reversed_cand) - 2):
            line3 = reversed_cand[i]
            line2 = reversed_cand[i+1]
            line1 = reversed_cand[i+2]
            try:
                td1_check = TD1CodeChecker(line1 + "\n" + line2 + "\n" + line3)
                if td1_check.valid:
                    mrz_data["parsed"] = td1_check.fields()
                    mrz_data["type"] = "TD1 (Identity Card)"
                    mrz_data["valid"] = True
                    return mrz_data
            except Exception:
                pass

        return mrz_data

class RegexParser:
    def parse(self, text):
        extracted = {}
        name_match = re.search(r'(?:Name|Surname|Given Names)\s*[:.]?\s*([A-Z\s]+)', text, re.IGNORECASE)
        if name_match:
            extracted['full_name'] = {"value": name_match.group(1).strip(), "confidence": 0.7}

        dob_match = re.search(r'(?:DOB|Date of Birth|Birth)\s*[:.]?\s*(\d{2}[-/.]\d{2}[-/.]\d{4}|\d{4}[-/.]\d{2}[-/.]\d{2})', text, re.IGNORECASE)
        if dob_match:
            extracted['date_of_birth'] = {"value": dob_match.group(1), "confidence": 0.8}

        return extracted

class CombinedParser:
    def __init__(self):
        self.mrz_parser = MRZParser()
        self.regex_parser = RegexParser()

    def parse(self, text):
        final_result = {
            "document_type": "Unknown",
            "fields": {},
            "mrz": {}
        }

        mrz_result = self.mrz_parser.parse(text)
        if mrz_result and mrz_result.get("valid"):
            final_result["mrz"] = mrz_result
            final_result["document_type"] = mrz_result.get("type", "Unknown")

            fields = mrz_result.get("parsed", {})
            if "surname" in fields and "name" in fields:
                final_result["fields"]["full_name"] = {"value": f"{fields.get('surname', '')} {fields.get('name', '')}", "confidence": 1.0}
            if "birth_date" in fields:
                final_result["fields"]["date_of_birth"] = {"value": fields.get("birth_date"), "confidence": 1.0}
            if "expiry_date" in fields:
                final_result["fields"]["expiration_date"] = {"value": fields.get("expiry_date"), "confidence": 1.0}
            if "nationality" in fields:
                final_result["fields"]["nationality"] = {"value": fields.get("nationality"), "confidence": 1.0}
            if "sex" in fields:
                final_result["fields"]["gender"] = {"value": fields.get("sex"), "confidence": 1.0}
            if "document_number" in fields:
                final_result["fields"]["id_number"] = {"value": fields.get("document_number"), "confidence": 1.0}

        regex_result = self.regex_parser.parse(text)
        for key, val in regex_result.items():
            if key not in final_result["fields"]:
                final_result["fields"][key] = val

        return final_result

# Main extraction function
def extract_credentials(image_bytes):
    """Main function to extract credentials from ID card/passport image."""
    try:
        # Load and preprocess image
        image = load_image_from_bytes(image_bytes)
        deskewed = correct_skew(image)
        pil_image = cv2_to_pil(deskewed)

        # Extract text
        raw_text = extract_text_tesseract(pil_image)

        # Parse data
        parser = CombinedParser()
        result = parser.parse(raw_text)

        # Format output
        output = {
            "document_type": result.get("document_type", "Unknown"),
            "extracted_data": result.get("fields", {}),
            "raw_text": raw_text[:500]  # Limit raw text length
        }

        return output

    except Exception as e:
        return {"error": str(e)}

def format_output_markdown(output_dict):
    if "error" in output_dict:
        return f"### ❌ Error\n{output_dict['error']}"
    
    md = f"### 📄 Document Type: **{output_dict.get('document_type', 'Unknown')}**\n\n"
    
    fields = output_dict.get("extracted_data", {})
    if fields:
        md += "#### 📋 Extracted Fields\n"
        md += "| Field | Value | Confidence |\n"
        md += "|-------|-------|------------|\n"
        for key, data in fields.items():
            value = data.get("value", "")
            try:
                conf = float(data.get("confidence", 0))
                conf_str = f"{conf:.2f}"
            except (ValueError, TypeError):
                conf_str = str(data.get("confidence", ""))
            md += f"| **{key.replace('_', ' ').title()}** | {value} | {conf_str} |\n"
    else:
        md += "_No fields extracted._\n"
        
    raw_text = output_dict.get("raw_text", "")
    if raw_text:
        md += "\n#### 🔍 Raw OCR Text\n"
        md += f"```text\n{raw_text}\n```"
        
    return md

# Gradio Interface
def gradio_interface(image_path):
    if image_path is None:
        return "Please upload an image."
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    output_dict = extract_credentials(image_bytes)
    return format_output_markdown(output_dict)

# Create Gradio app
iface = gr.Interface(
    fn=gradio_interface,
    inputs=gr.Image(type="filepath", label="Upload ID Card or Passport Image"),
    outputs=gr.Markdown(label="Extracted Credentials"),
    title="ID Card & Passport Data Extractor",
    description="Upload an image of an ID card or passport to extract structured data automatically.",
    examples=[]
)

if __name__ == "__main__":
    iface.launch(inbrowser=True)
