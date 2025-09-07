from worker import llm_router


def test_router_prefers_openai(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(llm_router, "openai", None)
    router = llm_router.LLMRouter()
    out = router.route("hello", "resume")
    assert out.startswith("[openai"), out


def test_router_no_provider(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    router = llm_router.LLMRouter()
    out = router.route("hi", "resume")
    assert out.startswith("[no provider"), out
