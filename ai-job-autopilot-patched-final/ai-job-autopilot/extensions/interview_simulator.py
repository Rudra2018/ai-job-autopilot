from dotenv import load_dotenv
load_dotenv()
import os

from vertexai.generative_models import GenerativeModel

def simulate_interview(role, company, resume_text):
    model = GenerativeModel("gemini-1.5-flash-latest")
    prompt = f"""
You are an expert technical interviewer. Simulate a realistic interview for the following role:
- Role: {role}
- Company: {company}
- Candidate Resume: {resume_text}

Return 5 tough questions and sample high-scoring answers.
"""
    response = model.generate_content(prompt)
    return response.text.strip()
