# extensions/ocr_job_parser.py

import pytesseract
from PIL import Image

def extract_text_from_job_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return f"OCR Failed: {e}"

def parse_job_details(ocr_text):
    lines = ocr_text.splitlines()
    title = next((l for l in lines if "engineer" in l.lower()), "Unknown")
    location = next((l for l in lines if "remote" in l.lower() or "berlin" in l.lower()), "Unknown")
    return {
        "title": title.strip(),
        "company": "From Screenshot",
        "location": location.strip(),
        "description": ocr_text,
        "link": "screenshot_job"
    }

