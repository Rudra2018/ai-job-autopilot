"""Routing layer for multiple language models.

The router chooses an available provider based on the requested task.  Each
provider call falls back to a deterministic string so unit tests do not require
network access or API keys.
"""

from __future__ import annotations

import os
from typing import Dict, List

try:  # Optional dependencies
    import openai  # type: ignore
except Exception:  # pragma: no cover - library may not be installed
    openai = None

try:  # pragma: no cover - optional
    import google.generativeai as genai  # type: ignore
except Exception:  # pragma: no cover - library may not be installed
    genai = None

try:  # pragma: no cover - optional
    import anthropic  # type: ignore
except Exception:  # pragma: no cover - library may not be installed
    anthropic = None


class LLMRouter:
    """Simple task based router for GPT-4o, Gemini 1.5 Pro and Claude 3 Sonnet."""

    TASK_PREFERENCE: Dict[str, List[str]] = {
        "resume": ["openai", "claude", "gemini"],
        "recruiter_message": ["gemini", "openai", "claude"],
        "feedback": ["claude", "openai", "gemini"],
    }

    def __init__(self) -> None:
        self.available = {
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "gemini": bool(os.getenv("GOOGLE_API_KEY")),
            "claude": bool(os.getenv("ANTHROPIC_API_KEY")),
        }
        if openai and self.available["openai"]:
            openai.api_key = os.getenv("OPENAI_API_KEY")
        if genai and self.available["gemini"]:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        if anthropic and self.available["claude"]:
            self._anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        else:
            self._anthropic_client = None

    # Public API -----------------------------------------------------
    def route(self, prompt: str, task: str) -> str:
        for provider in self.TASK_PREFERENCE.get(task, []):
            if self.available.get(provider):
                return getattr(self, f"_call_{provider}")(prompt)
        return f"[no provider available] {prompt}"

    # Provider implementations --------------------------------------
    def _call_openai(self, prompt: str) -> str:
        if not (openai and self.available["openai"]):
            return f"[openai mock] {prompt}"
        try:  # pragma: no cover - network call
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message["content"].strip()
        except Exception:  # pragma: no cover - graceful fallback
            return f"[openai mock] {prompt}"

    def _call_gemini(self, prompt: str) -> str:
        if not (genai and self.available["gemini"]):
            return f"[gemini mock] {prompt}"
        try:  # pragma: no cover - network call
            model = genai.GenerativeModel("gemini-1.5-pro-latest")
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception:  # pragma: no cover - graceful fallback
            return f"[gemini mock] {prompt}"

    def _call_claude(self, prompt: str) -> str:
        if not (self._anthropic_client and self.available["claude"]):
            return f"[claude mock] {prompt}"
        try:  # pragma: no cover - network call
            response = self._anthropic_client.messages.create(
                model="claude-3-sonnet-20240229", max_tokens=512, messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception:  # pragma: no cover - graceful fallback
            return f"[claude mock] {prompt}"


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    router = LLMRouter()
    print(router.route("Hello", "recruiter_message"))
