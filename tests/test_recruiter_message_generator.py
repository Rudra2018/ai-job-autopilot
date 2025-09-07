from worker import recruiter_message_generator as rmg


def test_tone_in_prompt(monkeypatch):
    captured = {}

    class DummyRouter:
        def route(self, prompt: str, task: str) -> str:
            captured['prompt'] = prompt
            return "[mock]"

    monkeypatch.setattr(rmg, '_router', DummyRouter())
    job = {"title": "Developer", "location": "Berlin"}
    rmg.generate_message("Alice", job, tone="formal")
    assert "Formal and professional" in captured['prompt']


def test_fallback_message(monkeypatch):
    class DummyRouter:
        def route(self, prompt: str, task: str) -> str:
            return "[mock]"

    monkeypatch.setattr(rmg, '_router', DummyRouter())
    job = {"title": "Developer", "location": "Berlin"}
    msg = rmg.generate_message("Alice", job, recipient_name="Hiring Team")
    assert "Hiring Team" in msg
    assert "Developer" in msg
