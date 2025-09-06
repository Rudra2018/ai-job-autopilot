
import pytesseract
from PIL import Image
import re

def extract_text_from_job_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return f"[OCR Error] {e}"

def parse_job_details(text):
    title_match = re.search(r"(Security Engineer|Cloud Security Engineer|Penetration Tester)", text, re.IGNORECASE)
    location_match = re.search(r"(Berlin|Munich|Remote)", text, re.IGNORECASE)
    return {
        "title": title_match.group(0) if title_match else "Unknown Title",
        "location": location_match.group(0) if location_match else "Unknown Location",
        "description": text.strip()
    }
