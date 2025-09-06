
import os
from vertexai.preview.generative_models import GenerativeModel, ChatSession

def gemini_fallback_respond(prompt: str) -> str:
    try:
        model = GenerativeModel("gemini-1.5-pro-preview-0409")
        chat = model.start_chat()
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        return f"[Gemini Fallback Error] {e}"
