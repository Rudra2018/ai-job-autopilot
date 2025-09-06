# ✅ This file fixes your missing import: `from extensions.llm_vertex import call_vertex_flash_if_available`
# 📄 Save this as: extensions/llm_vertex.py

import os

try:
    from vertexai.generative_models import GenerativeModel
except ImportError:
    GenerativeModel = None


def call_vertex_flash_if_available(prompt: str, model_name: str = "gemini-2.5-pro") -> str:
    """
    Calls Vertex AI Gemini model to generate content from prompt.
    Falls back to static message if unavailable.
    """
    if GenerativeModel is None:
        return "[⚠️ Vertex AI SDK not installed. Please install vertexai>=1.0.0]"

    try:
        model = GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[⚠️ Vertex AI failed: {str(e)}]"


# 🔧 Optional CLI test:
if __name__ == "__main__":
    prompt = "Give me 3 reasons why cybersecurity is critical in cloud environments."
    print(call_vertex_flash_if_available(prompt))

