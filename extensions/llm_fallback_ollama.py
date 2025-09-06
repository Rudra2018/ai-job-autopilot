import os

def fallback_to_ollama(prompt: str) -> str:
    """
    Calls Ollama's local LLM (e.g., llama3) with a user prompt.
    """
    try:
        import ollama
        response = ollama.chat(
            model=os.getenv("OLLAMA_MODEL", "llama3"),
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]
    except Exception as e:
        return f"[❌ Ollama Fallback Failed] {str(e)}"

