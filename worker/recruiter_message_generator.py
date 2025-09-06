import os

try:
    from vertexai.language_models import ChatModel, InputOutputTextPair
    from dotenv import load_dotenv
    load_dotenv()
    USE_GEMINI = True
except ImportError:
    USE_GEMINI = False

def generate_message(job_title: str, location: str, recipient_name: str = "there") -> str:
    if USE_GEMINI:
        try:
            chat_model = ChatModel.from_pretrained("chat-bison")
            chat = chat_model.start_chat()
            prompt = f"""
You are a job-seeking professional writing a short outreach message to a recruiter or potential referrer.
Generate a professional yet warm message asking for any open opportunities or referrals.

Recipient: {recipient_name}
Role: {job_title}
Location: {location}
Language: English
Tone: Polite, Enthusiastic
Length: 3–4 sentences
            """
            response = chat.send_message(prompt)
            return response.text.strip()
        except Exception as e:
            print("[⚠️] Gemini fallback error:", e)

    # Default static fallback
    return f"""Hi {recipient_name},

I'm reaching out because I’m very interested in the {job_title} role in {location}. I believe my experience aligns well, and I’d love to connect or learn if any opportunities are available.

Warm regards,
[Your Name]
"""

# Test (can be removed)
if __name__ == "__main__":
    print(generate_message("Cloud Security Engineer", "Berlin", "Anna"))

