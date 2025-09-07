from dotenv import load_dotenv
load_dotenv()
import os
from extensions.llm_fallback_ollama import fallback_to_ollama

def generate_recruiter_reply(context, job_title=""):
    prompt = f"""
You are a helpful job applicant assistant.
Based on the following message from a recruiter, write a professional, concise reply showing interest in the {job_title} role.

Recruiter message:
{context}
"""
    return fallback_to_ollama(prompt)
