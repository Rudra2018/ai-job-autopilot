from dotenv import load_dotenv
import os

load_dotenv()

from extensions.llm_fallback_ollama import fallback_to_ollama
from extensions.llm_vertex import call_vertex_flash_if_available


def ask_question(question: str) -> str:
    """Asks a mock interview question and gets AI feedback."""
    try:
        # Try with Vertex AI
        prompt = f"""You are a senior interviewer.
Please provide a high-quality answer to the following question in cybersecurity context:

Q: {question}
"""
        return call_vertex_flash_if_available(prompt)
    except Exception as e:
        print("[⚠️] Vertex AI error, using Ollama fallback:", e)
        return fallback_to_ollama(f"Q: {question}\nA:")

