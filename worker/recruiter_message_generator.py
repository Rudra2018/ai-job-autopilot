"""Utilities for generating recruiter outreach messages.

The original function accepted ``(job_title, location, recipient_name)`` which
made it awkward to integrate with the rest of the codebase.  The auto-apply
pipeline provides a ``job`` dictionary and the candidate's name, so the helper
now follows that convention instead.  The previous behaviour is preserved via
the ``recipient_name`` argument which defaults to "there".
"""

import os
from typing import Dict

try:  # pragma: no cover - optional dependency
    from vertexai.language_models import ChatModel
    from dotenv import load_dotenv
    load_dotenv()
    USE_GEMINI = True
except Exception:  # vertexai not installed or misconfigured
    USE_GEMINI = False


def generate_message(candidate_name: str,
                     job: Dict,
                     recipient_name: str = "there") -> str:
    """Return a short recruiter outreach message.

    Parameters
    ----------
    candidate_name: str
        Name of the person sending the message.
    job: Dict
        Dictionary containing at least ``title`` and ``location`` keys.
    recipient_name: str
        Optional recipient name used in the greeting.
    """

    job_title = job.get("title", "the role")
    location = job.get("location", "")

    if USE_GEMINI:
        try:  # pragma: no cover - network call
            chat_model = ChatModel.from_pretrained("chat-bison")
            chat = chat_model.start_chat()
            prompt = f"""
You are a job-seeking professional writing a short outreach message to a recruiter or potential referrer.
Generate a professional yet warm message asking for any open opportunities or referrals.

Sender: {candidate_name}
Recipient: {recipient_name}
Role: {job_title}
Location: {location}
Language: English
Tone: Polite, Enthusiastic
Length: 3–4 sentences
            """
            response = chat.send_message(prompt)
            return response.text.strip()
        except Exception as e:  # pragma: no cover - safety net
            print("[⚠️] Gemini fallback error:", e)

    # Default static fallback
    return (
        f"Hi {recipient_name},\n\n"
        f"My name is {candidate_name} and I'm very interested in the {job_title} role in {location}. "
        "I believe my experience aligns well and I'd love to connect or learn if any opportunities are available.\n\n"
        f"Best regards,\n{candidate_name}"
    )


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    demo_job = {"title": "Cloud Security Engineer", "location": "Berlin"}
    print(generate_message("Anna", demo_job, recipient_name="Hiring Team"))

