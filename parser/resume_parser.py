"""Resume parsing utility using multi-AI analysis.

This module extracts text from a PDF resume, parses it using the
``MultiAIResumeParser`` which can leverage OpenAI, Gemini and other
providers, and ensures the total years of experience are calculated.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

# Ensure repository root is on ``sys.path`` for imports when run as a script
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.core.pdf_text_extractor import EnhancedPDFExtractor
from src.ml.multi_ai_resume_parser import (
    parse_resume_with_multi_ai,
    calculate_total_experience,
)


def parse_resume(resume_path: str) -> Dict[str, Any]:
    """Parse a resume PDF and return structured data.

    Parameters
    ----------
    resume_path: str
        Path to the resume PDF file.
    """

    if not os.path.exists(resume_path):
        raise FileNotFoundError(f"Resume not found: {resume_path}")

    extractor = EnhancedPDFExtractor()
    extraction = extractor.extract_text(resume_path)

    result = parse_resume_with_multi_ai(extraction.text)

    # Ensure years of experience is always present
    career = result.setdefault("career_analysis", {})
    if not career.get("years_of_experience") and result.get("experience"):
        career["years_of_experience"] = calculate_total_experience(
            result["experience"]
        )

    return result


if __name__ == "__main__":
    data = parse_resume("config/resume.pdf")
    print("Extracted Resume Data:")
    for key, value in data.items():
        print(f"{key}: {value}")

