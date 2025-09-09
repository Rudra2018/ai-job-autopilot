"""Tests for the MultiAIResumeParser experience calculation."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.ml.multi_ai_resume_parser import MultiAIResumeParser, calculate_total_experience


def test_calculate_total_experience_and_merge():
    parser = MultiAIResumeParser()
    # Prepare mock results with experience entries but without years_of_experience
    results = [
        (
            "test",
            {
                "experience": [
                    {"duration_months": 12},
                    {"duration_months": 24},
                ],
                "career_analysis": {},
            },
        )
    ]

    merged = parser._merge_ai_results(results)
    assert merged["career_analysis"]["years_of_experience"] == 3.0


def test_calculate_total_experience_helper():
    experience = [{"duration_months": 6}, {"duration_months": 18}]
    assert calculate_total_experience(experience) == 2.0
