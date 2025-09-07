import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from worker import application_logger as al


def test_log_and_read(tmp_path, monkeypatch):
    log_path = tmp_path / "app.jsonl"
    monkeypatch.setattr(al, "LOG_PATH", log_path)
    al.log_application({"title": "T", "company": "C"}, "applied", recruiter_msg="hello")
    entries = list(al.read_application_log())
    assert len(entries) == 1
    entry = entries[0]
    assert entry["title"] == "T"
    assert entry["company"] == "C"
    assert entry["status"] == "applied"
    assert entry["recruiter_msg"] == "hello"
