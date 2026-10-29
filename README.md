# 🪪 DocuExtract Core: Autonomous Edge ID & Passport Intelligence Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8.svg?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![Tesseract OCR](https://img.shields.io/badge/Tesseract--OCR-v5.5-orange.svg?style=for-the-badge&logo=google&logoColor=white)](https://github.com/tesseract-ocr/tesseract)
[![ICAO Doc 9303](https://img.shields.io/badge/ICAO-Doc_9303_Compliant-success.svg?style=for-the-badge)](https://www.icao.int/Security/FAL/PKD/Pages/ICAO-Doc-9303.aspx)
[![Air-Gapped Offline](https://img.shields.io/badge/Security-100%25_Offline_Air--Gapped-red.svg?style=for-the-badge)](#security--data-privacy)
[![Gradio UI](https://img.shields.io/badge/Interface-Gradio_Interactive_GUI-FD6F22.svg?style=for-the-badge&logo=gradio&logoColor=white)](https://gradio.app/)

> **High-precision, air-gapped optical credential extraction and verification engine designed for zero-trust, edge-deployed identification workflows.**

---

## 📌 Executive Summary

**DocuExtract Core** is an enterprise-grade document parsing pipeline designed to ingest, normalize, and extract structured identities from government-issued identity documents (national identity cards, biometric passports, travel credentials). 

Unlike cloud-dependent API extractors that expose sensitive Personally Identifiable Information (PII) over external networks, **DocuExtract Core runs 100% locally on-device**. It guarantees sub-second processing, zero cloud leakage, full compliance with strict data protection mandates (GDPR, HIPAA), and seamless offline survivability.

---

## 🏛️ System Architecture & Processing Pipeline

The engine utilizes a deterministic 5-stage computer vision and parsing pipeline:

```
┌─────────────────┐
│ Raw Document    │
│ Image Ingestion │
└────────┬────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ 1. Computer Vision & Normalization Preprocessing       │
│    • Grayscale conversion & Gaussian smoothing         │
│    • Hough Line Transform angular skew estimation       │
│    • Affine rotation correction & deskewing            │
│    • Adaptive Gaussian binary thresholding             │
└────────┬───────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ 2. High-Fidelity OCR Engine (Tesseract 5.5)            │
│    • Modular language packs (ENG, FRA, ARA)            │
│    • Fully configurable Page Segmentation Modes (PSM)  │
└────────┬───────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ 3. Dual-Track Parsing & Validation Core                │
│    ├── Primary: ICAO Doc 9303 MRZ Engine               │
│    │   • TD1 (ID Cards, 3 lines × 30 chars)            │
│    │   • TD3 (Passports, 2 lines × 44 chars)           │
│    │   • 7-3-1 weight-algorithm checksum verification  │
│    └── Fallback: Heuristic RegEx Semantic Parser       │
│        • Contextual pattern matching for non-MRZ docs  │
│        • Fuzzy date normalization & confidence scoring │
└────────┬───────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ 4. Output Presentation & Interface Layer               │
│    • Interactive Local Web GUI (Gradio)                │
│    • High-Readability Formatted Markdown Tables        │
│    • Machine-Readable Structured JSON                  │
└────────────────────────────────────────────────────────┘
```

---

## 🌟 Key Capabilities

### 🛡️ Air-Gapped Zero-Trust Security
- **Strictly Offline**: Operates without an active internet connection. No biometric data, document images, or extracted names ever leave the local environment.
- **Stateless Execution**: Memory buffers are freed immediately post-inference; zero persistent image caching unless explicitly archived.

### 📐 Adaptive Computer Vision Normalization
- Automatically corrects tilted or perspective-skewed captures using **probabilistic Hough line detection** and **affine matrix transformation**.
- Removes high-frequency noise and enhances character contrast against holographic security overlays using adaptive Gaussian thresholding.

### 🪪 ICAO 9303 Cryptographic & Checksum Verification
- Comprehensive support for standard Machine-Readable Zones:
  - **TD1 Format**: 3-line ID card specifications.
  - **TD3 Format**: 2-line Passport standard specifications.
- Validates country codes, document numbers, dates of birth, expiration dates, and composite checksums according to the official **ICAO 7-3-1 weighting algorithm**.

### 🧩 Resilient Dual-Parser Fallback
- If MRZ zones are obscured or damaged, the engine automatically defers to an internal **Named Entity & Regular Expression Parser** to capture full names, birth dates, and document identifiers directly from visual inspection text.

---

## 💻 Quick Start & Offline Operation

### 1. Prerequisites

Ensure **Tesseract OCR (v5.0+)** is installed on your workstation:
- **Windows**: [UB-Mannheim Tesseract Installer](https://github.com/UB-Mannheim/tesseract/wiki) (Installs by default to `C:\Program Files\Tesseract-OCR`)
- **Linux**: `sudo apt install tesseract-ocr`
- **macOS**: `brew install tesseract`

### 2. Installation

Clone the repository and set up your Python environment:

```bash
git clone https://github.com/<your-username>/id_card_extractor.git
cd id_card_extractor

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate   # On Windows
source venv/bin/activate  # On Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### 3. Launching the Local Interface

#### 🚀 Method A: One-Click Desktop Launcher (Windows)
Simply double-click the included batch launcher:
```text
run_offline.bat
```
This script configures UTF-8 encoding, binds the environment offline, and automatically opens your default web browser to the local interface.

#### 🖥️ Method B: Terminal Execution
```bash
python gradio_app.py
```
Then navigate to `http://127.0.0.1:7860` in any web browser.

---

## 📊 Output Schema

### Formatted Markdown Output (Interactive UI)
When an identity document is uploaded, the engine renders an intuitive tabular summary:

| Field | Value | Confidence |
| :--- | :--- | :---: |
| **Document Type** | `TD3 (Passport)` | `1.00` |
| **Full Name** | `DOE JOHN` | `1.00` |
| **Date Of Birth** | `1980-01-01` | `1.00` |
| **Expiration Date** | `2027-01-01` | `1.00` |
| **Nationality** | `UTO` | `1.00` |
| **Gender** | `M` | `1.00` |
| **Id Number** | `123456789` | `1.00` |

### Machine-Readable JSON (API / Headless Mode)
```json
{
  "document_type": "TD3 (Passport)",
  "extracted_data": {
    "full_name": { "value": "DOE JOHN", "confidence": 1.0 },
    "date_of_birth": { "value": "800101", "confidence": 1.0 },
    "expiration_date": { "value": "270101", "confidence": 1.0 },
    "nationality": { "value": "UTO", "confidence": 1.0 },
    "gender": { "value": "M", "confidence": 1.0 },
    "id_number": { "value": "123456789", "confidence": 1.0 }
  },
  "raw_text": "UTOPIA\nPASSPORT\nType Code Passport No\nP UTO 123456789..."
}
```

---

## 📁 Repository Structure

```text
├── gradio_app.py         # Main entry point with Gradio UI & processing core
├── run_offline.bat       # Windows 1-click zero-dependency offline launcher
├── sample_passport.jpg   # Sample biometric test document for offline validation
├── requirements.txt      # Python dependencies manifest
├── tessdata/             # Local trained language models (eng, fra, ara, osd)
└── src/                  # Modular backend components
    ├── ocr_engine.py     # Tesseract integration & preprocessing filters
    ├── parsers.py        # TD1/TD3 MRZ decoders & RegEx semantic extractors
    └── utils.py          # Image transformation & geometry utilities
```

---

## 🔒 Security & Privacy by Design

- **Air-Gap Validated**: Never makes outbound HTTP/HTTPS telemetry requests.
- **Local Data Retention**: Uploaded documents are kept in volatile memory and never transmitted off the host device.
- **Regulatory Ready**: Fully aligned with requirements for GDPR Article 9 (Special Categories of Data) and biometric processing policies.

---

## 📜 License & Compliance

Distributed under the **MIT License**. Compliant with **ICAO Document 9303 specifications** for Machine Readable Travel Documents (MRTD).
