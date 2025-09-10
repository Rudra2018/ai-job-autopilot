import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests
from cryptography.fernet import Fernet
from pypdf import PdfReader


# ------------------------------------------------------------
# Agent implementations
# ------------------------------------------------------------

@dataclass
class ResumeUploaderAgent:
    """Parses a PDF resume and returns structured data."""

    def process(self, pdf_path: Path) -> Dict[str, Any]:
        reader = PdfReader(str(pdf_path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        name = lines[1] if len(lines) > 1 else ""
        email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)
        phone_match = re.search(r"\+?\d[\d\s-]{7,}\d", text)

        summary_lines = []
        for ln in lines[3:8]:  # grab a few lines after contact info
            if ln.lower().startswith("skills"):
                break
            summary_lines.append(ln)
        summary = " ".join(summary_lines)

        resume_json = {
            "name": name.title(),
            "contact_info": {
                "email": email_match.group(0) if email_match else None,
                "phone": phone_match.group(0) if phone_match else None,
            },
            "summary": summary,
            "education": [],
            "experience": [],
            "skills": [],
            "certifications": [],
            "languages": [],
        }
        return resume_json


@dataclass
class ProfileAnalyzerAgent:
    """Adds simple ATS keyword recommendations."""

    def process(self, resume_json: Dict[str, Any]) -> Dict[str, Any]:
        keywords = [
            "Cybersecurity",
            "Penetration Testing",
            "API Security",
            "DevSecOps",
            "GDPR",
        ]
        text = (resume_json.get("summary") or "") + " " + " ".join(resume_json.get("skills", []))
        missing = [kw for kw in keywords if kw.lower() not in text.lower()]
        optimized = dict(resume_json)
        optimized["keyword_recommendations"] = missing
        optimized["suggested_titles"] = ["Security Engineer", "Penetration Tester"]
        return optimized


@dataclass
class JobScraperAgent:
    """Fetches live job posts from a public job board API."""

    def process(self, optimized_profile_json: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            resp = requests.get("https://www.arbeitnow.com/api/job-board-api")
            data = resp.json().get("data", [])[:5]
        except Exception:
            data = []
        jobs: List[Dict[str, Any]] = []
        for item in data:
            jobs.append(
                {
                    "title": item.get("title"),
                    "company": item.get("company"),
                    "location": item.get("location"),
                    "salary_estimate": item.get("salary"),
                    "job_url": item.get("url"),
                    "apply_type": "External",
                }
            )
        return jobs


@dataclass
class AuthAgent:
    """Encrypts credentials and simulates authentication tokens."""

    def process(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        key = Fernet.generate_key()
        f = Fernet(key)
        encrypted = {k: f.encrypt(v.encode()).decode() for k, v in credentials.items() if v}
        return {"encrypted_credentials": encrypted, "fernet_key": key.decode()}


@dataclass
class ApplyAgent:
    """Simulates job applications."""

    def process(
        self,
        job_posts: List[Dict[str, Any]],
        optimized_profile_json: Dict[str, Any],
        resume_json: Dict[str, Any],
        auth_session_tokens: Dict[str, Any],
    ) -> Dict[str, Any]:
        report = {
            "total_jobs": len(job_posts),
            "applied_count": 0,
            "failed_count": len(job_posts),
            "success_rate": 0.0,
            "error_logs": ["Automation not implemented in demo"],
        }
        return report


@dataclass
class UIUXAgent:
    """Generates minimal React UI components."""

    def process(
        self,
        resume_json: Dict[str, Any],
        optimized_profile_json: Dict[str, Any],
        job_posts_json: List[Dict[str, Any]],
        application_report_json: Dict[str, Any],
    ) -> Dict[str, Any]:
        ui_dir = Path("ui/generated")
        ui_dir.mkdir(parents=True, exist_ok=True)
        component = f"""
import React from 'react';
export default function Dashboard() {{
  return (
    <div className='p-4'>
      <h1 className='text-2xl font-bold'>AI Job Autopilot</h1>
      <p>Applied Jobs: {application_report_json['applied_count']} / {application_report_json['total_jobs']}</p>
    </div>
  );
}}
"""
        (ui_dir / "Dashboard.jsx").write_text(component)
        return {"ui_path": str(ui_dir)}


# ------------------------------------------------------------
# Master orchestrator
# ------------------------------------------------------------

@dataclass
class MasterDashboardAgent:
    """Orchestrates the entire pipeline."""

    def run(self, resume_path: Path, credentials: Dict[str, str]) -> Dict[str, Any]:
        resume_agent = ResumeUploaderAgent()
        profile_agent = ProfileAnalyzerAgent()
        job_agent = JobScraperAgent()
        auth_agent = AuthAgent()
        apply_agent = ApplyAgent()
        ui_agent = UIUXAgent()

        resume_json = resume_agent.process(resume_path)
        optimized_profile_json = profile_agent.process(resume_json)
        job_posts_json = job_agent.process(optimized_profile_json)
        auth_session_tokens = auth_agent.process(credentials)
        application_report_json = apply_agent.process(
            job_posts_json, optimized_profile_json, resume_json, auth_session_tokens
        )
        ui_components = ui_agent.process(
            resume_json, optimized_profile_json, job_posts_json, application_report_json
        )

        final_dashboard = {
            "resume_json": resume_json,
            "optimized_profile_json": optimized_profile_json,
            "job_posts_json": job_posts_json,
            "application_report_json": application_report_json,
            "ui_components": ui_components,
            "metadata": {
                "pipeline_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "logs": [],
                "errors": [],
            },
        }
        return final_dashboard


def main() -> None:
    resume_path = Path("config/resume.pdf")
    credentials = {
        "linkedin_email": "demo@example.com",
        "linkedin_password": "dummy",
    }
    agent = MasterDashboardAgent()
    dashboard = agent.run(resume_path, credentials)
    Path("final_dashboard.json").write_text(json.dumps(dashboard, indent=2))
    print("final_dashboard.json generated")


if __name__ == "__main__":
    main()
