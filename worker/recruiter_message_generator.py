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
You are a job-seeking professional writing a short outreach message to a recruiter or potential referrer.
Generate a concise message asking for any open opportunities or referrals.

Sender: {candidate_name}
Recipient: {recipient_name}
Role: {job_title}
Location: {location}
{tone_instructions}
Length: 3-4 sentences
""".strip()

    response = _router.route(prompt, task="recruiter_message")
    if response.startswith("["):
        # Static fallback when no provider is configured
        return (
            f"Hi {recipient_name},\n\n"
            f"My name is {candidate_name} and I'm very interested in the {job_title} role in {location}. "
            "I believe my experience aligns well and I'd love to connect or learn if any opportunities are available.\n\n"
            f"Best regards,\n{candidate_name}"
        )
    return response


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    demo_job = {"title": "Cloud Security Engineer", "location": "Berlin"}
    print(generate_message("Anna", demo_job, recipient_name="Hiring Team"))
