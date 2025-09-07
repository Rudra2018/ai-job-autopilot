"""Utilities for generating recruiter outreach messages with tone presets."""

from __future__ import annotations

from typing import Dict

from .llm_router import LLMRouter

TONE_PRESETS = {
    "polite": "Tone: Polite and enthusiastic.",
    "formal": "Tone: Formal and professional.",
    "casual": "Tone: Casual and friendly.",
}

_router = LLMRouter()


def generate_message(candidate_name: str,
                     job: Dict,
                     recipient_name: str = "there",
                     tone: str = "polite") -> str:
    """Return a recruiter outreach message using the configured LLMs.

    Parameters
    ----------
    candidate_name: str
        Name of the person sending the message.
    job: Dict
        Dictionary containing at least ``title`` and ``location`` keys.
    recipient_name: str
        Optional recipient name used in the greeting.
    tone: str
        One of ``polite`` (default), ``formal`` or ``casual``.
    """

    job_title = job.get("title", "the role")
    location = job.get("location", "")
    tone_instructions = TONE_PRESETS.get(tone, TONE_PRESETS["polite"])

    prompt = f"""
You are Ankit Thakur, an experienced cybersecurity professional writing a personalized outreach message to a recruiter.
Generate a professional message highlighting relevant experience and skills.

Professional Background:
- SDET II (Cyber Security) at Halodoc Technologies LLP
- Senior Security Consultant at Prescient Security LLC 
- Expertise: Penetration Testing, API Security, Cloud Security, GDPR Compliance
- Certifications: AWS Security Specialty, CompTIA Security+, AWS SysOps Administrator
- Achievements: Reduced security risks by 25%, improved data protection by 30%
- Notable: Hall of Fame recognition from Google, Facebook, Yahoo, U.S. Department of Defense

Sender: {candidate_name}
Recipient: {recipient_name}
Role: {job_title}
Location: {location}
{tone_instructions}
Length: Professional message with specific skills mentioned
""".strip()

    response = _router.route(prompt, task="recruiter_message")
    if response.startswith("["):
        # Static fallback when no provider is configured
        return (
            f"Hi {recipient_name},\n\n"
            f"My name is Ankit Thakur and I'm very interested in the {job_title} role in {location}. "
            "With my extensive background in penetration testing, API security, and cloud security at companies like Halodoc Technologies and Prescient Security LLC, "
            "I believe I would be a strong fit for your team. My expertise includes penetration testing, vulnerability assessment, GDPR compliance, and AWS security certifications. "
            "I have successfully reduced security risks by 25% for clients and improved data protection by 30%.\n\n"
            "I'd love to connect and discuss how my skills can contribute to your security initiatives.\n\n"
            f"Best regards,\nAnkit Thakur\nat87.at17@gmail.com | +91 8717934430"
        )
    return response


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    demo_job = {"title": "Cloud Security Engineer", "location": "Berlin"}
    print(generate_message("Anna", demo_job, recipient_name="Hiring Team"))
