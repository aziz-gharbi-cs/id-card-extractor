# ID Card Data Extractor - Gradio App

This is a Gradio web application for extracting structured data from images of passports and ID cards using OCR and MRZ parsing.

## Features
- **Image Upload**: Upload images of ID cards (TD1) or Passports (TD3)
- **Automatic Processing**: Deskewing, denoising, and OCR
- **MRZ Parsing**: Support for TD1 (ID Cards) and TD3 (Passports) Machine Readable Zones
- **Fallback Regex Parsing**: Extracts Name and Date of Birth from visual text if MRZ is missing
- **JSON Output**: Returns clean, structured data

## Deployment on Hugging Face Spaces

1. **Create a new Space** on [Hugging Face](https://huggingface.co/spaces)
   - Choose "Gradio" as the SDK
   - Select Python as the environment

2. **Upload Files**:
   - `gradio_app.py` (main app file)
   - `requirements.txt`
   - `tessdata/` folder (Tesseract language data) - if using custom language data

3. **Install Tesseract**:
   - In your Space's `requirements.txt`, add:
     ```
     tesseract-ocr
     ```
   - Or use the system-installed Tesseract (usually available on Hugging Face Spaces)

4. **Configure Tesseract Path**:
   - In `gradio_app.py`, update the Tesseract path if needed:
     ```python
     pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Linux path
     ```

5. **Run the App**:
   - The app will automatically launch when you push to the Space

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install Tesseract OCR:
   - **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **Linux/Mac**: `sudo apt install tesseract-ocr` or `brew install tesseract`

3. Run the app:
   ```bash
   python gradio_app.py
   ```

## Usage

1. Upload an image of an ID card or passport
2. The app will process the image and extract:
   - Document type (TD1/ID Card or TD3/Passport)
   - Full name
   - Date of birth
   - Expiration date
   - Nationality
   - Gender
   - ID number

## Output Format

```json
{
  "document_type": "TD3 (Passport)",
  "extracted_data": {
    "full_name": {"value": "MUSTERMAN ERIKA", "confidence": 1.0},
    "date_of_birth": {"value": "640812", "confidence": 1.0},
    "expiration_date": {"value": "250812", "confidence": 1.0},
    "nationality": {"value": "D<<", "confidence": 1.0},
    "gender": {"value": "F", "confidence": 1.0},
    "id_number": {"value": "C01X00T47", "confidence": 1.0}
  },
  "raw_text": "Extracted OCR text..."
}
```

## Dependencies

- gradio: Web interface
- opencv-python-headless: Image processing
- pytesseract: OCR engine
- mrz: MRZ parsing library
- Pillow: Image handling
- numpy: Numerical operations

## Notes

- For best results, ensure the image is clear and well-lit
- MRZ parsing provides the most accurate results
- Regex parsing is used as fallback for non-standard documents</content>
<parameter name="filePath">c:\Users\azizg\Desktop\pcd\computer vision\id_card_extractor\GRADIO_README.md