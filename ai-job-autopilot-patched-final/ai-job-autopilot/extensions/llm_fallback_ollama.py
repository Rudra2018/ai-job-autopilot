from dotenv import load_dotenvnload_dotenv()nimport osn
def fallback_to_ollama(prompt):
    try:
        import ollama
        response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"]
    except Exception as e:
        return f"Ollama fallback failed: {e}"
