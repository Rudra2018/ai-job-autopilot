import sys
import types
from unittest.mock import MagicMock

from worker.playwright_apply import (
    set_platform_credentials,
    _get_platform_credentials,
    upload_and_parse_resume,
    smart_apply,
)


def test_set_and_get_credentials():
    set_platform_credentials("linkedin", "user@example.com", "pass")
    assert _get_platform_credentials("linkedin") == ("user@example.com", "pass")


def test_upload_and_parse_resume_calls_parser(tmp_path, monkeypatch):
    fake_resume = tmp_path / "resume.pdf"
    fake_resume.write_text("dummy")
    fake_module = types.SimpleNamespace()
    mock_parse = MagicMock(return_value={"text": "resume"})
    fake_module.parse_resume = mock_parse
    monkeypatch.setitem(sys.modules, "parser.resume_parser", fake_module)
    data = upload_and_parse_resume(str(fake_resume))
    assert data == {"text": "resume"}
    mock_parse.assert_called_once_with(str(fake_resume))


def test_smart_apply_uses_scraper_and_apply(monkeypatch):
    jobs = [{"url": "https://www.linkedin.com/jobs/view/123", "title": "E", "company": "C"}]
    monkeypatch.setattr("worker.playwright_apply.scrape_jobs_live", lambda *a, **k: jobs)
    called = []

    def fake_apply(job, resume_path):
        called.append((job, resume_path))

    monkeypatch.setattr("worker.playwright_apply.auto_detect_and_apply", fake_apply)
    monkeypatch.setattr("worker.playwright_apply.upload_and_parse_resume", lambda *_: {})
    smart_apply(resume_path="resume.pdf")
    assert called and called[0][0] == jobs[0]
