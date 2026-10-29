import streamlit as st
import cv2
import numpy as np
import json
import os
import tempfile
from src.preprocessor import correct_skew, cv2_to_pil
from src.ocr_engine import extract_text_tesseract
from src.parser import CombinedParser

# Set Tesseract Language Path to local directory if it exists
local_tessdata = os.path.join(os.path.dirname(__file__), 'tessdata')
if os.path.exists(local_tessdata):
    os.environ['TESSDATA_PREFIX'] = local_tessdata


# Page Configuration
st.set_page_config(
    page_title="ID Card Extractor",
    page_icon="🆔",
    layout="wide"
)

# Custom CSS for better look
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stJSON {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🆔 ID Card & Passport Data Extractor")
st.markdown("Upload an image of an ID card (TD1) or Passport (TD3) to extract structured data automatically.")

# File Uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Use columns for side-by-side view
    col1, col2 = st.columns(2)
    
    # Save uploaded file to a temporary location for opencv processing if needed
    # However, we can also decode directly from memory
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1) # BGR
    
    if image is None:
        st.error("Error: Could not load image.")
    else:
        with col1:
            st.subheader("Original Image")
            # Convert BGR to RGB for display
            st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), use_container_width=True)
            
        with col2:
            st.subheader("Extraction Results")
            status_container = st.empty()
            
            try:
                with st.spinner("Processing image..."):
                    # 1. Deskew
                    deskewed = correct_skew(image)
                    
                    # 2. OCR
                    pil_image = cv2_to_pil(deskewed)
                    
                    # Language selection
                    langs = ["eng", "ara", "fra", "deu", "spa"]
                    selected_lang = st.selectbox("Select OCR Language", langs, index=0)
                    
                    # Custom config
                    custom_config = r'--oem 3 --psm 3' 
                    
                    raw_text = extract_text_tesseract(pil_image, config=custom_config, lang=selected_lang) 

                    
                    # 3. Parse
                    data_parser = CombinedParser()
                    result = data_parser.parse(raw_text)
                    
                    st.success("Extraction Complete!")
                    st.json(result)

                    with st.expander("Debug Information"):
                        st.subheader("Raw OCR Text")
                        st.text(raw_text)
                        st.subheader("Deskewed Image")
                        st.image(cv2_to_pil(deskewed), use_container_width=True)

                    
            except Exception as e:
                st.error(f"An error occurred: {e}")
                # Optional: Show detailed error in expander
                with st.expander("Error Details"):
                    st.write(str(e))
