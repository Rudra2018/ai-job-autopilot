# 🤖 AI Job Autopilot

AI Job Autopilot is an end‑to‑end job search agent. It scrapes listings, matches them to your resume with [JobBERT‑v3](https://huggingface.co/TechWolf/JobBERT-v3), generates recruiter outreach and fills application forms via Playwright automation. The system learns from feedback and supports multiple large language models through a routing layer.

---

## ✨ Features

- 🧠 **AI Matching** – Resume ↔ job description matching with JobBERT‑v3
- 🕵️ **Smart Scraper** – LinkedIn, Xing, Indeed, Glassdoor, Monster, RemoteOK, AngelList/Wellfound
- 💌 **Recruiter Messaging** – Tone presets routed through GPT‑4o, Gemini 1.5 Pro or Claude 3 Sonnet
- 🔁 **Feedback Learning** – Uses rejection emails to refine ranking and resumes
- 🔐 **Form Automation** – Playwright autofill with login & CAPTCHA handling
- 📊 **Dashboard** – Real‑time application tracking and insights

---

## 🚀 Quickstart

1. **Clone and set up environment**
   ```bash
   git clone https://github.com/Rudra2018/ai-job-autopilot.git
   cd ai-job-autopilot
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Download JobBERT model**
   ```python
   from sentence_transformers import SentenceTransformer
   SentenceTransformer("TechWolf/JobBERT-v3").save("ml_models/jobbert_v3")
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # populate API keys and credentials
   ```

4. **Run the autopilot**
   ```bash
   python launch_autopilot.py
   ```

### Additional tools

- Batch resume testing: `python tests/batch_resume_runner.py`
- OCR screenshot matching: `python extensions/ocr_job_parser.py`
- Feedback loop & retraining: `python extensions/resume_retrain.py`
- Dashboard (Vite):
  ```bash
  cd ui
  npm install
  npm run dev
  ```

---

## 🔐 Supported Job Platforms

| Platform            | Scraping | Form Fill | Notes                        |
| ------------------- | :------: | :-------: | ---------------------------- |
| LinkedIn            |    ✅    |    ✅     | Easy Apply (last 24h) + CAPTCHA |
| Xing                |    ✅    |    ✅     | Session auto‑login           |
| Indeed              |    ✅    |    ❌     | Listing scrape               |
| Glassdoor           |    ✅    |    ❌     | Listing scrape               |
| Monster             |    ✅    |    ❌     | Listing scrape               |
| RemoteOK            |    ✅    |    ❌     | Remote‑only roles            |
| AngelList/Wellfound |    ✅    |    ❌     | Startup jobs                 |
| Greenhouse          |    ✅    |    ✅     | Autofill JSON forms          |
| Lever               |    ✅    |    ✅     | Multi‑step support           |

---

## 🧪 Tests

Run the full test suite:

```bash
pytest -q
```

---

## 📜 License

MIT — free to use, modify and deploy.

